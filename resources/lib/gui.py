import sys
import xbmc
import xbmcgui

__addon__ = sys.modules["__main__"].__addon__
__addonid__ = sys.modules["__main__"].__addonid__
__cwd__ = sys.modules["__main__"].__cwd__


def log(txt):
    if isinstance(txt, str):
        txt = txt.decode("utf-8")
    message = u'%s: %s' % (__addonid__, txt)
    xbmc.log(msg=message.encode("utf-8"), level=xbmc.LOGDEBUG)


class Screensaver(xbmcgui.WindowXMLDialog):

    def __init__(self, *args, **kwargs):
        self.stop = False
        self.Monitor = MyMonitor(action=self.exit)

    def onInit(self):
        # get addon settings
        self.winid   = xbmcgui.Window(xbmcgui.getCurrentWindowDialogId())
        self._get_settings()
        self._set_prop('path', self.slideshow_path)
        log('qlock image path: %s' % self.slideshow_path)

        while (not xbmc.abortRequested) and (not self.stop):
            xbmc.sleep(1000)

    def exit(self):
        self.stop = True
        # clear our properties on exit
        self._clear_prop('path')
        self.close()

    def _get_settings(self):
        # read addon settings
        self.slideshow_path   = __addon__.getSetting('path')

    def _set_prop(self, name, value):
        self.winid.setProperty('Qlock.%s' % name, value)

    def _clear_prop(self, name):
        self.winid.clearProperty('Qlock.%s' % name)



class MyMonitor(xbmc.Monitor):

    def __init__(self, *args, **kwargs):
        self.action = kwargs['action']

    def onScreensaverDeactivated(self):
        self.action()
