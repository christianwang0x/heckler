import wx

class ViewerPanel(wx.Panel):
    def __init__(self, parent_window, *args, **kwargs):
        super(ViewerPanel, self).__init__(*args, **kwargs)
        self.InitViewer()

    def InitViewer(self, requests):
        pass