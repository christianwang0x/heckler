#!/usr/bin/python3

from window import ToolbarFrame
from wxasync import WxAsyncApp
from asyncio.events import get_event_loop


# The main function to call for the app. The wx.App object has
# been replaced with the WxAsyncApp, and the app.MainLoop() call
# has been placed inside an asyncio loop call. This is to
# make the app asynchronous, mostly so that the progress
# bar on the control panel can actually work, and so that it
# doesn't seem like the app has crashed while the user is
# running the engine.
def main():
    app = WxAsyncApp()
    loop = get_event_loop()
    toolbar_frame = ToolbarFrame(loop, None)
    toolbar_frame.Show()
    loop.run_until_complete(app.MainLoop())

if __name__ == '__main__':
    main()
