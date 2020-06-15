# coding: UTF-8

"""
Experimenter_GUI; reformed previous Experimenter code with GUI interface 
Made to help an user to generate a Python script for a rather simple experiment.
jinook.oh@univie.ac.at
Cognitive Biology Dept., University of Vienna
- 2018.Apr

----------------------------------------------------------------------
Copyright (C) 2018 Jinook Oh, W. Tecumseh Fitch 
- Contact: jinook.oh@univie.ac.at, tecumseh.fitch@univie.ac.at

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
----------------------------------------------------------------------

This program was tested on OSX environment.

2018.APR.18
- 0.1: Initial development
2018.MAY.29
- 0.2: Changing stimuli-setup dialog

Features, limitations & dependencies :
- Text, image, sound, and video presentations are available.
- It assumes there's only one section; No limitation in number of trials or stimuli.
- This program itself and text & image presentation is performed using wxPython.
    http://www.wxpython.org/
- Sound presentation is performed using pyAudio.
    https://people.csail.mit.edu/hubert/pyaudio/
- Movie presentation is perforemd using wxPython's wx.media or VLC player. 
  For using VLC, VLC app should be installed
    http://www.videolan.org/vlc/index.html
  Also, VLC's Python binding should be located in 'scripts' folder.
    https://wiki.videolan.org/Python_bindings
"""

import sys
from os import path, getcwd, mkdir
from glob import glob
from copy import copy

import wx
from modules.item_panel import ItemPanel 
from modules.main_panel import MainPanel
from modules.script_panel import ScriptPanel
from modules.fFuncNClasses import GNU_notice, writeFile, get_time_stamp, show_msg, set_img_for_btn

DEBUGGING = False
VERSION = 'v.0.2'

#====================================================

class EGUIFrame(wx.Frame):

    def __init__(self):
        if DEBUGGING: print('EGUIFrame.__init__()')

        ### set up application folder
        if getattr(sys, 'frozen', False):
            ### If the application is run as a bundle, the pyInstaller bootloader
            # extends the sys module by a flag frozen=True and sets the app 
            # path into variable _MEIPASS'.
            self.e_gui_path = sys._MEIPASS

            ### TO BE FIXED 
            # After bundling with pyInstaller, running App failed, which seems to be the path issue.
            # The above sys._MEIPASS didn't work as expected.
            # When the path was stripped three times
            # (because e_gui.app/Contents/MacOS is where the e_gui executable is located)
            # using path.dirname, the e_gui.app successfully launched
            # Maybe this issue of pyInstaller might get fixed later
            for i in range(3):
                self.e_gui_path = path.dirname(self.e_gui_path)
        else:
            self.e_gui_path = path.dirname(path.abspath(__file__))
        
        self.flag_img = False
        self.flag_snd = False
        self.flag_mov = False
        self.flag_script_visible = False
        self.allowed_img_ext = ['png', 'jpg', 'tif', 'tiff']
        self.allowed_snd_ext = ['wav']
        self.allowed_mov_ext = ['mov', 'mp4', 'avi']
                                
        w_pos = (0, 25) 
        w_size = (wx.Display(0).GetGeometry()[2], wx.Display(0).GetGeometry()[3]-w_pos[1]) 
        self.w_sz = w_size # initial size

        wx.Frame.__init__(self, None, -1, "Experimenter_GUI - %s"%VERSION, 
                          pos = w_pos, 
                          size = w_size) 
                          #style=wx.DEFAULT_FRAME_STYLE^(wx.RESIZE_BORDER|wx.MAXIMIZE_BOX))
        self.SetBackgroundColour('#333333') 
        #self.ShowFullScreen(True)
        #self.Bind(wx.EVT_SIZE, self.onSizing)

        ### set window size exactly to self.w_sz without menubar/border/etc.
        _diff = (self.GetSize()[0]-self.GetClientSize()[0], self.GetSize()[1]-self.GetClientSize()[1])
        _sz = (w_size[0]+_diff[0], w_size[1]+_diff[1])
        self.SetSize(_sz)

        ### font setup
        if 'darwin' in sys.platform: _font = "Monaco"
        else: _font = "Courier"
        fontSz = 8
        self.base_script_font = wx.Font(20, wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.FONTWEIGHT_NORMAL, False, "Courier", wx.FONTENCODING_SYSTEM)
        self.fonts = [] # 0:smll, 1:default, larger fonts as index gets larger 
        for i in range(5):
            self.fonts.append( wx.Font(fontSz, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, faceName=_font) )
            fontSz += 2
        dc = wx.WindowDC(self)
        dc.SetFont(self.fonts[1])

        ### set up panels
        ip_sz=(270,w_size[1]-40); ip_pos=(0,40); 
        sp_sz=(670,w_size[1]-60); sp_pos=(w_size[0]-sp_sz[0],40) 
        mp_sz=(w_size[0]-ip_sz[0]-sp_sz[0],w_size[1]-80); mp_pos=(ip_sz[0],80)
        self.ip_sz=ip_sz; self.mp_sz=mp_sz; self.sp_sz=sp_sz
        title = wx.StaticText(self, -1, "Item list", pos=(ip_pos[0],3))
        title.SetFont(self.fonts[4])
        title.SetForegroundColour('#DDDDDD')
        self.iPanel = ItemPanel(self, pos=ip_pos, size=ip_sz)
        title = wx.StaticText(self, -1, "Set up items in script", pos=(mp_pos[0],3))
        title.SetFont(self.fonts[4])
        title.SetForegroundColour('#DDDDDD')
        sTxt = wx.StaticText(self, -1, " - Change a choice box item with mouse, or",
                pos=(mp_pos[0],title.GetPosition()[1]+title.GetSize()[1]+2))
        sTxt.SetFont(self.fonts[2])
        sTxt.SetForegroundColour('#DDDDDD')
        sTxt = wx.StaticText(self, -1, " type a text in a text-box and press Return-key.",
                pos=(mp_pos[0],sTxt.GetPosition()[1]+sTxt.GetSize()[1]+2))
        sTxt.SetFont(self.fonts[2])
        sTxt.SetForegroundColour('#DDDDDD')
        self.mPanel = MainPanel(self, pos=mp_pos, size=mp_sz)
        title = wx.StaticText(self, -1, "Result script", pos=(sp_pos[0],3))
        title.SetFont(self.fonts[4])
        title.SetForegroundColour('#DDDDDD')
        btn = wx.Button(self, -1, "", name="show_script_btn", pos=(sp_pos[0]+title.GetSize()[0]+5,0), size=(25,20))
        set_img_for_btn(path.join(self.e_gui_path, "input/img_script_show.png"), btn)
        btn.Bind(wx.EVT_LEFT_UP, self.onShowScript)
        self.sPanel = ScriptPanel(self, pos=sp_pos, size=sp_sz)

        ### Connecting key-inputs with some functions
        exit_BtnID = wx.NewIdRef(count=1)
        #esc_BtnID = wx.NewIdRef(count=1)
        self.Bind(wx.EVT_MENU, self.quit, id = exit_BtnID)
        #self.Bind(wx.EVT_MENU, self.onESC, id = esc_BtnID)
        accel_tbl = wx.AcceleratorTable([ (wx.ACCEL_CMD,  ord('Q'), exit_BtnID) ]) 
                                          #(wx.ACCEL_NORMAL, wx.WXK_ESCAPE, esc_BtnID) ])
        self.SetAcceleratorTable(accel_tbl)

        #msg = "Click OK button (or press ENTER key) to start the app.\nDialog for asking a series of questions to determine stimuli paths/correct stimulus/etc will appear.\n\nIf stimuli for trials should be specifically ordered, stimuli filenames should follow specific rules.\nIf you are not sure about it, cancel the dialog box and check the rules by pressing info(i) button next to 'setup_stimuli' in the left panel."
        #show_msg(msg, size=(400, 280))
        wx.CallLater(1, self.mPanel.setUpStimuli, None)

    #------------------------------------------------
    ''' 
    def onSizing(self, event):
        if DEBUGGING: print('EGUIFrame.onSizing()')
        cSz = self.GetSize()
        wd = cSz[0] - self.w_sz[0]
        hd = cSz[1] - self.w_sz[1]
        if wd == 0 and hd == 0: return

        ### update the window size
        w = self.w_sz[0]; h = self.w_sz[1]
        if wd > 0: w += wd
        if hd > 0: h += hd
        self.SetSize((w,h))

        ### update the script panel size
        w = self.sp_sz[0]; h = self.sp_sz[1]
        if wd > 0: w += wd
        if hd > 0: h += hd
        self.sPanel.SetSize((w,h))

        ### update the script editor size
        w = self.sPanel.stc_sz[0]; h = self.sPanel.stc_sz[1]
        if wd > 0: w += wd
        if hd > 0:
            h += hd
            ### update positions of other widgets
            for wid in self.sPanel.widgets:
                _p = wid.GetPosition()
                wid.SetPosition((_p[0], self.sPanel.stc.GetPosition()[1]+h+2))
        self.sPanel.stc.SetSize((w,h)) # update the size of styledTextCtrl
    '''         
    #------------------------------------------------
   
    def onShowScript(self, event):
        if DEBUGGING: print('EGUIFrame.onShowScript()')
        event.Skip()
        self.flag_script_visible = not self.flag_script_visible
        btn = event.GetEventObject()
        if self.flag_script_visible == True:
            self.sPanel.stc.Show() # hide script
            for w in self.sPanel.widgets[0]: w.Show() # hide script related widgets
            set_img_for_btn(path.join(self.e_gui_path, "input/img_script_hide.png"), btn) 
        else:
            self.sPanel.stc.Hide() # show script
            for w in self.sPanel.widgets[0]: w.Hide() # show script related widgets
            set_img_for_btn(path.join(self.e_gui_path, "input/img_script_show.png"), btn) 
        ### show/hide marker buttons in main panel
        for item in self.mPanel.items.keys():
            if item in self.iPanel.choice_items: valWid = wx.FindWindowByName( item+"_cho", self.mPanel ) 
            else: valWid = wx.FindWindowByName( item+"_txt", self.mPanel )
            if valWid == None or valWid.IsShown() == False: continue
            btn = wx.FindWindowByName( item+"_marker_btn", self.mPanel )
            if self.flag_script_visible == True: btn.Show()
            else: btn.Hide()
        self.mPanel.gbs.Layout()
        self.sPanel.gbs.Layout()
    
    #------------------------------------------------
    
    def quit(self, event):
        if DEBUGGING: print('EGUIFrame.quit()')
        self.Close()

# ===========================================================

class EGUI_App(wx.App):
    def OnInit(self):
        self.frame = EGUIFrame()
        self.frame.Show()
        self.SetTopWindow(self.frame)
        return True

#====================================================

CWD = getcwd() # current working directory
if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == '-w': GNU_notice(1)
        elif sys.argv[1] == '-c': GNU_notice(2)
    else:
        GNU_notice(0)
        app = EGUI_App(redirect = False)
        app.MainLoop()


