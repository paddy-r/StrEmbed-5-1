# HR June 2019 onwards
# Version 5 to follow HHC's StrEmbed-4 in Perl
# User interface for lattice-based assembly configurations

### ---
# HR 17/10/19
# Version 5.1 to draw main window as panels within flexgridsizer
# Avoids confusing setup for staticbox + staticboxsizer
### ---



# WX stuff
import wx
# WX customtreectrl for parts list
import wx.lib.agw.customtreectrl as ctc
# Allows inspection of app elements via Ctrl + Alt + I
# Use InspectableApp() in MainLoop()
import wx.lib.mixins.inspection as wit

# matplotlib stuff
import matplotlib as mpl
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wxagg import NavigationToolbar2WxAgg as NavigationToolbar

# OS operations for exception-free file checking
import os.path

# Import networkx for plotting lattice
import networkx as nx

# Gets rid of blurring throughout application by getting DPI info
import ctypes
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(True)
except:
    pass

# For STEP import
from step_parse_5_1 import StepParse



class MainWindow(wx.Frame):

    # Constructor
    def __init__(self):
        wx.Frame.__init__(self, parent = None, title = "PyStrEmbed-1")
        self.SetBackgroundColour('white')



        ### MENU BAR
        menuBar  = wx.MenuBar()

        fileMenu = wx.Menu()
        menuBar.Append(fileMenu, "&File")
        fileOpen = fileMenu.Append(wx.ID_OPEN, "&Open", "Open file")
        fileSave = fileMenu.Append(wx.ID_SAVE, "&Save", "Save file")
        fileSaveAs = fileMenu.Append(wx.ID_SAVEAS, "&Save as", "Save file as")
        fileClose = fileMenu.Append(wx.ID_CLOSE, "&Close", "Close file")
        fileExit = fileMenu.Append(wx.ID_EXIT, "&Exit", "Exit program")

        partMenu = wx.Menu()
        menuBar.Append(partMenu, "&Parts")

        geomMenu = wx.Menu()
        menuBar.Append(geomMenu, "&Geometry")

        lattMenu = wx.Menu()
        menuBar.Append(lattMenu, "&Lattice")

        abtMenu   = wx.Menu()
        menuBar.Append(abtMenu,  "&About")
        menuAbout = abtMenu.Append(wx.ID_ABOUT,"&About", "About PyStrEmbed-1")

        self.SetMenuBar(menuBar)



        # Bindings for menu items
        self.Bind(wx.EVT_MENU, self.OnFileOpen,      fileOpen)
        self.Bind(wx.EVT_MENU, self.DoNothingDialog, fileSave)
        self.Bind(wx.EVT_MENU, self.DoNothingDialog, fileSaveAs)
        self.Bind(wx.EVT_MENU, self.OnExit,  fileClose)
        self.Bind(wx.EVT_MENU, self.OnExit,  fileExit)
        self.Bind(wx.EVT_MENU, self.OnAbout, menuAbout)



        ### TOOLBAR
        # Main window toolbar with assembly operations
        self.tb = wx.ToolBar(self, style = wx.TB_NODIVIDER | wx.TB_FLAT)
        self.SetToolBar(self.tb)
        self.tb.SetToolBitmapSize((40,40))
        self.tb.SetBackgroundColour('white')
        # File tools
        self.fileOpenTool  = self.tb.AddTool(wx.ID_ANY, 'Open',  wx.Bitmap("Images/fileopen.bmp"),  bmpDisabled = wx.NullBitmap,
                                   shortHelp = 'File open',  longHelp = 'File open')
        self.exitTool      = self.tb.AddTool(wx.ID_ANY, 'Exit', wx.Bitmap("Images/fileclose.bmp"), bmpDisabled = wx.NullBitmap,
                                   shortHelp = 'Exit', longHelp = 'Exit')
        self.tb.AddSeparator()
        # Assembly tools
        self.insertLeftTool   = self.tb.AddTool(wx.ID_ANY, 'Insert node to left', wx.Bitmap("Images/insertleft1.bmp"), bmpDisabled = wx.NullBitmap,
                                 shortHelp = 'Insert left', longHelp = 'Insert left')
        self.insertRightTool  = self.tb.AddTool(wx.ID_ANY, 'Insert node to right', wx.Bitmap("Images/insertright1.bmp"), bmpDisabled = wx.NullBitmap,
                                 shortHelp = 'Insert right', longHelp = 'Insert right')
        self.adoptTool        = self.tb.AddTool(wx.ID_ANY, 'Adopt node', wx.Bitmap("Images/adopt1.bmp"), bmpDisabled = wx.NullBitmap,
                                 shortHelp = 'Adopt',  longHelp = 'Adopt')
        self.aggregateTool    = self.tb.AddTool(wx.ID_ANY, 'Aggregate nodes', wx.Bitmap("Images/aggregate1.bmp"), bmpDisabled = wx.NullBitmap,
                                 shortHelp = 'Aggregate',   longHelp = 'Aggregate')
        self.disaggregateTool = self.tb.AddTool(wx.ID_ANY, 'Disaggregate nodes', wx.Bitmap("Images/disaggregate1.bmp"), bmpDisabled = wx.NullBitmap,
                                 shortHelp = 'Disaggregate', longHelp = 'Disaggregate')
        self.tb.Realize()



        # Bind toolbar tools to actions
        self.Bind(wx.EVT_TOOL, self.OnFileOpen, self.fileOpenTool)
        self.Bind(wx.EVT_TOOL, self.OnExit,     self.exitTool)

        self.Bind(wx.EVT_TOOL, self.DoNothingDialog, self.insertLeftTool)
        self.Bind(wx.EVT_TOOL, self.DoNothingDialog, self.insertRightTool)
        self.Bind(wx.EVT_TOOL, self.DoNothingDialog, self.adoptTool)
        self.Bind(wx.EVT_TOOL, self.DoNothingDialog, self.aggregateTool)
        self.Bind(wx.EVT_TOOL, self.DoNothingDialog, self.disaggregateTool)



        ### STATUS BAR
        # Status bar
        self.statbar = self.CreateStatusBar()
        self.statbar.SetBackgroundColour('white')
        # Update status bar with window size on (a) first showing and (b) resizing
        self.Bind(wx.EVT_SIZE, self.OnResize, self)



        # Create main panel
        self.InitMainPanel()



    def InitMainPanel(self):

        ### MAIN PANEL
        #
        # Create main panel to contain everything
        self.panel = wx.Panel(self)
        self.box   = wx.BoxSizer(wx.VERTICAL)

        # Create FlexGridSizer to have 3 panes
        # 2nd and 3rd arguments are hgap and vgap b/t panes (cosmetic)
        self.grid = wx.FlexGridSizer(cols = 3, rows = 2, hgap = 10, vgap = 10)

        self.part_header = wx.StaticText(self.panel, label = "Parts view")
        self.geom_header = wx.StaticText(self.panel, label = "Geometry view")
        self.latt_header = wx.StaticText(self.panel, label = "Lattice view")

        self.panel_style = wx.SIMPLE_BORDER
        self.part_panel = wx.Panel(self.panel, style = self.panel_style)
        self.geom_panel = wx.Panel(self.panel, style = self.panel_style)
        self.latt_panel = wx.Panel(self.panel, style = self.panel_style)

        self.part_sizer = wx.BoxSizer(wx.VERTICAL)
        self.latt_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Some special setup for geometry sizer (grid)
        self.image_cols = 2
        self.geom_sizer = wx.GridSizer(cols = self.image_cols, rows = 0, hgap = 5, vgap = 5)
        # Defines tightness of images in grid (i.e. produces blank border)
        self.geom_tight = 0.7


        # PARTS VIEW SETUP
        # Custom tree ctrl implementation
        self.treeStyle = (ctc.TR_MULTIPLE | ctc.TR_EDIT_LABELS | ctc.TR_HAS_BUTTONS)
        self.partTree_ctc = ctc.CustomTreeCtrl(self.part_panel, agwStyle = self.treeStyle)
        self.partTree_ctc.SetBackgroundColour('white')
        self.part_sizer.Add(self.partTree_ctc, 1, wx.EXPAND)



        # GEOMETRY VIEW SETUP
        # Set up image-view grid, where "rows = 0" means the sizer updates dynamically
        # according to the number of elements it holds
#        self.geom_sizer.Add(self.image_grid, 1, wx.EXPAND)

        # Binding for toggling of part/assembly images
        # though toggle buttons not yet realised
        self.Bind(wx.EVT_TOGGLEBUTTON, self.ImageToggled)
        
        self.no_image_ass  = 'Images/noimage_ass.png'
        self.no_image_part = 'Images/noimage_part.png'



        # LATTICE VIEW SETUP
        # Set up matplotlib FigureCanvas with toolbar for zooming and movement
        self.latt_figure = mpl.figure.Figure()
        self.latt_canvas = FigureCanvas(self.latt_panel, -1, self.latt_figure)
        self.latt_axes   = self.latt_figure.add_subplot(111)
        self.latt_canvas.Hide()

        # Realize but hide, to be shown later when file loaded/data updated
        self.latt_tb = NavigationToolbar(self.latt_canvas)
#        self.latt_tb.Realize()
        self.latt_tb.Hide()

        self.latt_sizer.Add(self.latt_canvas, 1, wx.EXPAND | wx.ALIGN_BOTTOM | wx.ALL, border = 5)
        self.latt_sizer.Add(self.latt_tb, 0, wx.EXPAND)

        self.selected_colour = 'blue'
        


        # OVERALL SIZERS SETUP
        self.part_panel.SetSizer(self.part_sizer)
        self.geom_panel.SetSizer(self.geom_sizer)
        self.latt_panel.SetSizer(self.latt_sizer)

        self.grid.AddMany([(self.part_header), (self.geom_header), (self.latt_header),
                           (self.part_panel, 1, wx.EXPAND), (self.geom_panel, 1, wx.EXPAND), (self.latt_panel, 1, wx.EXPAND)])

        # Set all grid elements to "growable" upon resizing
        # Flags (second argument is proportional size)
        self.grid.AddGrowableRow(1,0)
        self.grid.AddGrowableCol(0,3)
        self.grid.AddGrowableCol(1,2)
        self.grid.AddGrowableCol(2,3)

        # Set sizer for/update main panel
        self.box.Add(self.grid, 1, wx.ALL | wx.EXPAND, 5)
        self.panel.SetSizer(self.box)



    def GetFilename(self, dialog_text = "Open file", starter = None, ender = None):

        ### General file-open method; takes list of file extensions as argument
        ### and can be used for specific file names ("starter", string)
        ### or types ("ender", string or list)

        # Convert "ender" to list if only one element
        if isinstance(ender, str):
            ender = [ender]

        # Check that only one kwarg is present
        # Create text for file dialog
        if starter is not None and ender is None:
            file_open_text = starter.upper() + " files (" + starter.lower() + "*)|" + starter.lower() + "*"
        elif starter is None and ender is not None:
            file_open_text = [el.upper() + " files (*." + el.lower() + ")|*." + el.lower() for el in ender]
            file_open_text = "|".join(file_open_text)
        else:
            raise ValueError("Requires starter or ender only")

        # Create file dialog
        fileDialog = wx.FileDialog(self, dialog_text, "", "",
                                   file_open_text,
                                   wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        fileDialog.ShowModal()
        filename = fileDialog.GetPath()
        fileDialog.Destroy()

        # Return file name, ignoring rest of path
        return filename



    def DisplayPartsList(self):

        # Create root node...
        root_id  = self.assembly.tree.root
        root_tag = self.assembly.tree.get_node(root_id).tag

        # Exception handler if file loaded previously
        try:
            self.partTree_ctc.DeleteAllItems()
        except:
            pass
        ctc_root_item = self.partTree_ctc.AddRoot(text = root_tag, ct_type = 1)
        self.ctc_dict[root_id] = ctc_root_item
        self.ctc_dict_inv[ctc_root_item] = root_id

        # ...then all others
        # Assumes treelib ordering ensures parents are defined before children
        for el in self.assembly.tree_dict:
            if el != root_id:
                parent_id = self.assembly.tree.parent(el).identifier
                ctc_parent = self.ctc_dict[parent_id]
                ctc_text = self.assembly.part_dict[self.assembly.tree_dict[el]]
                ctc_item = self.partTree_ctc.AppendItem(ctc_parent, text = ctc_text, ct_type = 1)
                self.ctc_dict[el] = ctc_item
                self.ctc_dict_inv[ctc_item] = el
        
        # Binding for checking of list items
        self.Bind(ctc.EVT_TREE_ITEM_CHECKED, self.TreeItemChecked)
        self.Bind(ctc.EVT_TREE_SEL_CHANGED,  self.TreeItemSelected)

        self.partTree_ctc.ExpandAll()
        


    def TreeItemChecked(self, event):
        
        def ScaleImage(img):
            # Resize image to geometry panel
            # NEEDS IMPROVEMENT TO BE MORE GENERAL (IN TERMS OF ASPECT RATIO)
            p_w, p_h   = self.geom_panel.GetSize()
            h          = img.GetHeight()
            w          = img.GetWidth()
            
            w_new = p_w*self.geom_tight/self.image_cols
            h_new = w_new*h/w
            img = img.Scale(w_new, h_new)

            return img
        
        
        
        # Get checked item and search for corresponding image
        #
        item = event.GetItem()
        id_  = self.ctc_dict_inv[item]
        
        self.selected_items = self.partTree_ctc.GetSelections()

        if item.IsChecked():
            # Get image
            if id_ in self.assembly.leaf_ids:
                img = self.assembly.tree_dict[id_]
                img = os.path.join('Images', img + '.png')
                if os.path.isfile(img):
                    img = wx.Image(img, wx.BITMAP_TYPE_ANY)
                else:
                    img = wx.Image(self.no_image_part, wx.BITMAP_TYPE_ANY)
            else:
                img = wx.Image(self.no_image_ass, wx.BITMAP_TYPE_ANY)
                
            # Create/add button in geom_panel
            # 
            # Includes rescaling to panel
            img = ScaleImage(img)
            button = wx.BitmapToggleButton(self.geom_panel, id_, wx.Bitmap(img))
            button.SetBackgroundColour('white')
            self.geom_sizer.Add(button, 0, wx.EXPAND)
            
            # Update global list and dict
            #
            # Data is list, i.e. same format as "selected_items"
            # but ctc lacks "get selections" method for checked items
            self.checked_items.append(item)
            self.button_dict[id_] = button
            self.button_dict_inv[button] = id_
            
            # Toggle if already selected elsewhere
            if self.ctc_dict[id_] in self.selected_items:
                button.SetValue(True)
            else:
                pass
            
        else:
            # Remove button from geom_panel
            obj = self.button_dict[id_]
            obj.Destroy()
            
            # Update global list and dict
            self.checked_items.remove(item)
            self.button_dict.pop(id_)
            self.button_dict_inv.pop(obj)
           
        # Update image sizer
        self.geom_sizer.Layout()
            


    def TreeItemSelected(self, event):
        
        # Get selected item and update global list of items
        #
        # Using GetSelection rather than maintaining list of items
        # as with checked items b/c releasing ctrl key during multiple
        # selection means not all selections are tracked easily
        self.selected_items = self.partTree_ctc.GetSelections()
        
        self.UpdateToggledImages()
        self.UpdateLatticeSelections()



    def ImageToggled(self, event):
        
        id_ = event.GetId()
        self.UpdateListSelections(id_)
        
        self.UpdateLatticeSelections()

        

    def UpdateListSelections(self, id_):
        
        # Select/deselect parts list item
        item = self.ctc_dict[id_]
        if item in self.selected_items:
            self.selected_items.remove(item)
        else:
            self.selected_items.append(item)
        
        # With "select = True", SelectItem toggles state if multiple selections enabled
        self.partTree_ctc.SelectItem(self.ctc_dict[id_], select = True)



    def UpdateLatticeSelections(self):
        
        # Update colour of selected items
        #
        # Set all back to default colour first
        for node in self.assembly.g.nodes():
            self.assembly.g.nodes[node]['colour'] = self.assembly.default_colour
        # Then selected nodes
        for item in self.selected_items:
            id_ = self.ctc_dict_inv[item]
            self.assembly.g.nodes[id_]['colour'] = self.selected_colour
        
        # Redraw lattice
        self.DisplayLattice()


    
    def UpdateToggledImages(self):
        
        for id_, button in self.button_dict.items():
            button.SetValue(False)
        
        for item in self.selected_items:
            id_    = self.ctc_dict_inv[item]
            if id_ in self.button_dict:
                button = self.button_dict[id_]
                button.SetValue(True)
            else:
                pass
        


    def DisplayLattice(self):

        # Get node positions, colour map, labels
        pos         = nx.get_node_attributes(self.assembly.g, 'pos')
        colour_map  = [self.assembly.g.nodes[el]['colour'] for el in self.assembly.g.nodes]
#        node_labels = nx.get_node_attributes(self.assembly.g, 'label')
        
        # Draw to lattice panel figure
        try:
            self.latt_axes.clear()
        except:
            pass
        nx.draw(self.assembly.g, pos, node_color = colour_map, with_labels = True, ax = self.latt_axes)
#        nx.draw_networkx_labels(self.assembly.g, pos, labels = node_labels, ax = self.latt_axes)

        # Minimise white space around plot in panel
        self.latt_figure.subplots_adjust(left = 0.01, bottom = 0.01, right = 0.99, top = 0.99)

        # Show lattice figure
        self.latt_canvas.draw()
        self.latt_canvas.Show()
        self.latt_tb.Show()

        # Update lattice panel layout
        self.latt_panel.Layout()



    def DoNothingDialog(self, event):

        nowt = wx.MessageDialog(self, "Functionality to be added", "Do nothing dialog", wx.OK)
        # Create modal dialogue that stops process
        nowt.ShowModal()
        nowt.Destroy()



    def OnFileOpen(self, event):

#        # Delete if exists from previous file load
#        # TO BE COMPLETED FOR VERSION 1-2
#        try:
#            del self.assembly
#        except AttributeError:
#            pass
        
        # Get STEP filename
        self.open_filename = self.GetFilename(ender = ["stp", "step"]).split("\\")[-1]

        # Load data, create nodes and edges, etc.
        self.assembly = StepParse()
        self.assembly.load_step(self.open_filename)
        self.assembly.create_tree()

        # Checked and selected items lists, shared b/t all views
        self.checked_items  = []
        self.selected_items = []

        # Toggle buttons
        self.button_dict     = {}
        self.button_dict_inv = {}
        
        # Write interactive parts list using WX customtreectrl, from treelib nodes
        self.ctc_dict     = {}
        self.ctc_dict_inv = {}



        # Show parts list and lattice
        self.DisplayPartsList()
        
        # Clear geometry window if necessary
        try:
            self.geom_sizer.Clear(True)
        except:
            pass    
        
        # Clear lattice plot if necessary
        try:
            self.latt_axes.clear()
        except:
            pass
        
        # Display lattice
        self.DisplayLattice()



    def OnInsertLeft(self, event):
        pass



    def OnInsertRight(self, event):
        pass



    def OnAdopt(self, event):

        pass



    def OnAggregate(self, event):

        pass



    def OnDisaggregate(self, event):

        pass



    def OnAbout(self, event):

        # Show program info
        abt_text = """StrEmbed-5-1: A user interface for manipulation of design configurations\n
            Copyright (C) 2019 Hugh Patrick Rice\n
            This program is free software: you can redistribute it and/or modify
            it under the terms of the GNU General Public License as published by
            the Free Software Foundation, either version 3 of the License, or
            (at your option) any later version.\n
            This program is distributed in the hope that it will be useful,
            but WITHOUT ANY WARRANTY; without even the implied warranty of
            MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
            GNU General Public License for more details.\n
            You should have received a copy of the GNU General Public License
            along with this program. If not, see <https://www.gnu.org/licenses/>."""
 
        abt = wx.MessageDialog(self, abt_text, 'About StrEmbed-5-1', wx.OK)
        abt.ShowModal()         # Shows dialogue that stops process (modal)
        abt.Destroy()



    def OnExit(self, event):

        self.Close(True)        # Close program



    def OnResize(self, event):

        # Display window size in status bar
        self.statbar.SetStatusText("Window size = " + format(self.GetSize()))
        event.Skip()



if __name__ == '__main__':
    app = wit.InspectableApp()
    frame = MainWindow()
    frame.Show()
    frame.Maximize()
    app.MainLoop()
