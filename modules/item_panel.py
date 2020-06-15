# coding: UTF-8

'''
Experimenter_GUI: item_panel
- Left side panel to show item list 

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

from os import path
from copy import copy

import wx
import wx.lib.scrolledpanel as sPanel
from modules.fFuncNClasses import show_msg, set_img_for_btn 

DEBUGGING = False

#====================================================

class ItemPanel(sPanel.ScrolledPanel):
    def __init__(self, parent, pos, size): 
        self.parent = parent
        if DEBUGGING: print('ItemPanel.__init__()')
        sPanel.ScrolledPanel.__init__(self, parent, -1, pos=pos, size=size)

        # basic item list is separated into two groups. [0] = basic; displayed by default, [1] = displayed only when user presses a button
        self.bItemsList = [
                              [
                                  'setup_stimuli', 'user_response', 'inter_trial_interval',
                                  'trial_timeout', 'randomize_trials', 'randomize_stimuli'
                              ],
                              [
                                  'feedback', 'number_of_trials', 'number_of_stimuli_per_trial',
                                  'key_bindings', 'randomize_stimuli_idx', 'correction_trial',
                                  'trigger', 'train_or_test', 'reaction_time_start', 
                                  'user_response_start'
                              ]
                          ]

        self.choice_items = ['user_response', 'feedback', 'randomize_trials', 
                             'randomize_stimuli', 'correction_trial', 
                             'trigger', 'train_or_test'] # items, whose values will be displayed with wx.Choice widget

        self.item_info = [] 

        ### basic items (these items are necessary for running experimenter script) 
        # it will have item name as key, its value will be another dictionary.
        # the dictionary will have 'values', 'value'(default value) and 'desc'(description)
        # For items with value which will be displayed with wx.Choice, 'values' is a list of choices.
        # For items with value which will be displayed with wx.TextCtrl, 'values' is a list, which has minimum and maximum integer value.
        # For items with wx.TextCtrl and arbitrary string value, 'values' should be None.
        self.item_info.append( dict( number_of_trials = dict(values=[1, 10000], 
                                                        value=1, 
                                                        desc="Number of trials.\nThis will be automatically calculated when setup_stimuli is done."),
                           number_of_stimuli_per_trial = dict(values=[1, 10000], 
                                                              value=1, 
                                                              desc="Number of stimuli per trial.\nThis will be automatically calculated when setup_stimuli is done."),
                           setup_stimuli = dict(values=None, 
                                               value="",
                                               desc="By clicking 'setup' (gear shape) button, you will be asked a series of questions related to stimuli path(s) and other information.\n\nStimuli can be divided into several folders or all in one folder.\nIf it is divided into several folders, each folder means a collection of a stimulus file for each trial.\nIf all stimuli files are located in one foler, stimuli filename should have three parts divided by underbar '_'.\nThe 1st part is any string for user's convenience to recognize the file, the 2nd part is a trial index (starting from zero), the 3rd part is a stimulus index (also, starting from zero).\n\nIf filename has '_c' after the stimulus index part, the filename will be treated as a correct response string (When a stimulus is clicked, the filename of the clicked stimulus will be sent as a response string.)\ne.g.) when there are three stimuli, two images and one sound in each trial.\ns_000_00_c.png, s_000_01.png, s_000_02.wav, s_001_00.png, s_001_01_c.png, s_001_02.wav, ...\n\nIf filename has '_c-' at the end, string after '_c-' will be treated as a correct response string.\ne.g.) When there are one image and two text (yes/no), each image stimulus' filename can be as following.\nmyStimulus00_c-yes.png, myStimulus01_c-no.png, myStimulus02_c-no.png, ...\n\nIf neither of them ('_c', or '_c-XXX') is present in filename, the trial will be treated as a trial with no correct response (threfore, no feedback).\n"),
                           user_response = dict(values=['mouse_click', 'key_stroke', 'none'],
                                                value='mouse_click', 
                                                desc="'mouse_click', 'key_stroke', 'none' is available.\n'mouse_click' is used for binding click event to image, text or slider.\n'key_bindings' shoud be set up for 'key_stroke'.\nIf this is 'none' trial finishes when the last stimulus was presentation time is up."),
                           key_bindings = dict(values=None,
                                               value="['CTRL+Q', 'CTRL+S', 'CTRL+L']",
                                               desc="Should be a python list with string elements in format of 'Modifier key+Target key'\ne.g.) 'CTRL+Q', 'SHIFT+A', 'ALT+C', 'NONE+K', 'NONE+LEFT', 'NONE+F1'.\n\nDefault setup : \nCTRL+Q - quit\nCTRL+S - save session info (result file path, trial_cnt, and trial_idx)\nCTRL_L - load the saved session"),
                           feedback = dict(values=['Visual', 'Auditory', 'Both', 'None'], 
                                           value='Visual', 
                                           desc="Visual, Auditory, Both, or None"),
                           inter_trial_interval = dict(values=[1, 60001], 
                                                       value=1000,  
                                                       desc="Inter-trial-interval in milliseconds."),
                           trial_timeout = dict(values=[-1, 60001], 
                                                value=-1, 
                                                desc="Trial timeout time in milliseconds. This time measure will start after 'reaction_time_start'.\n-1 means there's no timeout."),
                           randomize_trials = dict(values=[True, False], 
                                                   value=True, 
                                                   desc="Randomizing trials sequence."),
                           randomize_stimuli = dict(values=[True, False], 
                                                    value=False, 
                                                    desc="Randomzing positions and presenting time."),
                           randomize_stimuli_idx = dict(values=None,
                                                        value=[0],
                                                        desc="Normally all stimuli will be randomized. But this list of indices does not include all stimuli indices, stimuli only with these indices will be randomized, while other stimuli will be fixed.\nWhen images and sounds are both used, the sound should be excluded from this index list, because image randomization uses positions of other stimuli, while sound has no positon."),
                           correction_trial = dict(values=[True, False], 
                                                   value=False, 
                                                   desc="The same trial happens repeatedly until correct response."),
                           trigger = dict(values=[True, False], 
                                          value=False, 
                                          desc="Trial will start when the trigger image (input/trigger.png) is clicked."),
                           train_or_test = dict(values=[True, False], 
                                                value=False, 
                                                desc="Twenty percent of trials will be assigned to 'test' trials, others will be 'training' trials.\nTrials will be randomized regardless of 'randomize_stimuli'.\nThere will be no feedback for test trials.\nThe first trial will be a training trial.\nIf one trial is a test trial, the next one will be a training.\nThese rules and the percentage of test trial can be changed by reprogramming 'make_trial_idx' function in 'start_session' function of 'Experimenter' class in the produced script file."),
                           reaction_time_start = dict(values=[0, 360000],
                                                      value=0, 
                                                      desc="Time (in milliseconds) to start reaction time measurement.\nReaction time measurement starts after user_response_start. Zero means that reaction time measurement starts at the same time with user_response_start. Minus value is not allowed."),
                           user_response_start = dict(values=[-360000, 360000],
                                                      value=0, 
                                                      desc="Time (in milliseconds) to start accepting user response.\nDefault value is zero.\nZero here means that user response will be enabled as soon as presentations of all the stimuli are finished. End of stimuli presentation is reached when image is displayed, sound/movie is played to its end, or at user defined time in 'present_time' item.\n\nIf you give minus value here such as -9000 and 10 seconds long movie stimulus is played. User response will be enabled one second after the beginning of the movie.\nIf too large minus value is given (longer than stimulus play), user response will be enabled as soon as trial starts.")
                           ))
                           
        ### Optional items 
        # Dictionary structure is as same as the basic item dictionary
        self.item_info.append( dict( arduino = dict(values=None,
                                                    value="motor_on",
                                                    desc="When this item is added, script for Arduino will be added.\nWhen the feedback is positive, an activation signal will be sent to Arduino to release food reward.\nThis item's value is the signal text for Arduino chip to activate food reward."), 
                           ))

        ### Items for stimulus setup
        # Dictionary structure is as same as the basic item dictionary
        self.item_info.append( dict( clickable = dict(values=None,
                                                 value=None,
                                                 desc="[This item & its values will automatically appear when the setup_stimuli is done.]\nDetermine whether an image is clickable or not. It will be set to False for 'snd' stimulus."),
                                present_time = dict(values=None,
                                                    value=None,
                                                    desc="[This item & its values will automatically appear when the setup_stimuli is done.]\nPresenting start and end time in milliseconds. The start time starts from one, not zero. When the end time is -1, image stimulus will remain until end of trial, and sound/movie stimulus will play till its end."),
                                rect = dict(values=None,
                                            value=None,
                                            desc="[This item & its values will automatically appear when the setup_stimuli is done.]\nWhen stimulus is image, rect can specify image presentation with x, y, width, height.\nx, y coordinates are float numbers between 0.0 and 1.0.\n0.0 means left or top end, 1.0 means right or bottom end.\nwidth and height are in pixels. If width or height is -1, the image will be displayed with its original size."),
                                s_type = dict(values=None,
                                              value=None,
                                              desc="[This item & its values will automatically appear when the setup_stimuli is done.]\nStimulus type. This is automatically determined by file extensions. Not manually editable.")))
        
        bd = 0
        self.gbs = wx.GridBagSizer(0,0)
        self.gbs.Add(wx.StaticLine(self, -1, size=(size[0]-10,-1)), pos=(0,0), span=(1,4), flag=wx.EXPAND|wx.ALL, border=5)
        row = 0
        for i in range(len(self.bItemsList)):
            for item in self.bItemsList[i]:
                row += 1
                wn = "%s_sTxt"%(item)
                sTxt = wx.StaticText(self, -1, item, name=wn)
                sTxt.SetFont(parent.fonts[2])
                sTxt.SetForegroundColour('#DDDDDD')
                self.gbs.Add(sTxt, pos=(row,0), flag=wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ALL, border=0)
                wn = "%s_help_btn"%(item)
                btn = wx.Button(self, -1, "", name=wn, size=(30,27))
                set_img_for_btn(path.join(self.parent.e_gui_path, "input/img_info.png"), btn)
                btn.Bind(wx.EVT_LEFT_UP, self.onHelp)
                self.gbs.Add(btn, pos=(row,1), flag=wx.ALIGN_LEFT|wx.ALL, border=1)
                self.gbs.Add((10,-1), pos=(row,2), flag=wx.ALIGN_LEFT|wx.ALL, border=0)
                self.gbs.Add(wx.StaticText(self, -1, "", size=(1,1)), pos=(row,3), flag=wx.EXPAND|wx.ALIGN_LEFT|wx.ALL, border=0)
                if i == 1: # bItemsList[1] is hidden by default
                    sTxt.Hide()
                    btn.Hide()
            if i == 0: 
                row += 1
                self.sh_btn = wx.Button(self, -1, "", name="showHide_btn", size=(250,25))
                set_img_for_btn(path.join(self.parent.e_gui_path, "input/img_arrow_down.png"), self.sh_btn)
                self.sh_btn.Bind(wx.EVT_LEFT_UP, self.onShowHide)
                self.flag_bItemsList1_shown = False
                self.gbs.Add(self.sh_btn, pos=(row,0), span=(1,4), flag=wx.EXPAND|wx.ALL, border=5)

        for item in sorted(self.item_info[2].keys()): # items automatically added when stimuli path is selected
            row += 1
            wn = "%s_sTxt"%(item)
            sTxt = wx.StaticText(self, -1, item, name=wn)
            sTxt.SetFont(parent.fonts[2])
            sTxt.SetForegroundColour('#DDDDDD')
            self.gbs.Add(sTxt, pos=(row,0), flag=wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ALL, border=0)
            wn = "%s_help_btn"%(item)
            btn = wx.Button(self, -1, "", name=wn, size=(30,27))
            set_img_for_btn(path.join(self.parent.e_gui_path, "input/img_info.png"), btn)
            btn.Bind(wx.EVT_LEFT_UP, self.onHelp)
            self.gbs.Add(btn, pos=(row,1), flag=wx.ALIGN_LEFT|wx.ALL, border=1)
            self.gbs.Add((10,-1), pos=(row,2), flag=wx.ALIGN_LEFT|wx.ALL, border=0)
            self.gbs.Add(wx.StaticText(self, -1, "", size=(1,1)), pos=(row,3), flag=wx.EXPAND|wx.ALIGN_LEFT|wx.ALL, border=0)
            sTxt.Hide()
            btn.Hide()

        row += 1
        self.gbs.Add(wx.StaticLine(self, -1, size=(size[0]-10,-1)), pos=(row,0), span=(1,4), flag=wx.EXPAND|wx.ALL, border=5)
        row += 1
        self.gbs.Add(wx.StaticText(self, -1, ""), pos=(row,0), span=(1,4), flag=wx.EXPAND|wx.ALL, border=1)
        row += 1
        self.gbs.Add(wx.StaticLine(self, -1, size=(size[0]-10,-1)), pos=(row,0), span=(1,4), flag=wx.EXPAND|wx.ALL, border=5)
        row += 1
        self.sh_op_btn = wx.Button(self, -1, "Show optional items", name="showHideOptionalItems_btn", size=(250,25))
        set_img_for_btn(path.join(self.parent.e_gui_path, "input/img_arrow_down.png"), self.sh_op_btn, False)
        self.sh_op_btn.Bind(wx.EVT_LEFT_UP, self.onShowHideOptionalItems)
        self.flag_optionItems_shown = False
        self.gbs.Add(self.sh_op_btn, pos=(row,0), span=(1,4), flag=wx.EXPAND|wx.ALL, border=5)
        
        for item in sorted(self.item_info[1].keys()): # optional items (arduino, ...)
            row += 1
            wn = "%s_sTxt"%(item)
            sTxt = wx.StaticText(self, -1, item, name=wn)
            sTxt.SetFont(parent.fonts[2])
            sTxt.SetForegroundColour('#DDDDDD')
            self.gbs.Add(sTxt, pos=(row,0), flag=wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ALL, border=0)
            sTxt.Hide()
            wn = "%s_help_btn"%(item)
            btn = wx.Button(self, -1, "", name=wn, size=(30,27))
            set_img_for_btn(path.join(self.parent.e_gui_path, "input/img_info.png"), btn)
            btn.Bind(wx.EVT_LEFT_UP, self.onHelp)
            self.gbs.Add(btn, pos=(row,1), flag=wx.ALIGN_LEFT|wx.ALL, border=1)
            btn.Hide()
            wn = "%s_add_btn"%(item)
            btn = wx.Button(self, -1, "", name=wn, size=(30,27))
            set_img_for_btn(path.join(self.parent.e_gui_path, "input/img_add.png"), btn)
            btn.Bind(wx.EVT_LEFT_UP, self.onAddItem) 
            self.gbs.Add(btn, pos=(row,2), flag=wx.ALIGN_LEFT|wx.ALL, border=0)
            btn.Hide()
            self.gbs.Add(wx.StaticText(self, -1, "", size=(1,1)), pos=(row,3), flag=wx.EXPAND|wx.ALIGN_LEFT|wx.ALL, border=0)
        row += 1
        self.gbs.Add(wx.StaticLine(self, -1, size=(size[0]-10,-1)), pos=(row,0), span=(1,4), flag=wx.EXPAND|wx.ALL, border=5)

        self.SetSizer(self.gbs)
        self.SetupScrolling()

    #------------------------------------------------

    def onAddItem(self, event):
        ''' process an optional item when add_btn is pressed
        '''
        if DEBUGGING: print('ItemPanel.onAddItem()')
        obj_name = event.GetEventObject().GetName()
        item = obj_name.replace("_add_btn", "")
        self.parent.mPanel.add_del_item(item)

    #------------------------------------------------

    def onHelp(self, event):
        ''' show descriptions of a selected item
        '''
        if DEBUGGING: print('ItemPanel.onHelp()')
        obj_name = event.GetEventObject().GetName()
        item = obj_name.replace("_help_btn", "")
        for i in range(len(self.item_info)):
            if item in self.item_info[i].keys():
                show_msg( self.item_info[i][item]["desc"], (400, 250) )
                break

    #------------------------------------------------
    
    def onShowHide(self, event):
        ''' show/hide basic items
        '''
        if DEBUGGING: print('ItemPanel.onShowHide()')
        event.Skip()
        def _func(item):
        # show/hide item title and its help button
            sTxt = wx.FindWindowByName( "%s_sTxt"%(item), self )
            helpBtn = wx.FindWindowByName( "%s_help_btn"%(item), self )
            if self.flag_bItemsList1_shown == False:
                sTxt.Show()
                helpBtn.Show()
            elif self.flag_bItemsList1_shown == True:
                sTxt.Hide()
                helpBtn.Hide()
        for item in self.bItemsList[1]: # items hidden by default among basic items (item_info[0])
            _func(item) 
        for item in sorted(self.item_info[2].keys()): # items automatically added when stimuli path is selected
            _func(item)
        
        ### change arrow button image and flag value
        if self.flag_bItemsList1_shown == False:
            self.flag_bItemsList1_shown = True
            set_img_for_btn(path.join(self.parent.e_gui_path, "input/img_arrow_up.png"), self.sh_btn)
        elif self.flag_bItemsList1_shown == True:
            self.flag_bItemsList1_shown = False
            set_img_for_btn(path.join(self.parent.e_gui_path, "input/img_arrow_down.png"), self.sh_btn)
        
        self.gbs.Layout()
        self.Layout()
        self.SetupScrolling()
    
    #------------------------------------------------
    
    def onShowHideOptionalItems(self, event):
        ''' show/hide optional items
        '''
        if DEBUGGING: print('ItemPanel.onShowHideOptionalItems()')
        event.Skip()
        for item in sorted(self.item_info[1].keys()):
        # show/hide item title and its help,add button
            sTxt = wx.FindWindowByName( "%s_sTxt"%(item), self )
            helpBtn = wx.FindWindowByName( "%s_help_btn"%(item), self )
            addBtn = wx.FindWindowByName( "%s_add_btn"%(item), self )
            if self.flag_optionItems_shown == False:
                sTxt.Show()
                helpBtn.Show()
                addBtn.Show()
            elif self.flag_optionItems_shown == True:
                sTxt.Hide()
                helpBtn.Hide()
                addBtn.Hide()
        
        ### change arrow button image, label and flag value
        if self.flag_optionItems_shown == False:
            self.flag_optionItems_shown = True
            set_img_for_btn(path.join(self.parent.e_gui_path, "input/img_arrow_up.png"), self.sh_op_btn, False)
            self.sh_op_btn.SetLabel('Hide optional items')
        elif self.flag_optionItems_shown == True:
            self.flag_optionItems_shown = False
            set_img_for_btn(path.join(self.parent.e_gui_path, "input/img_arrow_down.png"), self.sh_op_btn, False)
            self.sh_op_btn.SetLabel('Show optional items')
        
        self.gbs.Layout()
        self.Layout()
        self.SetupScrolling()
    
    #------------------------------------------------

#====================================================

if __name__ == "__main__": pass




