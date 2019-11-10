# Qlock screensaver add-on by phil65
# credits to donabi & amet

import os
import sys
import xbmcaddon
import xbmc

__cwd__ = xbmcaddon.Addon().getAddonInfo('path').decode("utf-8")

sys.path.append(xbmc.translatePath(os.path.join(__cwd__, 'resources', 'lib').encode("utf-8")).decode("utf-8"))

if __name__ == '__main__':
    import gui
    screensaver_gui = gui.Screensaver('script-python-qlock.xml', __cwd__, 'default')
    screensaver_gui.doModal()
    del screensaver_gui
    sys.modules.clear()
