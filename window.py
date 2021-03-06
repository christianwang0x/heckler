import wx
from control import ControlPanel
from viewer_events import ViewerEventPanel


# Defines the menu at the top of the screen
# Unfortunately the current Async implementation does
# not work with menu items or toolbar items, so these
# controls have not been added yet.
class MenuFrame(wx.Frame):
    def __init__(self, *args, **kwargs):
        super(MenuFrame, self).__init__(*args, **kwargs)
        self.super_panel = wx.Panel(self)
        self.notebook = wx.Notebook(self.super_panel)
        self.control_panel = ControlPanel(self, self.notebook)
        self.notebook.AddPage(self.control_panel, "Control")
        sizer = wx.BoxSizer()
        sizer.Add(self.notebook, -1, wx.EXPAND | wx.ALL)
        self.super_panel.SetSizer(sizer)
        self.InitMenu()

    # Creates and adds menu items to the menu, and binds them to
    # the appropriate callback functions
    def InitMenu(self):

        menubar = wx.MenuBar()

        file_menu = wx.Menu()
        new_mi = wx.MenuItem(file_menu, wx.ID_ANY, '&New')
        open_mi = wx.MenuItem(file_menu, wx.ID_ANY, '&Open')
        save_mi = wx.MenuItem(file_menu, wx.ID_ANY, '&Save')
        open_setup_mi = wx.MenuItem(file_menu, wx.ID_ANY, '&Open Setup')
        save_setup_mi = wx.MenuItem(file_menu, wx.ID_ANY, '&Save Setup')
        exit_mi = wx.MenuItem(file_menu, wx.ID_ANY, 'Exit')

        [file_menu.Append(i) for i in (new_mi, open_mi, save_mi)]
        file_menu.AppendSeparator()
        [file_menu.Append(i) for i in (open_setup_mi, save_setup_mi)]
        file_menu.AppendSeparator()
        file_menu.Append(exit_mi)

        control_menu = wx.Menu()
        stop_mi = wx.MenuItem(control_menu, wx.ID_ANY, '&Stop')
        preferences_mi = wx.MenuItem(control_menu, wx.ID_ANY, '&Preferences')

        control_menu.Append(stop_mi)
        control_menu.AppendSeparator()
        control_menu.Append(preferences_mi)

        help_menu = wx.Menu()
        help_mi = wx.MenuItem(help_menu, wx.ID_ANY, '&Help')
        about_mi = wx.MenuItem(help_menu, wx.ID_ANY, '&About')

        help_menu.Append(help_mi)
        help_menu.Append(about_mi)
        help_menu.AppendSeparator()

        self.Bind(wx.EVT_MENU, self.control_panel.OnNew, new_mi)
        self.Bind(wx.EVT_MENU, self.control_panel.OnOpen, open_mi)
        self.Bind(wx.EVT_MENU, self.control_panel.OnSave, save_mi)
        self.Bind(wx.EVT_MENU, self.control_panel.OnOpenSetup, open_setup_mi)
        self.Bind(wx.EVT_MENU, self.control_panel.OnSaveSetup, save_setup_mi)
        self.Bind(wx.EVT_MENU, self.control_panel.OnExit, exit_mi)

        self.Bind(wx.EVT_MENU, self.control_panel.OnStop, stop_mi)
        self.Bind(wx.EVT_MENU, self.control_panel.OnPreferences, preferences_mi)

        self.Bind(wx.EVT_MENU, self.control_panel.OnHelp, help_mi)
        self.Bind(wx.EVT_MENU, self.control_panel.OnAbout, about_mi)

        menubar.Append(file_menu, '&File')
        menubar.Append(control_menu, '&Control')
        menubar.Append(help_menu, '&Help')

        self.SetMenuBar(menubar)

    # Create a viewer tab from a list of request objects.
    def CreateViewer(self, reqs):
        self.viewer_event_panel = ViewerEventPanel(self,reqs, self.notebook)
        self.notebook.AddPage(self.viewer_event_panel, "Viewer")
        return None


# Defines the size and title of the main window
class WindowFrame(MenuFrame):
    def __init__(self, *args, **kwargs):
        super(WindowFrame, self).__init__(*args, **kwargs)
        self.InitWindow()

    def InitWindow(self):
        self.SetSize((1200, 850))
        self.SetTitle('Heckler')
        self.Center()


# Initializes the toolbar, currently the run button does not work
# as the asynchronous bind function does not work with toolbar
# items.
class ToolbarFrame(WindowFrame):
    def __init__(self, loop, *args, **kwargs):
        super(ToolbarFrame, self).__init__(*args, **kwargs)
        self.toolbar = None
        self.InitToolbar()
        self.loop = loop

    def InitToolbar(self):
        toolbar = wx.ToolBar(self, wx.ID_ANY, pos=(0, 0))
        self.ToolBar = toolbar
        new_tb = toolbar.AddTool(wx.ID_NEW, "New", wx.Bitmap('res/icon/file.png'))
        open_tb = toolbar.AddTool(wx.ID_OPEN, "Open", wx.Bitmap('res/icon/folder-open.png'))
        save_tb = toolbar.AddTool(wx.ID_SAVE, "Save", wx.Bitmap('res/icon/save.png'))
        exit_tb = toolbar.AddTool(wx.ID_EXIT, "Exit", wx.Bitmap('res/icon/sign-out-alt.png'))
        # run_tb = toolbar.AddTool(wx.ID_EXECUTE, "Run", wx.Bitmap('res/icon/play.png'))
        stop_tb = toolbar.AddTool(wx.ID_STOP, "Stop", wx.Bitmap('res/icon/stop.png'))
        toolbar.EnableTool(wx.ID_STOP, False)
        toolbar.EnableTool(wx.ID_EXECUTE, False)
        toolbar.Bind(wx.EVT_TOOL, self.control_panel.OnNew, new_tb)
        toolbar.Bind(wx.EVT_TOOL, self.control_panel.OnOpen, open_tb)
        toolbar.Bind(wx.EVT_TOOL, self.control_panel.OnSave, save_tb)
        toolbar.Bind(wx.EVT_TOOL, self.control_panel.OnExit, exit_tb)
        # toolbar.Bind(wx.EVT_TOOL, self.control_panel.OnRun, run_tb)
        # AsyncBind(run_tb, wx.EVT_TOOL, self.control_panel.OnRun)
        toolbar.Bind(wx.EVT_TOOL, self.control_panel.OnStop, stop_tb)
        toolbar.Realize()
