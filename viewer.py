import wx

# Defines the layout and formatting for the viewer tab
class ViewerPanel(wx.Panel):
    def __init__(self, parent_window, reqs, *args, **kwargs):
        super(ViewerPanel, self).__init__(*args, **kwargs)
        self.request_list = \
            wx.ListCtrl(self, wx.ID_ANY,
                        style=wx.LC_REPORT |
                              wx.LC_SINGLE_SEL)
        self.response_box = wx.TextCtrl(self, style=wx.TE_READONLY | wx.TE_MULTILINE )

        self.parent_window = parent_window
        self.fwfont = wx.Font(9, wx.FONTFAMILY_TELETYPE,
                              wx.FONTSTYLE_NORMAL,
                              wx.FONTWEIGHT_NORMAL)

        self.hfont = wx.SystemSettings.GetFont(wx.SYS_SYSTEM_FONT)
        self.hfont.SetPointSize(9)
        self.OnRender = None
        self.reqs = reqs
        self.InitViewer()
        self.LoadRequests(reqs)

    def InitViewer(self):
        sizer = wx.GridBagSizer(1, 1)
        self.SetSizer(sizer)
        sizer.Add(self.response_box, pos=(12, 3), span=(8, 7), flag=wx.EXPAND)
        self.response_box.SetFont(self.fwfont)
        self.request_list.SetFont(self.fwfont)
        rlist = self.request_list
        rlist.InsertColumn(0, 'No.', width=50)
        rlist.InsertColumn(1, 'Method', width=50)
        rlist.InsertColumn(2, 'URL', width=150)
        rlist.InsertColumn(3, 'Parameters', width=150)
        rlist.InsertColumn(4, 'Length', width=50)
        rlist.InsertColumn(5, 'Status', width=50)
        rlist.InsertColumn(6, 'Response time', width=50)
        rlist.InsertColumn(7, 'Request', width=200, format=wx.LIST_FORMAT_LEFT)
        rlist.InsertColumn(8, 'Response', width=200)
        sizer.Add(rlist, pos=(3, 3), span=(8, 7), flag=wx.EXPAND)
        """
        render_btn = wx.Button(self, label="Render response", size=(120, 25))
        render_btn.SetFont(self.hfont)
        sizer.Add(render_btn, pos=(3, 10))
        render_btn.Bind(wx.EVT_BUTTON, self.OnRender)
        """
        sizer.AddGrowableCol(3)
        sizer.AddGrowableRow(3)
        sizer.AddGrowableRow(12)

        sizer.Add((10, 10), pos=(20, 3))

    def ParseRequest(self, request):
        request_tl = request.request.split('\n')[0].rstrip()
        method, url, version = request_tl.split(' ')
        params = request.params
        length = len(request.response)
        status = request.response.split(b' ')[1].decode('utf-8', errors='ignore')
        response_time_f = request.response_time - request.request_time
        response_time = str(int(round(response_time_f * 1000))) + " ms"
        response = request.response.decode("utf-8", errors='ignore')
        _request = request.request
        return tuple((str(i) for i in (method, url, params, length,
                status, response_time, _request, response)))

    def LoadRequests(self, reqs):
        for no, request in enumerate(reqs):
            row_data = (str(no),) + self.ParseRequest(request)
            index = self.request_list.InsertItem(no, no)
            for column, data in enumerate(row_data):
                self.request_list.SetItem(index, column, data)
