import wx

class LayoutFrame(wx.Frame):
    def __init__(self, *args, **kwargs):
        super(LayoutFrame, self).__init__(*args, **kwargs)
        self.InitLayout()

    def InitLayout(self):
        panel = wx.Panel(self)
        sizer = wx.GridBagSizer(3, 3)
        panel.SetSizer(sizer)
        data_box = wx.TextCtrl(panel, style=wx.TE_MULTILINE)
        sizer.Add(data_box, pos=(1, 1), span=(32, 2), flag=wx.EXPAND)

        sizer.AddGrowableCol(1)
        sizer.AddGrowableRow(32)

        run_btn = wx.Button(panel, label="Run", size=(120,30))
        sizer.Add(run_btn, pos=(1, 4))
        stop_btn = wx.Button(panel, label="Stop", size=(120,30))
        sizer.Add(stop_btn, pos=(1,5))
        cnt_btn = wx.Button(panel, label="Continue", size=(120, 30))
        sizer.Add(cnt_btn, pos=(1,6))

        host_lbl = wx.StaticText(panel, label="Host:")
        sizer.Add(host_lbl, pos=(3,4))
        host_txt = wx.TextCtrl(panel)
        sizer.Add(host_txt, pos=(3, 5), span=(1, 2), flag=wx.EXPAND)

        port_lbl = wx.StaticText(panel, label="Port:")
        sizer.Add(port_lbl, pos=(4, 4))
        port_txt = wx.TextCtrl(panel)
        sizer.Add(port_txt, pos=(4, 5), flag=wx.EXPAND)
        ssl_chk = wx.CheckBox(panel, label="HTTPS")
        sizer.Add(ssl_chk, pos=(4, 6))

        sep1 = wx.StaticLine(panel, size=(300, 1))
        sizer.Add(sep1, pos=(6, 4), span=(1, 4), flag=wx.ALIGN_CENTER)

        mode_lbl = wx.StaticText(panel, label="Mode:")
        sizer.Add(mode_lbl, pos=(8, 4))
        mode_names = ['Serial', 'Concurrent', 'Multiplex', 'Permuter']
        mode_cb = wx.ComboBox(panel, choices=mode_names,
                         style=wx.CB_READONLY)
        sizer.Add(mode_cb, pos=(8, 5), span=(1, 2))

        mark_lbl = wx.StaticText(panel, label="Marker #:")
        sizer.Add(mark_lbl, pos=(9,4))
        mark_numbers = [str(i) for i in range(1, 17)]
        mark_cb = wx.ComboBox(panel, choices=mark_numbers,
                              style=wx.CB_READONLY)
        sizer.Add(mark_cb, pos=(9, 5))

        load_ps_btn = wx.Button(panel, label="Load File", size=(90, 30))
        sizer.Add(load_ps_btn, pos=(9, 6))
        ps_lb = wx.ListBox(panel)
        sizer.Add(ps_lb, pos=(10, 4), span=(5, 3), flag=wx.EXPAND)

        add_pl_btn = wx.Button(panel, label="Add", size=(90, 30))
        sizer.Add(add_pl_btn, pos=(15, 4))
        add_pl_txt = wx.TextCtrl(panel)
        sizer.Add(add_pl_txt, pos=(15, 5), span=(1, 2), flag=wx.EXPAND)

        encdr_lbl = wx.StaticText(panel, label="Encoder:")
        sizer.Add(encdr_lbl, pos=(16, 4), span=(1, 1))
        encdrs = ["None", "Hexadecimal", "Base 64", "MD5"]
        encdr_cb = wx.ComboBox(panel, choices=encdrs, style=wx.CB_READONLY)
        sizer.Add(encdr_cb, pos=(16, 5), span=(1, 2), flag=wx.EXPAND)

        sep2 = wx.StaticLine(panel, size=(300, 1))
        sizer.Add(sep2, pos=(18, 4), span=(1, 4), flag=wx.ALIGN_CENTER)

        update_cn = wx.CheckBox(panel, label="Update Content Length Header")
        sizer.Add(update_cn, pos=(20, 4), span=(1, 3))

        ka_cb = wx.CheckBox(panel, label="Keep-Alive")
        sizer.Add(ka_cb, pos=(21, 4), span=(1, 3))

        use_proxy = wx.CheckBox(panel, label="Use Proxy")
        sizer.Add(use_proxy, pos=(22, 4), span=(1, 3))

        host_lbl = wx.StaticText(panel, label="Proxy Host:")
        sizer.Add(host_lbl, pos=(23,4), span=(1, 1))
        host_txt = wx.TextCtrl(panel)
        sizer.Add(host_txt, pos=(23, 5), span=(1, 2), flag=wx.EXPAND)

        phost_lbl = wx.StaticText(panel, label="Proxy Port:")
        sizer.Add(phost_lbl, pos=(24,4), span=(1, 1))
        phost_txt = wx.TextCtrl(panel)
        sizer.Add(phost_txt, pos=(24, 5), span=(1, 2), flag=wx.EXPAND)

        use_proxy = wx.CheckBox(panel, label="Authenticate Proxy")
        sizer.Add(use_proxy, pos=(25, 4), span=(1, 3))

        user_lbl = wx.StaticText(panel, label="Proxy User:")
        sizer.Add(user_lbl, pos=(26,4), span=(1, 1))
        user_txt = wx.TextCtrl(panel)
        sizer.Add(user_txt, pos=(26, 5), span=(1, 2), flag=wx.EXPAND)

        pass_lbl = wx.StaticText(panel, label="Proxy Pass:")
        sizer.Add(pass_lbl, pos=(27,4), span=(1, 1))
        pass_txt = wx.TextCtrl(panel)
        sizer.Add(pass_txt, pos=(27, 5), span=(1, 2), flag=wx.EXPAND)

        nra_lbl = wx.StaticText(panel, label="Network Reconnect Attempts:")
        sizer.Add(nra_lbl, pos=(28,4), span=(1, 2))
        nra_txt = wx.TextCtrl(panel)
        sizer.Add(nra_txt, pos=(28, 6), span=(1, 1), flag=wx.EXPAND)

        nrd_lbl = wx.StaticText(panel, label="Network Reconnect Delay:")
        sizer.Add(nrd_lbl, pos=(29,4), span=(1, 2))
        nrb_txt = wx.TextCtrl(panel)
        sizer.Add(nrb_txt, pos=(29, 6), span=(1, 1), flag=wx.EXPAND)

        ct_lbl = wx.StaticText(panel, label="Connection Threads:")
        sizer.Add(ct_lbl, pos=(30,4), span=(1, 2))
        ct_txt = wx.TextCtrl(panel)
        sizer.Add(ct_txt, pos=(30, 6), span=(1, 1), flag=wx.EXPAND)

        dbr_lbl = wx.StaticText(panel, label="Delay Between Requests:")
        sizer.Add(dbr_lbl, pos=(31,4), span=(1, 2))
        dbr_txt = wx.TextCtrl(panel)
        sizer.Add(dbr_txt, pos=(31, 6), span=(1, 1), flag=wx.EXPAND)

        add_mark_btn = wx.Button(panel, label="Add Markers", size=(120, 30))
        sizer.Add(add_mark_btn, pos=(33, 1), flag=wx.ALIGN_RIGHT)
        clr_mark_btn = wx.Button(panel, label="Clear Markers", size=(120, 30))
        sizer.Add(clr_mark_btn, pos=(33, 2))

        progress_bar = wx.Gauge(panel, range=100)
        sizer.Add(progress_bar, pos=(34, 1), flag=wx.EXPAND, span=(1, 2))

        sizer.Add((10, 10), pos=(35, 1))

class MenuFrame(LayoutFrame):
    def __init__(self, *args, **kwargs):
        super(MenuFrame, self).__init__(*args, **kwargs)
        self.InitMenu()

    def InitMenu(self):
        menubar = wx.MenuBar()

        file_menu = wx.Menu()
        new_mi = wx.MenuItem(file_menu, wx.ID_ANY, '&New')
        open_mi = wx.MenuItem(file_menu, wx.ID_ANY, '&Open')
        save_mi = wx.MenuItem(file_menu, wx.ID_ANY, '&Save')
        open_setup_mi = wx.MenuItem(file_menu, wx.ID_ANY, '&Open Setup')
        save_setup_mi = wx.MenuItem(file_menu, wx.ID_ANY, '&Save Setup')
        close_mi = wx.MenuItem(file_menu, wx.ID_ANY, 'Close Window')
        exit_mi = wx.MenuItem(file_menu, wx.ID_ANY, 'Exit')

        [ file_menu.AppendItem(i) for i in (new_mi, open_mi, save_mi) ]
        file_menu.AppendSeparator()
        [ file_menu.AppendItem(i) for i in (open_setup_mi, save_setup_mi) ]
        file_menu.AppendSeparator()
        [ file_menu.AppendItem(i) for i in (close_mi, exit_mi) ]
        
        control_menu = wx.Menu()
        run_mi = wx.MenuItem(control_menu, wx.ID_ANY, '&Run')
        abort_mi = wx.MenuItem(control_menu, wx.ID_ANY, '&Abort')
        stop_mi = wx.MenuItem(control_menu, wx.ID_ANY, '&Stop')
        preferences_mi = wx.MenuItem(control_menu, wx.ID_ANY, '&Preferences')

        [ control_menu.AppendItem(i) for i in (run_mi, abort_mi, stop_mi)]
        control_menu.AppendSeparator()
        control_menu.AppendItem(preferences_mi)

        help_menu = wx.Menu()
        help_mi = wx.MenuItem(help_menu, wx.ID_ANY, '&Help')
        about_mi = wx.MenuItem(help_menu, wx.ID_ANY, '&About')

        help_menu.AppendItem(help_mi)
        help_menu.AppendItem(about_mi)
        help_menu.AppendSeparator()

        self.Bind(wx.EVT_MENU, self.OnNew, new_mi)
        self.Bind(wx.EVT_MENU, self.OnOpen, open_mi)
        self.Bind(wx.EVT_MENU, self.OnSave, save_mi)
        self.Bind(wx.EVT_MENU, self.OnOpenSetup, open_setup_mi)
        self.Bind(wx.EVT_MENU, self.OnSaveSetup, save_setup_mi)
        self.Bind(wx.EVT_MENU, self.OnClose, close_mi)
        self.Bind(wx.EVT_MENU, self.OnExit, exit_mi)
        
        self.Bind(wx.EVT_MENU, self.OnRun, run_mi)
        self.Bind(wx.EVT_MENU, self.OnAbort, abort_mi)
        self.Bind(wx.EVT_MENU, self.OnStop, stop_mi)
        self.Bind(wx.EVT_MENU, self.OnPreferences, preferences_mi)
        
        self.Bind(wx.EVT_MENU, self.OnHelp, help_mi)
        self.Bind(wx.EVT_MENU, self.OnAbout, about_mi)

        menubar.Append(file_menu, '&File')
        menubar.Append(control_menu, '&Control')
        menubar.Append(help_menu, '&Help')

        self.SetMenuBar(menubar)

    def OnNew(self, e):
        pass

    def OnOpen(self, e):
        pass

    def OnSave(self, e):
        pass

    def OnOpenSetup(self, e):
        pass

    def OnSaveSetup(self, e):
        pass

    def OnClose(self, e):
        self.Close()

    def OnExit(self, e):
        self.Close()

    def OnRun(self, e):
        pass

    def OnAbort(self, e):
        pass

    def OnStop(self, e):
        pass

    def OnPreferences(self, e):
        pass

    def OnHelp(self, e):
        pass

    def OnAbout(self, e):
        pass


class WindowFrame(MenuFrame):
    def __init__(self, *args, **kwargs):
        super(WindowFrame, self).__init__(*args, **kwargs)
        self.InitWindow()
        
    def InitWindow(self):
        self.SetSize((1200, 880))
        self.SetTitle('Heckler Control')
        self.Center()

def main():
    app = wx.App()
    window_frame = WindowFrame(None)
    window_frame.Show()
    app.MainLoop()

if __name__ == '__main__':
    main()
