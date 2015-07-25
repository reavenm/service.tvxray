import xbmc
import xbmcaddon
import xbmcgui

from bs4 import BeautifulSoup
from urllib2 import HTTPError
from urllib2 import urlopen


__addon__ = xbmcaddon.Addon("service.tvxray")
__addonversion__ = __addon__.getAddonInfo('version')
__addonid__ = __addon__.getAddonInfo('id')
__addonname__ = __addon__.getAddonInfo('name')
__settings__ = __addon__
__language__ = __settings__.getLocalizedString


def notification(text):
    text = text.encode('utf-8')
    icon = __settings__.getAddonInfo("icon")
    smallicon = icon.encode("utf-8")
    if __settings__.getSetting("notification") == "true":
        xbmc.executebuiltin('Notification(TV X-ray,'+text+',3000,' + smallicon + ')')


def log(msg):
    LOGDEBUG = 2
    message = '%s: %s' % (__settings__.getAddonInfo("name"), msg)
    if __settings__.getSetting("debug") == "true":
            level = LOGDEBUG
            xbmc.log(message, level)


class Main:

    def __init__(self):
        self.Player = tvxrayPlayer()
        while True:
            if xbmc.Monitor().waitForAbort(10):
                break


class tvxrayPlayer(xbmc.Player):

    def __init__(self):
        xbmc.Player.__init__(self)

    def onPlayBackStarted(self):
        xbmc.sleep(1000)
        mediaTitle = xbmc.getInfoLabel('VideoPlayer.Title')
        imdbID = xbmc.getInfoLabel('VideoPlayer.IMDBNumber')
        log('Playback started for " %s " with id: %s' % (mediaTitle, imdbID))
        myfacts = showFacts(__settings__.getSetting("enable_facts"), __settings__.getSetting("facts_spoilers"))

        if not myfacts:
            log('No facts found for title: ' + mediaTitle)
        else:
            log('Just to test show me the facts: \n%s' % myfacts)

    def onPlayBackEnded(self):
        log('playback stop/end')

    def onPlayBackStopped(self):
        self.onPlayBackEnded()


def mediaLink(xType):
    # add logic to request imdbID if kodiDB doesnt have it
    imdbID = xbmc.getInfoLabel('VideoPlayer.IMDBNumber')
    link = 'http://m.imdb.com/title/' + imdbID + '/' + xType

    if not imdbID:
        log('error empty imdb#')
        return None
    else:
        return link


def myData(url):
    try:
        html = urlopen(url)
    except HTTPError as e:
        log(e)
        return None

    try:
        data = BeautifulSoup(html.read(), 'html.parser')
    except AttributeError as e:
        log('%s, found while trying to parse html' % e)
        return None
    return data


def showFacts(enable, showSpoilers):
    if enable:
        try:
            all_data = myData(mediaLink("trivia")).find_all("div", {"class": "col-xs-12 drop-panel-content"})
            if showSpoilers:
                sp_facts = []
                for data in all_data:
                    sp_facts.append(data.text)
                return sp_facts

            else:
                un_facts = []
                for data in all_data:
                    if data.find_parent("section") is None:
                        un_facts.append(data)
                return un_facts

        except AttributeError as e:
            log('%s, found while trying to find facts' % e)
            return None


def showGoofs(enable, showSpoilers):
    if enable:
        try:
            if showSpoilers:
                all_data = myData(mediaLink("goofs")).find_all("section")
                for tag in all_data:
                    p_tag = tag.find_all("p")
                    for sp_goofs in p_tag:
                        print sp_goofs.text  # get_text(strip=True)

            else:
                all_data = myData(mediaLink("goofs")).find_all("section", {"class": "unspoilt goofs"})
                for tag in all_data:
                    p_tag = tag.find_all("p")
                    for un_goofs in p_tag:
                        print un_goofs.text  # get_text(strip=True)

        except AttributeError as e:
            log('%s, found while trying to find goofs' % e)
            return None


if __name__ == "__main__":
    print '##### %s: Version - %s, has started ' % (__addonname__, __addonversion__)
    Main()
    print '##### %s: Version - %s, has stopped' % (__addonname__, __addonversion__)
