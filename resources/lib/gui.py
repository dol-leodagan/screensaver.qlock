import os
import sys
import xbmc
import xbmcaddon
import xbmcgui
import datetime
from xml.dom import minidom

__addon__      = xbmcaddon.Addon()
__addonid__    = __addon__.getAddonInfo('id')
__cwd__        = __addon__.getAddonInfo('path').decode("utf-8")
__layoutDir__  = xbmc.translatePath(os.path.join( __cwd__, 'resources', 'layout' ))

class Screensaver(xbmcgui.WindowXMLDialog):

    class ExitMonitor(xbmc.Monitor):
        def __init__(self, exit_callback):
            self.exit_callback = exit_callback
        def onScreensaverDeactivated(self):
            self.exit_callback()
        def onAbortRequested(self):
            self.exit_callback()

    def onInit(self):
        self.stop    = False
        self.Monitor = self.ExitMonitor(self.exit)
        self.winid   = xbmcgui.Window(xbmcgui.getCurrentWindowDialogId())

        self.language = None
        self.now      = None

        # get addon settings
        self._get_settings()
        self._set_prop('background', self.slideshow_enabled)
        self._set_prop('path', self.slideshow_path)
        self._set_prop('level', "%XFFFFFF" % int(int(self.dim_level) / 100 * 255))

        self.loop()

        self.log('Qlock2 starting, background enable: %s, path: %s, level: %s' % (self.slideshow_enabled, self.slideshow_path, self.dim_level))

        while (not xbmc.abortRequested) and (not self.stop):
            xbmc.sleep(1000)
            self.loop()

    def loop(self):
        self.setLanguage()
        self.update()

    def log(self, txt):
        if isinstance(txt, str):
            txt = txt.decode("utf-8")
        message = u'%s: %s' % (__addonid__, txt)
        xbmc.log(msg=message.encode("utf-8"), level=xbmc.LOGDEBUG)

    def exit(self):
        self.stop = True

        # clear our properties on exit
        self._clear_prop('background')
        self._clear_prop('path')
        self._clear_prop('level')

        self.clearHighlight()
        self.clearBackground()

        del self.Monitor
        del self.winid

        self.close()

    def _get_settings(self):
        self.slideshow_enabled = __addon__.getSetting('background')
        self.slideshow_path    = __addon__.getSetting('path')
        self.dim_level         = __addon__.getSetting('level')

    def _set_prop(self, name, value):
        self.winid.setProperty('Qlock2.%s' % name, value)

    def _clear_prop(self, name):
        self.winid.clearProperty('Qlock2.%s' % name)


    def getLanguage(self):
        if xbmc.getLanguage() in (os.listdir(__layoutDir__)):
            lang = xbmc.getLanguage()
        else:
            lang = "English"

        return lang

    def setLanguage(self, lang = None):
        if lang is None:
            lang = self.getLanguage()

        if not self.language or lang != self.language:
            self.language = lang
            self.changeLayout()
            self.log("Set new Language - [%s]" % lang)

    def changeLayout(self):
        layout = xbmc.translatePath( os.path.join(__layoutDir__, self.language, 'layout.xml'))
        dom = minidom.parse(layout)

        backgrounds = dom.getElementsByTagName('background')
        self.background = backgrounds[0].getAttribute('all').split(',')

        times = dom.getElementsByTagName('time')
        time = times[0]
        time_layout = {}

        for time_attr in ('all', 'm00', 'm05', 'm10', 'm15', 'm20', 'm25', 'm30', 'm35', 'm40', 'm45', 'm50', 'm55', 'h01', 'h02', 'h03', 'h04', 'h05', 'h06', 'h07', 'h08', 'h09', 'h10', 'h11', 'h12'):
            time_layout[time_attr] = time.getAttribute(time_attr).split(',')

        for time_attr in ('shiftHour', 'shiftOnHalfHour', 'shiftOn20', 'shiftOn25'):
            try:
                time_layout[time_attr] = int(time.getAttribute(time_attr))
            except:
                time_layout[time_attr] = 0

        self.time = time_layout

        self.drawBackground()
        self.now = None

    def update(self):
        if self.timeChanged():
            self.now = datetime.datetime.now()
            self.clearHighlight()

            currentMinute = self.now.minute / 5 * 5
            minute = "m%.2d" % currentMinute

            to = int(self.time['shiftHour'])
            if currentMinute > 19:
                to += self.time['shiftOn20']
            if currentMinute > 24:
                to += self.time['shiftOn25']
            if currentMinute > 34:
                to += self.time['shiftOnHalfHour']

            shiftedHour = (self.now.hour + to) % 12
            if shiftedHour == 0:
                hour = "h12"
            else:
                hour = "h%.2d" % shiftedHour

            if self.language == 'German' and shiftedHour == 1 and currentMinute == 0 :
                # German only, at one o'clock
                self.drawHighlight(["1","2","4","5","6","45","46","47","108","109","110"])
            else:
                self.drawHighlight(self.time['all'])
                self.drawHighlight(self.time[hour])
                self.drawHighlight(self.time[minute])

    def drawHighlight(self, indices):
        for i in indices:
            self._set_prop('%d.Highlight' % int(i), self.background[int(i)-1])

    def clearHighlight(self):
        for i in range(len(self.background)):
            self._clear_prop('%d.Highlight' % (i + 1))

    def drawBackground(self):
        for i in range(len(self.background)):
            self._set_prop('%d.Background' % (i + 1), self.background[i])

    def clearBackground(self):
        for i in range(len(self.background)):
            self._clear_prop('%d.Background' % (i + 1))

    def timeChanged(self):
        current = datetime.datetime.now()
        if not self.now or current.minute / 5 * 5 != self.now.minute / 5 * 5 or current.hour != self.now.hour:
            return True
        return False