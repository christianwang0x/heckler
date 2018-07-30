import wx
from window import ToolbarFrame


def main():
    app = wx.App()
    toolbar_frame = ToolbarFrame(None)
    toolbar_frame.Show()
    app.MainLoop()

if __name__ == '__main__':
    main()
