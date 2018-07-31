import wx

class ViewerEventPanel(wx.Panel):
    def __init__(self, parent_window, *args, **kwargs):
        super(ViewerEventPanel, self).__init__(*args, **kwargs)
        self.parent_window = parent_window
