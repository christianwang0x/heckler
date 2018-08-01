import wx
import pickle
import engine
from options import Options
from constants import *


class EventsPanel(wx.Panel):
    def __init__(self, parent_window, *args, **kwargs):
        super(EventsPanel, self).__init__(*args, **kwargs)
        self.ops = Options()
        self.requests = []
        self.hfont = wx.SystemSettings.GetFont(wx.SYS_SYSTEM_FONT)
        self.hfont.SetPointSize(9)
        self.fwfont = wx.Font(9, wx.FONTFAMILY_TELETYPE,
                              wx.FONTSTYLE_NORMAL,
                              wx.FONTWEIGHT_NORMAL)
        self.parent_window = parent_window
        self.engine = None

    def OnRun(self, e):
        if self.running:
            wx.MessageBox("Engine is already running", 'Error', wx.OK | wx.ICON_INFORMATION)
            return None

        s = self.ops.validate()
        if s:
            wx.MessageBox(s, 'Input Error', wx.OK | wx.ICON_EXCLAMATION)
            return None
        else:
            self.running = True
            self.parent_window.ToolBar.EnableTool(wx.ID_STOP, True)
            self.parent_window.ToolBar.EnableTool(wx.ID_EXECUTE, False)
            host = str(self.ops.host.GetValue())
            port = int(self.ops.port.GetValue())
            threads = int(self.ops.threads.GetValue())
            _ssl = int(self.ops.https.GetValue())
            template = self.ops.data.GetValue()
            encoder = self.ops.encoder.GetValue()
            self.ops.encode_all_payloads(encoder)
            pset = self.ops.ps_sets
            mode = self.ops.mode.GetValue()
            E = engine.Engine(host, port, threads)
            reqs = E.run(template, pset, _ssl, mode)
            self.parent_window.CreateViewer(reqs)
            self.running = False
            self.parent_window.ToolBar.EnableTool(wx.ID_STOP, False)
            self.parent_window.ToolBar.EnableTool(wx.ID_EXECUTE, True)
            return None

    def OnStop(self, e):
        if not self.running:
            wx.MessageBox("Engine is not running", "Error", wx.OK | wx.ICON_INFORMATION)
            return None
        # self.requester.stop_signal = True
        self.running = False
        self.parent_window.ToolBar.EnableTool(wx.ID_STOP, False)
        self.parent_window.ToolBar.EnableTool(wx.ID_EXECUTE, True)
        return None

    def OnNew(self, e):
        pass

    def OnSave(self, e):
        with wx.FileDialog(self, "Save requests to file", wildcard="Pickle files (*.p)|*.p",
                           style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as fileDialog:

            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return

            pathname = fileDialog.GetPath()
            #with open(pathname, 'w') as fp:
             #   pickle.dump(self.reqs, fp)

    def OnOpen(self, e):
        pass

    def OnOpenSetup(self, e):
        with wx.FileDialog(self, "Open setup file", wildcard="Pickle files (*.p)|*.p",
                           style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return

            pathname = fileDialog.GetPath()
            with open(pathname, 'r') as fp:
                setup = pickle.load(fp)
                for (key, value) in vars(setup):
                    getattr(self.ops, key).SetValue(value)

    def OnSaveSetup(self, e):
        with wx.FileDialog(self, "Save current setup to file", wildcard="Pickle files (*.p)|*.p",
                           style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return
            pathname = fileDialog.GetPath()
            with open(pathname, 'w') as fp:
                pickle.dump(self.ops, fp)

    def OnExit(self, e):
        self.Close()

    def OnPreferences(self, e):
        pass

    def OnHelp(self, e):
        wx.MessageBox(HELP_MSG, 'Help', wx.OK | wx.ICON_QUESTION)

    def OnAbout(self, e):
        wx.MessageBox(ABOUT_MSG, 'About', wx.OK | wx.ICON_INFORMATION)

    def UpdatePSBox(self):
        current_marker = self.ops.marker_no.GetValue()
        self.ops.ps_box.Clear()
        current_ps = self.ops.ps_sets.get(current_marker, [])
        for p in current_ps:
            self.ops.ps_box.Append(p)
        return None

    def OnLoadSetFile(self, e):
        with wx.FileDialog(self, "Open parameter file", wildcard="All files (*.*)|*.*",
                           style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return

            pathname = fileDialog.GetPath()
            with open(pathname, 'r') as fp:
                ps = [i.rstrip() for i in fp.readlines()]
                current_marker = self.ops.marker_no.GetValue()
                self.ops.ps_sets[current_marker] = ps
                self.UpdatePSBox()


    def OnAddP(self, e):
        new_p = self.ops.add_p.GetValue()
        current_marker = self.ops.marker_no.GetValue()
        current_ps = self.ops.ps_sets.get(current_marker)
        if current_ps is None:
            self.ops.ps_sets[current_marker] = [new_p, ]
        else:
            current_ps.append(new_p)
        self.UpdatePSBox()

    def OnDelP(self, e):
        current_marker = self.ops.marker_no.GetValue()
        current_ps = self.ops.ps_sets.get(current_marker)
        if not current_ps:
            return
        selected = self.ops.ps_box.GetSelections()
        if not selected:
            current_ps.pop()
        else:
            for i in selected:
                current_ps.pop(i)
        self.UpdatePSBox()


    def OnClearPS(self, e):
        current_marker = self.ops.marker_no.GetValue()
        self.ops.ps_sets[current_marker] = []
        self.UpdatePSBox()


    def OnSelectPS(self, e):
        new_no = self.ops.marker_no.GetValue()
        new_ps = self.ops.ps_sets.get(new_no, [])
        self.ops.ps_box.Clear()
        for p in new_ps:
            self.ops.ps_box.Append(p)
        return None

    def OnAddMarkers(self, e):
        index = self.ops.data.GetInsertionPoint()
        sindex = index
        squote = chr(0xab)
        equote = chr(0xbb)
        oldtext = self.ops.data.GetValue()
        newtext = oldtext[:sindex] + squote
        newtext += equote + oldtext[sindex:]
        self.ops.data.SetValue(newtext)
        return None

    def OnClearMarkers(self, e):
        oldtext = self.ops.data.GetValue()
        newtext = oldtext.replace(chr(0xab), '')
        newtext = newtext.replace(chr(0xbb), '')
        self.ops.data.SetValue(newtext)
        return None