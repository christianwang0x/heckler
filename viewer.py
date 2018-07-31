import wx
# from viewer_events import ViewerEventPanel


class ViewerPanel(wx.Panel):
    def __init__(self, parent_window, reqs, *args, **kwargs):
        super(ViewerPanel, self).__init__(*args, **kwargs)
        self.request_list = wx.ListCtrl(self, wx.ID_ANY,
                                        style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        self.InitViewer()
        self.LoadRequests(reqs)
        self.parent_window = parent_window


    def InitViewer(self):
        sizer = wx.GridBagSizer(1, 1)
        self.SetSizer(sizer)
        rlist = self.request_list
        rlist.InsertColumn(0, 'No.', width=50)
        rlist.InsertColumn(1, 'Method', width=50)
        rlist.InsertColumn(2, 'URL', width=150)
        rlist.InsertColumn(3, 'Parameters', width=150)
        rlist.InsertColumn(4, 'Length', width=50)
        rlist.InsertColumn(5, 'Status', width=50)
        rlist.InsertColumn(6, 'Response time', width=50)
        rlist.InsertColumn(7, 'Request', width=200)
        rlist.InsertColumn(8, 'Response', width=200)
        sizer.Add(rlist, pos=(3, 3), span=(8, 7), flag=wx.EXPAND)

    def ParseRequest(self, request):
        request_tl = request.request.split('\n')[0].rstrip()
        method, url, version = request_tl.split(' ')
        params = request.params
        length = len(request.response)
        status = request.response.split(b' ')[1].decode('utf-8')
        response_time = request.response_time - request.request_time
        response = request.response.decode("utf-8")
        _request = request.request
        return tuple((str(i) for i in (method, url, params, length,
                status, response_time, _request, response)))

    def LoadRequests(self, reqs):
        for no, request in enumerate(reqs):
            row_data = self.ParseRequest(request)
            index = self.request_list.InsertItem(no, no)
            for column, data in enumerate(row_data):
                self.request_list.SetItem(index, column+1, data)
