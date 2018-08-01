import wx
from window import ToolbarFrame
from async_main import WxAsyncApp
from asyncio.events import get_event_loop


def main():
    app = WxAsyncApp()
    loop = get_event_loop()
    toolbar_frame = ToolbarFrame(loop, None)
    toolbar_frame.Show()
    loop.run_until_complete(app.MainLoop())

if __name__ == '__main__':
    main()
