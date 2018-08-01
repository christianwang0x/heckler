import wx
import pickle
from viewer import ViewerPanel

class ViewerEventPanel(ViewerPanel):
    def __init__(self, *args, **kwargs):
        super(ViewerEventPanel, self).__init__(*args, **kwargs)
        self.InitViewerEvents()

    def InitViewerEvents(self):
        self.request_list.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnRequestSelect)

    def OnRequestSelect(self, e):
        row = self.request_list.GetFirstSelected()
        if row < 0:
            return None
        response = self.request_list.GetItem(row, 8).GetText()
        self.response_box.SetValue(response)

    def OnSave(self, e):
        with wx.FileDialog(self, "Save requests to file", wildcard="Pickle files (*.p)|*.p",
                           style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as fileDialog:

            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return

            pathname = fileDialog.GetPath()
            with open(pathname, 'w') as fp:
                pickle.dump(self.reqs, fp)
