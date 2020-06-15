# coding: UTF-8

'''
Experimenter_GUI: main_panel
- Middle panel to show used items in the current setup 

----------------------------------------------------------------------
Copyright (C) 2016 Jinook Oh, W. Tecumseh Fitch 
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
'''


import re
from os import getcwd, path
from glob import glob
from time import time
from copy import copy
from operator import itemgetter
from random import shuffle
from math import sqrt

import wx
import wx.lib.scrolledpanel as sPanel
from wx.lib.wordwrap import wordwrap

from modules import setup_stim_dlg
from modules.fFuncNClasses import load_img, show_msg, set_img_for_btn, convert_idx_to_ordinal

DEBUGGING = False

#====================================================

class MainPanel(sPanel.ScrolledPanel):
    def __init__(self, parent, pos, size):
        self.parent = parent
        if DEBUGGING: print('MainPanel.__init__()')
        self.sz = size
        
        self.items = {} # currently added item names and its values in this panel

        sPanel.ScrolledPanel.__init__(self, parent, -1, pos=pos, size=(size[0]+5, size[1]))
        
        self.df = self.parent.fonts[2]
        self.init_items() 
        self.SetupScrolling()

    #------------------------------------------------

    def init_items(self):
        if DEBUGGING: print('MainPanel.init_items()')
        bw = 2
        btnSz = (30, -1)
        self.gbs = wx.GridBagSizer(0,0)
        row = -1 

        def _func(item, row, val_widget_type, item_list_idx, flag_hide):
            col = 0
            ### StaticText of item name
            wn = "%s_sTxt"%(item)
            if len(item) > 18: _txt = item[:18] + ".."
            else: _txt = item
            sTxt = wx.StaticText(self, -1, _txt, name=wn)
            sTxt.SetFont(self.parent.fonts[1]) # small font
            sTxt.SetForegroundColour('#DDDDDD')
            self.gbs.Add(sTxt, pos=(row,col), flag=wx.ALIGN_CENTER_VERTICAL|wx.ALL, border=bw)
            if flag_hide == True: sTxt.Hide()
            vw = 165 # width of a widget (TextCtrl or Choice) for item value
            if item == 'setup_stimuli':
                ### image button to set up stimuli paths and other related information 
                wn = "%s_btn"%(item)
                btn = wx.Button(self, -1, label="", name=wn, size=btnSz)
                set_img_for_btn(path.join(self.parent.e_gui_path, "input/img_setup.png"), btn)
                btn.Bind(wx.EVT_LEFT_UP, self.setUpStimuli)
                col += 1
                self.gbs.Add(btn, pos=(row,col), flag=wx.ALIGN_CENTER_VERTICAL|wx.ALL, border=bw)
                if flag_hide == True: btn.Hide()
                vw -= 30
            ### delete button for optional items (item_list_idx == 1)
            if item_list_idx == 1:
                wn = "%s_del_btn"%(item)
                btn = wx.Button(self, -1, "", name=wn, size=btnSz)
                set_img_for_btn(path.join(self.parent.e_gui_path, "input/img_delete.png"), btn)
                btn.Bind(wx.EVT_LEFT_UP, self.onDelItem)
                col += 1
                self.gbs.Add(btn, pos=(row,col), flag=wx.ALIGN_CENTER_VERTICAL|wx.ALL, border=bw)
                if flag_hide == True: btn.Hide()
                vw -= 30
            ### widget for a value of the item
            iData = self.parent.iPanel.item_info[item_list_idx][item] 
            if val_widget_type == "choice":
                wn = "%s_cho"%(item)
                valWid = wx.Choice(self, -1, choices = [str(x) for x in iData["values"]], 
                                             name = wn,
                                             size = (vw,-1))
                valWid.Bind(wx.EVT_CHOICE, self.chkChangedValue)
                idx = valWid.FindString( str(iData["value"]) )
                if idx != wx.NOT_FOUND: valWid.SetSelection(idx)
            else:
                wn = "%s_txt"%(item)
                valWid = wx.TextCtrl(self, -1, value = str(iData["value"]), 
                                               name = wn,
                                               size = (vw,-1),
                                               style = wx.TE_LEFT|wx.TE_PROCESS_ENTER)
                valWid.Bind(wx.EVT_TEXT_ENTER, self.chkChangedValue)
            valWid.SetFont(self.df)
            col += 1
            if item == 'setup_stimuli' or item_list_idx == 1:
                self.gbs.Add(valWid, pos=(row,col), flag=wx.ALIGN_CENTER_VERTICAL|wx.ALL, border=bw)
            else:
                self.gbs.Add(valWid, pos=(row,col), span=(1,2), flag=wx.ALIGN_CENTER_VERTICAL|wx.ALL, border=bw)
                col += 1
            if flag_hide == True:
                valWid.Hide()
            else:
                self.items[item] = self.getItemVal(item)[1] # store item and its value
            if item in ['number_of_trials', 'number_of_stimuli_per_trial', 'setup_stimuli', 's_type']:
                valWid.SetEditable(False)
                valWid.SetBackgroundColour('#999999')

            ### marker button
            wn = "%s_marker_btn"%(item)
            btn = wx.Button(self, -1, "", name=wn, size=btnSz)
            set_img_for_btn(path.join(self.parent.e_gui_path, "input/img_marker_next.png"), btn)
            btn.Bind(wx.EVT_LEFT_UP, self.onDisplayingMarker)
            btn.Hide() # script is not visible by default, therefore marker (for script) buttons are also hidden by default
            col += 1
            self.gbs.Add(btn, pos=(row,col), flag=wx.ALIGN_CENTER_VERTICAL|wx.ALL, border=bw)
            if flag_hide == True or self.parent.flag_script_visible == False: btn.Hide()
            
            col += 1
            self.gbs.Add(wx.StaticText(self, -1, "", size=(1,1)), pos=(row,col), flag=wx.EXPAND|wx.ALL, border=bw)

        for i in range(len(self.parent.iPanel.bItemsList)):
            for item in self.parent.iPanel.bItemsList[i]:
                if item in self.parent.iPanel.choice_items: val_widget_type = "choice"
                else: val_widget_type = "text"
                row += 1
                if i == 0: flag_hide = False
                else: flag_hide = True
                _func(item, row, val_widget_type, 0, flag_hide)
            if i == 0:
                row += 1
                self.sh_btn = wx.Button(self, -1, "", name="showHide_btn", size=(self.sz[0]-10,-1))
                set_img_for_btn(path.join(self.parent.e_gui_path, "input/img_arrow_down.png"), self.sh_btn)
                self.sh_btn.Bind(wx.EVT_LEFT_UP, self.onShowHide)
                self.flag_bItemsList1_shown = False
                self.gbs.Add(self.sh_btn, pos=(row,0), span=(1,4), flag=wx.EXPAND|wx.ALL, border=5)
        for i in range(2,0,-1):
            for item in sorted(self.parent.iPanel.item_info[i].keys()):
                if item in self.parent.iPanel.choice_items: val_widget_type = "choice"
                else: val_widget_type = "text"
                row += 1
                _func(item, row, val_widget_type, i, True)
            if i == 2:
                row += 1
                self.gbs.Add(wx.StaticLine(self, -1, size=(self.sz[0]-10,-1)), pos=(row,0), span=(1,4), flag=wx.EXPAND|wx.ALL, border=5)

        self.SetSizer(self.gbs)
        self.gbs.Layout()
        self.Layout()
        self.SetupScrolling()

    #------------------------------------------------
    
    def onShowHide(self, event):
        ''' show/hide basic items
        '''
        if DEBUGGING: print('MainPanel.onShowHide()')
        event.Skip()
        def _func(item):
        # show/hide item title and its help button
            _w = []
            _w.append( wx.FindWindowByName( "%s_sTxt"%(item), self ))
            if item == 'setup_stimuli': _w.append( wx.FindWindowByName( "%s_btn"%(item), self ) )
            if item in self.parent.iPanel.choice_items: _w.append( wx.FindWindowByName("%s_cho"%(item), self) )
            else: _w.append( wx.FindWindowByName("%s_txt"%(item), self) )
            if self.parent.flag_script_visible == True: _w.append( wx.FindWindowByName( "%s_marker_btn"%(item), self ) )
            if self.flag_bItemsList1_shown == False:
                for widget in _w:
                    widget.Show()
                    self.items[item] = self.getItemVal(item)[1] # store item and its value
            elif self.flag_bItemsList1_shown == True:
                for widget in _w:
                    widget.Hide()
                    __ = self.items.pop(item, None) # remove the item from the current item dictionary
        for item in self.parent.iPanel.bItemsList[1]: # items hidden by default among basic items (item_info[0])
            _func(item) 
        for item in sorted(self.parent.iPanel.item_info[2].keys()): # items automatically added when stimuli path is selected
            _func(item)
        
        ### change arrow button image and flag value
        if self.flag_bItemsList1_shown == False:
            self.flag_bItemsList1_shown = True
            set_img_for_btn(path.join(self.parent.e_gui_path, "input/img_arrow_up.png"), self.sh_btn)
        elif self.flag_bItemsList1_shown == True:
            self.flag_bItemsList1_shown = False
            set_img_for_btn(path.join(self.parent.e_gui_path, "input/img_arrow_down.png"), self.sh_btn)
        
        self.gbs.Layout()
        #self.Layout()
        self.SetupScrolling()

    #------------------------------------------------
    
    def add_del_item(self, item, item_list_idx=1, flag_del=False):
        if DEBUGGING: print('MainPanel.add_del_item()')

        _w = []
        _w.append( wx.FindWindowByName( "%s_sTxt"%(item), self ))
        if item == 'setup_stimuli': _w.append( wx.FindWindowByName("%s_btn"%(item), self) )
        if item_list_idx == 1: _w.append( wx.FindWindowByName("%s_del_btn"%(item), self) )
        if item in self.parent.iPanel.choice_items: _w.append( wx.FindWindowByName("%s_cho"%(item), self) )
        else: _w.append( wx.FindWindowByName("%s_txt"%(item), self) )
        if self.parent.flag_script_visible == True: _w.append( wx.FindWindowByName( "%s_marker_btn"%(item), self ) )
        for widget in _w:
            if flag_del == True:
                widget.Hide()
                __ = self.items.pop(item, None) # remove the item from the current item dictionary
            else:
                widget.Show()
                self.items[item] = self.getItemVal(item)[1] # store item and its value
        self.gbs.Layout()
        self.Layout()
        self.SetupScrolling()
        
        ### add script for the item
        if item == 'arduino':
            self.addItemScript(item) # note: when new script is added, markers will be added to the new lines
        else:
            self.parent.sPanel.dispMarkers(item)
        #self.chkChangedValue(valWid.GetName())

    #------------------------------------------------
    
    def addItemScript(self, item, additional_info=None):
        if DEBUGGING: print('MainPanel.addItemScript()')
        txt = self.parent.sPanel.stc.GetText()
        idx = txt.find("#[flag:%s]"%item)
        if idx != -1: # the flag was found (the script already exists)
            return
        if additional_info == None: f = open( path.join(self.parent.e_gui_path, 'scripts/%s.py'%(item)), 'r' )
        else: f = open( path.join(self.parent.e_gui_path, 'scripts/%s_%s.py'%(item, additional_info)), 'r' )
        txt = f.read()
        f.close()
        self.parent.sPanel.addItemScript(txt)
    
    #------------------------------------------------

    def onDelItem(self, event):
        '''Deleting item here means deleting from screen (hiding)
        '''
        if DEBUGGING: print('MainPanel.onDelItem()')
        if type(event) == str:
            obj_name = event
            obj = wx.FindWindowByName( obj_name, self )
        else:
            event.Skip()
            obj = event.GetEventObject()
            obj_name = obj.GetName()
        item = obj_name.replace("_del_btn", "")
        __ = self.items.pop(item, None) # remove the item from the current item dictionary

        self.add_del_item(item, item_list_idx=1, flag_del=True)
        
        ### (when applicable) remove item script from the script panel
        if item == 'arduino': self.removeItemScript(item)
            
    #------------------------------------------------
    
    def removeItemScript(self, item):
        if DEBUGGING: print('MainPanel.removeItemScript()')

        if item == 'movie':
            scriptTxt = self.parent.sPanel.stc.GetText()
            idx_wxMedia = scriptTxt.find('#[flag:wx.media')
            idx_vlc = scriptTxt.find('#[flag:vlc')
            if idx_wxMedia != -1:
                f = open( path.join(self.parent.e_gui_path, 'scripts/movie_wx.media.py'), 'r' )
                txt = f.read()
                f.close()
                self.parent.sPanel.removeItemScript(txt)
            if idx_vlc != -1: 
                f = open( path.join(self.parent.e_gui_path, 'scripts/movie_vlc.py'), 'r' )
                txt = f.read()
                f.close()
                self.parent.sPanel.removeItemScript(txt)
        else:
            f = open( path.join(self.parent.e_gui_path, 'scripts/%s.py'%(item)), 'r' )
            txt = f.read()
            f.close()
            self.parent.sPanel.removeItemScript(txt)
    
    #------------------------------------------------
    
    def onDisplayingMarker(self, event):
        if DEBUGGING: print('MainPanel.onDisplayingMarker()')
        event.Skip()
        obj = event.GetEventObject()
        obj_name = obj.GetName()
        item = obj_name.replace("_marker_btn", "")
        self.parent.sPanel.dispMarkers(item)
    
    #------------------------------------------------
    
    def chkChangedValue(self, event):
        if DEBUGGING: print('MainPanel.chkChangedValue()')
        '''Check & process (such as showing error message, updating the script, etc) the entered value
        When the value was changed by SetValue by code, 'event' will be name of the object(widget)
        '''
        if type(event) == str:
            obj_name = event
            obj = wx.FindWindowByName( obj_name, self )
        else:
            event.Skip()
            obj = event.GetEventObject()
            obj_name = obj.GetName()
        item = obj_name[:-4] 
        
        if '_txt' in obj_name:
            vType, val = self.getItemVal(item)
            key_found_in_item_info = False
            for ii in range(len(self.parent.iPanel.item_info)):
                iInfo = self.parent.iPanel.item_info[ii]
                if item in iInfo.keys():
                    key_found_in_item_info = True
                    break 
            
            err_msg = ""

            ### check whether the entered value is in the range of values, where it's applicable
            if key_found_in_item_info == True and iInfo[item]["values"] != None:
                rng = iInfo[item]["values"] # range of values
                err_msg = ""
                _val = None
                try: _val = int(val)
                except: pass
                if _val == None: err_msg += "This value should be an integer.\n"
                else:
                    if rng[0] > _val or rng[1] < _val:
                        err_msg += "This value should range between %i and %i\n"%(rng[0], rng[1]) 
            
            if item in ['clickable', 'rect']:
                stObj = wx.FindWindowByName( "s_type_txt", self )
                st = stObj.GetValue().replace(' ','').strip("[]").replace('"','').replace("'","").split(",") # stimulus types
            if item == 'clickable':
            ### check values of clickable
                val = re.sub('(?i)' + re.escape('true'), 'True', val) # change 'true' with lower or upper case on any letter to 'True' for boolean value
                val = re.sub('(?i)' + re.escape('false'), 'False', val) # change 'false' with lower or upper case on any letter to 'False' for boolean value
                obj.SetValue(val)
                _val = val.strip().strip("[]").split(",")
                ur = self.getItemVal("user_response")[1]
                for i in range(len(_val)):
                    if _val[i].strip().lower() == "true" and ur != 'mouse_click':
                        err_msg += "Item index %i in 'clickable': user_response is not mouse_click.\n"%(i)
                    if _val[i].strip().lower() == "true" and st[i].strip() == "snd":
                        err_msg += "Item index %i in 'clickable': 'snd' stimulus can't be clicked.\n"%(i)
            elif item == 'present_time':
            ### check values of 'present_time'
                _val = val.replace(" ","").strip("[]").split("],[") # split by stimulus
                for i in range(len(_val)):
                    _v = _val[i].split(",") # split the start-time and end-time
                    if len(_v) != 2: err_msg += "Item index %i in 'present_time': Length of an inside list of 'present_time' should be two, start-time & end-time.\n"%(i)
                    else:
                        for j in range(2):
                            try: _v[j] = int(_v[j])
                            except: pass
                        if type(_v[0]) != int or type(_v[1]) != int:
                            err_msg += "Item index %i in 'present_time': Items in 'present_time' should be integers (time in milliseconds).\n"%(i)
                        else:
                            if _v[0] < 1:
                                err_msg += "Item index %i in 'present_time': Start-time, (first item in the inner list), should be one at minimum.\n"%(i)
                            if _v[1] != -1 and _v[1] <= _v[0]: # End-time should be either -1 or larger than the start-time.
                                err_msg += "Item index %i in 'present_time': End-time, (second item in the inner list), should be larger than the start-time.\n"%(i)
            elif item == 'rect':
            ### check values of 'rect'
                val = re.sub('(?i)' + re.escape('none'), 'None', val) # change 'none' with lower or upper case on any letter to 'None'
                obj.SetValue(val)
                _val = val.replace(" ","").strip("[]").split("],[") # split by stimulus
                for i in range(len(_val)):
                    _v = _val[i].split(",") # split rect info (x,y,w,h) 
                    if len(_v) != 4:
                        err_msg += "Item index %i in 'rect': Length of an inside list of 'rect' should be four (x,y,w,h).\n"%(i)
                        continue
                    if st[i].strip() == 'snd':
                        if _val[i] != "None,None,None,None":
                            err_msg += "Item index %i in 'rect': 'rect' is not applicable for 'snd' stimulus. It should be None,None,None,None.\n"%(i)
                            continue
                    else:
                        try:
                            _v[0]=float(_v[0]); _v[1]=float(_v[1])
                            _v[2]=int(_v[2]); _v[3]=int(_v[3])
                        except:
                            pass
                        for j in range(len(_v)):
                            if j < 2 and type(_v[j]) != float:
                                err_msg += "x & y coordiantes in 'rect' should be float numbers.\nCheck more info by clicking (i) button next to 'rect' in the lfet panel.\n"
                            elif j >= 2 and type(_v[j]) != int:
                                err_msg += "width & height in 'rect' should be integers.\nCheck more info by clicking (i) button next to 'rect' in the lfet panel.\n"
                            else:
                                if j < 2: # x, y
                                    if _v[j] < 0 or _v[j] > 1: # x, y should between 0.0 and 1.0
                                        err_msg += "x & y in 'rect' should be between 0.0 and 1.0.\nCheck more info by clicking (i) button next to 'rect' in the left panel.\n"
                                else: # w, h
                                    if _v[j] != -1 and _v[j] <= 0: # w, h should be -1 or larger than zero 
                                        err_msg += "width & height in 'rect' should be larger than zero.\nCheck more info by clicking (i) button next to 'rect' in the left panel.\n"
                                if err_msg != "": break

            if err_msg != "":
                show_msg(err_msg, size=(700,350))
                obj.SetValue( str(self.items[item]) ) # return the value to the previously stored value
                return
        
        elif '_cho' in obj_name:
            vType, val = self.getItemVal(item)
            if item == 'feedback': 
                if val in ['Auditory', 'Both']:
                    self.addItemScript('audio_output')
                    self.items['audio_output'] = "added"
                else:
                    self.removeItemScript('audio_output')
                    __ = self.items.pop('audio_output', None)

            elif item == 'user_response':
                obj = wx.FindWindowByName("clickable_txt")
                if obj != None:
                    if val == 'mouse_click':
                        obj.SetEditable(True)
                        obj.SetBackgroundColour('#ffffff')
                    else:
                        ### if user_response is not mouse_click, clickable should be all False
                        ns = int(self.getItemVal("number_of_stimuli_per_trial")[1])
                        _v = str([False for x in range(ns)])
                        self.setItemVal("clickable", _v)
                        obj.SetEditable(False)
                        obj.SetBackgroundColour('#999999')
        
        self.parent.sPanel.updateItemVal(item)
        self.items[item] = val # store item's value

        if item == 'user_response' and val == 'key_stroke':
            msg = "For key_stroke to work, some programming is necessary.\n\nFirst, add desired keys to key_bindings.\ne.g.) To process key stroke of 'A' and 'L', add 'NONE+A, NONE+L' in key_bindings.\n\nNext, you should program how to deal with correct user response. The user response will be 'A' or 'L' in case of the above example. Which will be correct in which trial is determined in init_expmt function.\nMarkers for key_stroke related lines in the script will be shown after you close this window."
            show_msg(msg, size=(500,300))
            self.parent.sPanel.dispMarkers("key_stroke")
    
    #------------------------------------------------

    def getItemVal(self, item):
        ''' find a value object by the item name,
        return the found value's type and the value itself
        '''
        if DEBUGGING: print('MainPanel.getItemVal()')
        obj = wx.FindWindowByName( item+"_txt", self )
        if obj != None: value = obj.GetValue().strip()
        else:
            obj = wx.FindWindowByName( item+"_cho", self )
            value = obj.GetString( obj.GetSelection() )
        tmp = None
        try: tmp = int(value)
        except: pass
        if tmp != None: vType = 'i' # integer
        else:
            if value in ['True', 'False']: vType = 'b' # boolean
            elif len(value) > 1 and value[0] == '[' and value[-1] == ']': vType = 'l' # list
            else: vType = 't' # text
        return vType, value

    #------------------------------------------------
    
    def setItemVal(self, item, val):
        ''' find a value object by the item name,
        set the value with given one
        '''
        if DEBUGGING: print('MainPanel.setItemVal()')
        val = str(val)
        obj_name = item + "_txt"
        obj = wx.FindWindowByName(obj_name, self)
        if obj == None: # it's a wx.Choice widget
            obj_name = obj_name.replace("_txt", "_cho")
            obj = wx.FindWindowByName(obj_name, self )
            idx = obj.FindString(val)
            if idx != wx.NOT_FOUND: obj.SetSelection(idx) # update the value
        else: # it's a TextCtrl widget
            obj.SetValue(val) # update the value
        self.chkChangedValue(obj_name) # check the updated value
    
    #------------------------------------------------

    def setUpStimuli(self, event):
        ''' Function to ask stimuli path(s) and related information, then process the info 
        '''
        if DEBUGGING: print('MainPanel.setUpStimuli()')
        if event != None: event.Skip()
       
        dlg = setup_stim_dlg.SetupStimuliDialog(self)
        result = dlg.ShowModal()
        if result == wx.ID_OK: sInfo = dlg.GetValues()
        elif result == wx.ID_CANCEL: return 
        dlg.Destroy() 

        stim_fp = []
        for ti in range(sInfo["number_of_trials"]):
            stim_fp.append([])
            for paths_of_es in sInfo["paths_of_es"]:
                stim_fp[-1].append( paths_of_es[ti] )
            for paths_of_rs in sInfo["paths_of_rs"]:
                stim_fp[-1].append( paths_of_rs[ti] )
        self.setItemVal("setup_stimuli", str(stim_fp))

        self.setItemVal("number_of_trials", sInfo["number_of_trials"])
        nes = sInfo["number_of_experimental_stimuli"]
        nrs = sInfo["number_of_response_stimuli"]
        nspt = nes + nrs
        self.setItemVal("number_of_stimuli_per_trial", nspt)
        stim_types = sInfo["types_of_es"] + sInfo["types_of_rs"]
        _idx = list(range(nspt))
        for si in range(nspt):
            if stim_types[si] == 'snd':
                _idx[si] = None # exclude sound stimulus from 
                  # randomized stimuli index
        while None in _idx: _idx.remove(None)
        self.setItemVal("randomize_stimuli_idx", str(_idx))

        ### add widgets for stimulus parameters 
        self.add_del_item("s_type", item_list_idx=2)
        self.setItemVal("s_type", str(stim_types)) 
        self.add_del_item("clickable", item_list_idx=2)
        ur = self.getItemVal("user_response")[1]
        txt = "["
        for st in stim_types:
            if st in ['snd', 'mov']: txt += "False, " # sound stimulus won't be clicked; 'mov' is also False by default. VLC object can be clicked, but not wx.media.MediaCtrl object
            else:
                if ur in ['mouse_click', 'slider']: txt += "True, "
                else: txt += "False, "
        txt = txt.rstrip(", ") + "]"
        self.setItemVal("clickable", txt)
        if ur != 'mouse_click':
            obj = wx.FindWindowByName("clickable_txt")
            obj.SetEditable(False)
            obj.SetBackgroundColour('#999999')
        self.add_del_item("present_time", item_list_idx=2)
        txt = "["
        for si in range(nspt): txt += "[1, -1], "
        txt = txt.rstrip(", ") + "]"
        self.setItemVal("present_time", txt)
        self.add_del_item("rect", item_list_idx=2)
        txt = "["
        rects = sInfo["rects_of_es"] + sInfo["rects_of_rs"]
        for si in range(nspt):
            if stim_types[si] == 'snd': txt += "[None,None,None,None], "
            else: txt += "%s, "%(rects[si])
        txt = txt.rstrip(", ") + "]"
        self.setItemVal("rect", txt)

        if 'snd' in stim_types: # if there's sound stimulus 
            if not "audio_output" in self.items.keys():
            # audio_output is not already included in script
                self.addItemScript('audio_output')
                self.items['audio_output'] = "added"
        else: # there's no sound stimulus
            vType, val = self.getItemVal("feedback")
            if val in ['Visual', 'None']: # feedback doesn't need audio output
                self.removeItemScript('audio_output')
                __ = self.items.pop('audio_output', None)

        if 'mov' in stim_types: # if there's movie stimulus among stimuli
            if "movie" in self.items.keys():
            # if there's already a movie script in the current setup 
                ### removie it first (because there are two different movie scripts with wx.media and vlc)
                self.removeItemScript('movie')
                __ = self.items.pop('movie', None)
            ### add script
            self.addItemScript('movie', sInfo["movie_module"]) # wx.media or VLC
            self.items['movie'] = "added"
        else: # no movie stimulus
            self.removeItemScript('movie')
            __ = self.items.pop('movie', None)

        if 'slider' in stim_types: # if there's a slider
            self.addItemScript('slider')
            self.items['slider'] = "added"
        else: # no slider
            self.removeItemScript('slider')
            __ = self.items.pop('slider', None)

        self.chkChangedValue("setup_stimuli_txt") # show changed setup_stimuli text

    #------------------------------------------------

#====================================================


if __name__ == "__main__": pass


