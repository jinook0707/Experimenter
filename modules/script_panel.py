# coding: UTF-8

'''
Experimenter_GUI: script_panel
- Right side panel to show generated script 

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


import keyword, subprocess
from copy import copy
from os import getcwd, path

import wx, wx.stc
from modules.fFuncNClasses import show_msg, PopupDialog, set_img_for_btn

DEBUGGING = False

# ======================================================

class STC(wx.stc.StyledTextCtrl):
    def __init__(self, parent, pos, size):
        self.parent = parent
        if DEBUGGING: print('STC.__init__()')
        wx.stc.StyledTextCtrl.__init__(self, parent, -1, pos=pos, size=size, style=wx.SIMPLE_BORDER)
        self.setStyle()
        
    # --------------------------------------------------
   
    def setStyle(self, face='Monaco', fore='#002266', back='#444444', sz=12):
        if DEBUGGING: print('STC.setStyle()')
        self.StyleClearAll()
        self.SetViewWhiteSpace(wx.stc.STC_WS_VISIBLEALWAYS)
        self.SetIndentationGuides(1)
        self.SetViewEOL(0)
        self.SetIndent(4) 
        self.SetMarginType(0, wx.stc.STC_MARGIN_NUMBER)
        self.SetMarginWidth(0, self.TextWidth(0,'9999'))
        
        self.SetLexer(wx.stc.STC_LEX_PYTHON)
        self.SetKeyWords(0, " ".join(keyword.kwlist))
        self.SetKeyWords(1, "self abs dict help min setattr all dir hex next slice any divmod id object sorted ascii enumerate input oct staticmethod bin eval int open str bool exec isinstance ord sum bytearray filter issubclass pow super bytes float iter print tuple callable format len property type chr frozenset list range vars classmethod getattr locals repr zip compile globals map reversed __import__ complex hasattr max round delattr hash memoryview set") # 'self' and built-in functions
        
        dFont = dict(face=face, fore=fore, back=back, sz=sz)
        self.StyleSetSpec(wx.stc.STC_STYLE_LINENUMBER, "face:%(face)s,fore:#ffffffs,back:#111111,size:%(sz)i"%(dFont))
        self.StyleSetSpec(wx.stc.STC_STYLE_DEFAULT, "face:%(face)s,fore:%(fore)s,back:%(back)s,size:%(sz)i"%(dFont))
        self.StyleSetSpec(wx.stc.STC_P_DEFAULT, "face:%(face)s,fore:%(fore)s,back:%(back)s,size:%(sz)i"%(dFont))
        self.StyleSetSpec(wx.stc.STC_P_COMMENTLINE, "face:%(face)s,fore:#00cc00,back:%(back)s,italic,size=%(sz)i"%(dFont))
        self.StyleSetSpec(wx.stc.STC_P_COMMENTBLOCK, "face:%(face)s,fore:#00cc00,back:%(back)s,italic,size=%(sz)i"%(dFont))
        self.StyleSetSpec(wx.stc.STC_P_TRIPLE, "face:%(face)s,fore:#00cc00,back:%(back)s,italic,size=%(sz)i"%(dFont)) # Triple quotes
        self.StyleSetSpec(wx.stc.STC_P_TRIPLEDOUBLE, "face:%(face)s,fore:#00cc00,back:%(back)s,italic,size=%(sz)i"%(dFont)) # Triple double quotes
        self.StyleSetSpec(wx.stc.STC_P_NUMBER, "face:%(face)s,fore:#eeee33,back:%(back)s,size=%(sz)i"%(dFont))
        self.StyleSetSpec(wx.stc.STC_P_STRING, "face:%(face)s,fore:#ff7700,back:%(back)s,size=%(sz)i"%(dFont))
        self.StyleSetSpec(wx.stc.STC_P_CHARACTER, "face:%(face)s,fore:#ff7700,back:%(back)s,size=%(sz)i"%(dFont)) # Single quoted string 
        self.StyleSetSpec(wx.stc.STC_P_WORD, "face:%(face)s,fore:#cc4488,back:%(back)s,size=%(sz)i"%(dFont)) # Keyword
        self.StyleSetSpec(wx.stc.STC_P_WORD2, "face:%(face)s,fore:#ff8888,back:%(back)s,size=%(sz)i"%(dFont)) # 'self' & built-in functions 
        self.StyleSetSpec(wx.stc.STC_P_CLASSNAME, "face:%(face)s,fore:#aaaaff,back:%(back)s,bold,size=%(sz)i"%(dFont))
        self.StyleSetSpec(wx.stc.STC_P_DEFNAME, "face:%(face)s,fore:#55cccc,back:%(back)s,bold,size=%(sz)i"%(dFont))
        self.StyleSetSpec(wx.stc.STC_P_OPERATOR, "face:%(face)s,fore:%(fore)s,back:%(back)s,bold,size=%(sz)i"%(dFont))
        self.StyleSetSpec(wx.stc.STC_P_IDENTIFIER, "face:%(face)s,fore:#ffffff,back:%(back)s,size=%(sz)i"%(dFont))
        self.StyleSetSpec(wx.stc.STC_P_STRINGEOL, "face:%(face)s,fore:#000000,back:#E0C0E0,size=%(sz)i"%(dFont)) # End of line where string is not closed

        self.MarkerDefine(0, wx.stc.STC_MARK_ARROW, "#ffaa00", "#000000")#
        self.SetCaretStyle(2)
        self.SetCaretForeground('#111111')
    
    # --------------------------------------------------

# ======================================================

class ScriptPanel(wx.Panel):
    def __init__(self, parent, pos, size):
        self.parent = parent
        if DEBUGGING: print('ScriptPanel.__init__()')
        wx.Panel.__init__(self, parent, -1, pos=pos, size=size)
        self.SetBackgroundColour('#333333')
        
        self.fSzSTC = 12
        self.cmi = -1 # current marker index
        self.markerIds = []
        btnSz = (30,-1)
        self.widgets = [[], []] # widgets others than STC, the first widget list belongs to STC (meaning when Script is hidden, these widgets will be hidden as well; marker button, zoom button), the second widget list contaings others such as save, load button.
        self.scriptChangedByMainPanel = '' # for storing script when it was changed by manipulating widgets in mainPanel (to compare this with script when it's saved to check whether manual script change occurred)

        self.gbs = wx.GridBagSizer(0,0)
        bw = 2 
       
        row=0; col=0
        stc_sz = (size[0]-4, size[1]-100)
        self.stc = STC(self, (2,0), stc_sz)
        self.gbs.Add(self.stc, pos=(row,col), span=(1,10), flag=wx.EXPAND|wx.ALL, border=bw)
        
        col += 10
        self.gbs.Add(wx.StaticText(self, -1, "", size=(1,1)), pos=(row,col), flag=wx.EXPAND|wx.ALL, border=bw)
       
        row += 1
        col = 0
        sTxt = wx.StaticText(self, -1, "Marker")
        self.widgets[0].append(sTxt)
        sTxt.SetForegroundColour('#CCCCCC')
        self.gbs.Add(sTxt, pos=(row,col), flag=wx.ALIGN_CENTER_VERTICAL|wx.ALL, border=bw)

        col += 1
        btn = wx.Button(self, -1, label="marker", name="prevM", size=btnSz)
        set_img_for_btn(path.join(self.parent.e_gui_path, "input/img_marker_prev.png"), btn)
        self.widgets[0].append(btn)
        btn.Bind(wx.EVT_LEFT_UP, self.onNavMarkers)
        self.gbs.Add(btn, pos=(row,col), flag=wx.ALIGN_CENTER_VERTICAL|wx.ALL, border=bw)
       
        col += 1
        btn = wx.Button(self, -1, label="marker", name="nextM", size=btnSz)
        set_img_for_btn(path.join(self.parent.e_gui_path, "input/img_marker_next.png"), btn)
        self.widgets[0].append(btn)
        btn.Bind(wx.EVT_LEFT_UP, self.onNavMarkers)
        self.gbs.Add(btn, pos=(row,col), flag=wx.ALIGN_CENTER_VERTICAL|wx.ALL, border=bw)

        col += 1
        sTxt = wx.StaticText(self, -1, "Zoom")
        self.widgets[0].append(sTxt)
        sTxt.SetForegroundColour('#CCCCCC')
        self.gbs.Add(sTxt, pos=(row,col), flag=wx.ALIGN_CENTER_VERTICAL|wx.ALL, border=bw)

        col += 1
        btn = wx.Button(self, -1, label="", name="zoom+", size=btnSz)
        set_img_for_btn(path.join(self.parent.e_gui_path, "input/img_zoomin.png"), btn)
        self.widgets[0].append(btn)
        btn.Bind(wx.EVT_LEFT_UP, self.onZoom)
        self.gbs.Add(btn, pos=(row,col), flag=wx.ALIGN_CENTER_VERTICAL|wx.ALL, border=bw)

        col += 1
        btn = wx.Button(self, -1, label="", name="zoom-", size=btnSz)
        set_img_for_btn(path.join(self.parent.e_gui_path, "input/img_zoomout.png"), btn)
        self.widgets[0].append(btn)
        btn.Bind(wx.EVT_LEFT_UP, self.onZoom)
        self.gbs.Add(btn, pos=(row,col), flag=wx.ALIGN_CENTER_VERTICAL|wx.ALL, border=bw)

        col += 1 
        self.gbs.Add(wx.StaticText(self, -1, "", size=(1,1)), pos=(row,col), flag=wx.EXPAND|wx.ALL, border=bw)
        
        col += 1
        cho = wx.Choice(self, -1, choices = ["Show: Stimuli_set-up", "Show: Scheduling_stimuli_presentation", "Show: Presenting_text", "Show: Presenting_image", "Show: Presenting_sound", "Show: Presenting_movie", "Show: Writing_result", "Show: Presenting_feedback"])
        self.widgets[0].append(cho)
        cho.Bind(wx.EVT_LEFT_UP, self.onChoiceMarkerTag)
        self.gbs.Add(cho, pos=(row,col), span=(1,4), flag=wx.ALIGN_CENTER_VERTICAL|wx.ALL, border=bw)
        
        col += 4 
        self.gbs.Add(wx.StaticText(self, -1, "", size=(1,1)), pos=(row,col), span=(1,1), flag=wx.EXPAND|wx.ALL, border=bw)
       
        row += 1; col = 0 
        txt = wx.TextCtrl(self, -1, value='SearchText', name="searchTxt", size=(120,-1), style=wx.TE_PROCESS_ENTER)
        self.widgets[0].append(txt)
        txt.Bind(wx.EVT_TEXT_ENTER, self.onSearch)
        self.gbs.Add(txt, span=(1,3), pos=(row,col), flag=wx.ALIGN_CENTER_VERTICAL|wx.ALL, border=bw)
        col += 3 
        btn = wx.Button(self, -1, label="", name="searchBtn", size=btnSz)
        set_img_for_btn(path.join(self.parent.e_gui_path, "input/img_search.png"), btn)
        self.widgets[0].append(btn)
        btn.Bind(wx.EVT_LEFT_UP, self.onSearch)
        self.gbs.Add(btn, pos=(row,col), flag=wx.ALIGN_CENTER_VERTICAL|wx.ALL, border=bw)
        col += 1
        txt = wx.TextCtrl(self, -1, value='ReplaceText', name="replaceTxt", size=(150,-1), style=wx.TE_PROCESS_ENTER)
        self.widgets[0].append(txt)
        self.gbs.Add(txt, span=(1,3), pos=(row,col), flag=wx.ALIGN_CENTER_VERTICAL|wx.ALL, border=bw)
        col += 3
        btn = wx.Button(self, -1, label="Replace-1", name="replaceOneBtn", size=(btnSz[0]*3,btnSz[1]))
        self.widgets[0].append(btn)
        btn.Bind(wx.EVT_LEFT_UP, self.onReplace)
        self.gbs.Add(btn, pos=(row,col), flag=wx.ALIGN_CENTER_VERTICAL|wx.ALL, border=bw)
        col += 1
        btn = wx.Button(self, -1, label="Replace-All", name="replaceAllBtn", size=(btnSz[0]*3,btnSz[1]))
        self.widgets[0].append(btn)
        btn.Bind(wx.EVT_LEFT_UP, self.onReplace)
        self.gbs.Add(btn, pos=(row,col), flag=wx.ALIGN_CENTER_VERTICAL|wx.ALL, border=bw)
        col += 1
        self.gbs.Add(wx.StaticText(self, -1, "", size=(1,1)), span=(1,2), pos=(row,col), flag=wx.EXPAND|wx.ALL, border=bw)

        row += 1
        col = 0
        sTxt = wx.StaticText(self, -1, "FileName (without path)")
        self.widgets[1].append(sTxt)
        sTxt.SetForegroundColour('#CCCCCC')
        self.gbs.Add(sTxt, pos=(row,col), span=(1,4), flag=wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT|wx.ALL, border=bw)

        col += 4 
        txt = wx.TextCtrl(self, -1, value='test.py', name="fn", size=(150,-1), style=wx.TE_PROCESS_ENTER)
        self.widgets[1].append(txt)
        txt.Bind(wx.EVT_TEXT_ENTER, self.onSave)
        self.gbs.Add(txt, pos=(row,col), span=(1,3), flag=wx.ALIGN_CENTER_VERTICAL|wx.ALL, border=bw)

        col += 3 
        btn = wx.Button(self, -1, label="Save", name="save", size=(btnSz[0]*3,btnSz[1]), style=wx.ID_SAVE)
        set_img_for_btn(path.join(self.parent.e_gui_path, "input/img_save.png"), btn, False)
        self.widgets[1].append(btn)
        btn.Bind(wx.EVT_LEFT_UP, self.onSave)
        self.gbs.Add(btn, pos=(row,col), flag=wx.ALIGN_CENTER_VERTICAL|wx.ALL, border=bw)
       
        col += 1
        btn = wx.Button(self, -1, label="Load", name="load", size=(btnSz[0]*3,btnSz[1]))
        set_img_for_btn(path.join(self.parent.e_gui_path, "input/img_load.png"), btn, False)
        self.widgets[1].append(btn)
        btn.Bind(wx.EVT_LEFT_UP, self.onLoad)
        self.gbs.Add(btn, pos=(row,col), flag=wx.ALIGN_CENTER_VERTICAL|wx.ALL, border=bw)

        col += 1 
        btn = wx.Button(self, -1, label="RUN", name="run", size=(btnSz[0]*3,btnSz[1]))
        set_img_for_btn(path.join(self.parent.e_gui_path, "input/img_run.png"), btn, False)
        self.widgets[1].append(btn)
        btn.Bind(wx.EVT_LEFT_UP, self.onRun)
        self.gbs.Add(btn, pos=(row,col), flag=wx.ALIGN_CENTER_VERTICAL|wx.ALL, border=bw)
        
        col += 1 
        self.gbs.Add(wx.StaticText(self, -1, "", size=(1,1)), pos=(row,col), flag=wx.EXPAND|wx.ALL, border=bw)

        ### load the base code
        f = open( path.join(self.parent.e_gui_path, 'scripts/base.py'), 'r' )
        txt = f.read()
        f.close()
        for item in self.parent.mPanel.items.keys():
            _, _, txt = self.replaceValTxt(item, txt)
        self.stc.AddText(txt)
        
        ### hide script and related buttons by default
        self.stc.Hide()
        for w in self.widgets[0]: w.Hide()

        self.SetSizer(self.gbs)
        self.gbs.Layout()
        #self.SetupScrolling()

    # --------------------------------------------------
    
    def scriptChangeByMainPanel(self, txt):
        self.stc.SetText(txt)
        self.scriptChangedByMainPanel = txt # store script when it was changed by manipulating widgets in mainPanel (to compare this with script when it's saved to check whether manual script change occurred)
    
    # --------------------------------------------------
    
    def updateItemVal(self, item):
        if DEBUGGING: print('ScriptPanel.updateItemVal()')
        ### store line numbers of markers
        if self.markerIds != []:
            m_line_num = []
            for mid in self.markerIds:
                m_line_num.append( self.stc.MarkerLineFromHandle(mid) )

        ### update the value
        txt = self.stc.GetText()
        idx1, idx2, txt = self.replaceValTxt(item, txt)
        self.scriptChangeByMainPanel(txt)

        ### restore markers
        if self.markerIds != []:
            self.markerIds = []
            for line_num in m_line_num:
                self.markerIds.append( self.stc.MarkerAdd(line_num,0) )
        
        ### selection on the changed value
        self.stc.GotoPos(idx1)
        self.stc.SetSelection(idx1, idx2)
        line_num = self.stc.GetCurrentLine()
        line_num = max(0, line_num-3)
        self.stc.SetFirstVisibleLine(line_num)

    # --------------------------------------------------

    def replaceValTxt(self, item, txt):
        if DEBUGGING: print('ScriptPanel.replaceValTxt()')
        vType, value = self.parent.mPanel.getItemVal(item)
        flag = '#[flag:%s]'%(item)
        idx2 = txt.find(flag) # find where the item's flag is
        idx1 = copy(idx2)
        while txt[idx1] != '=': idx1 -= 1 # move index to the previous '=' sign
        if vType == 't': value = '"%s"'%(value) # if the vaule is text, add quote marks around it
        elif vType == 'l': value = value.replace("],", "],\n           ")
        txt = '%s %s %s'%(txt[:idx1+1], value, txt[idx2:]) # change the value text
        idx1 += 2; idx2 = txt.find(flag)-1
        return idx1, idx2, txt

    # --------------------------------------------------

    def addItemScript(self, newTxt):
        if DEBUGGING: print('ScriptPanel.addItemScript()')
        lbls = ['import', 'class', 'function', 'init', 'functionInExperimenterClass']
        mi1=[]; mi2=[]
        txt = self.stc.GetText()
        for lbl in lbls:
            flag = '#[flag:%s-begin]'%(lbl)
            idx1 = newTxt.find(flag)
            while newTxt[idx1] != '\n' and idx1 < len(newTxt): idx1 += 1 # to the next line
            idx1 += 1
            flag = '#[flag:%s-end]'%(lbl)
            idx2 = newTxt.find(flag)
            if idx1 == -1 or idx2 == -1: continue # flags are not found. go to the next lbl
            idx = txt.find(flag)
            while txt[idx] != '\n' and idx > 0: idx -= 1 # to the previous line
            idx += 1
            txt = txt[:idx] + newTxt[idx1:idx2] + txt[idx:] # insert the new script text

            mi1.append(idx) # store index for marking
            idx = txt.find(flag)
            while txt[idx] != '\n' and idx > 0: idx-=1 # to the previous line
            mi2.append(idx+1) # store index for marking
        self.scriptChangeByMainPanel(txt)

        self.delAllMarkers()
        ### add markers for newly added lines
        for i in range(len(mi1)):
            _i = int(mi1[i])
            while _i < mi2[i]:
                self.stc.GotoPos(_i)
                line_num = self.stc.GetCurrentLine()
                self.markerIds.append( self.stc.MarkerAdd(line_num,0) )
                ### to the next line
                _i += 1
                while txt[_i] != '\n' and _i < mi2[i]: _i += 1
        self.cmi = -1 # current marker index
        self.stc.ScrollToColumn(0)
        
    # --------------------------------------------------
    
    def removeItemScript(self, targetTxt):
        if DEBUGGING: print('ScriptPanel.removeItemScript()')
        lbls = ['import', 'class', 'function', 'init', 'functionInExperimenterClass']
        mi1=[]; mi2=[]
        txt = self.stc.GetText()
        for lbl in lbls:
            flag = '#[flag:%s-begin]'%(lbl)
            idx1 = targetTxt.find(flag)
            while targetTxt[idx1] != '\n' and idx1 < len(targetTxt): idx1 += 1 # to the next line
            idx1 += 1
            flag = '#[flag:%s-end]'%(lbl)
            idx2 = targetTxt.find(flag)
            if idx1 == -1 or idx2 == -1: continue # flags are not found. go to the next lbl
            txt = txt.replace( targetTxt[idx1:idx2], "" ) # remove the target text from the current script  
        self.scriptChangeByMainPanel(txt)
        self.delAllMarkers()

    # --------------------------------------------------
    
    def onSearch(self, event):
        ''' search a string in the current script text
        '''
        if event != None: event.Skip()
        searchTxt = wx.FindWindowByName("searchTxt").GetValue().strip()
        if searchTxt == '':
            if event == None: return searchTxt, -1
            else: return
        curr_pos = self.stc.GetCurrentPos()
        if curr_pos > 0: curr_pos += len(searchTxt)
        txtLen = self.stc.GetTextLength()
        if curr_pos >= txtLen:
            idx = self.stc.FindText(0, txtLen, searchTxt )
        else:
            idx = self.stc.FindText(curr_pos, txtLen, searchTxt )
            if idx == -1: idx = self.stc.FindText(0, txtLen, searchTxt )
        if event == None: return searchTxt, idx # if this function was called by 'onReplace', return found index
        if idx == -1:
            show_msg("The search string, %s, is not found in the current script."%(searchTxt), (250,150))
        else:
            self.stc.GotoPos(idx)
            self.stc.SetSelection(idx, idx+len(searchTxt))

    # --------------------------------------------------
    
    def onReplace(self, event):
        ''' search a string in the current script text
        & replace it with the typed text in replaceTxt
        '''
        event.Skip()
        searchTxt, idx1 = self.onSearch(None)
        if idx1 == -1:
            show_msg("The search string, %s, is not found in the current script."%(searchTxt), (250,150))
            return
        evtObjName = event.GetEventObject().GetName() 
        replaceTxt = wx.FindWindowByName("replaceTxt").GetValue().strip()
        if evtObjName == "replaceOneBtn": 
            self.stc.Replace(idx1, idx1+len(searchTxt), replaceTxt)
            self.stc.GotoPos(idx1)
            self.stc.SetSelection(idx1, idx1+len(replaceTxt))
        elif evtObjName == "replaceAllBtn":
            cnt = 1
            lastIdx = -1
            while idx1 != -1:
                self.stc.Replace(idx1, idx1+len(searchTxt), replaceTxt)
                lastIdx = copy(idx1)
                searchTxt, idx1 = self.onSearch(None)
                if idx1 == -1: show_msg("%i found texts are replaced."%(cnt), (250,100))
                cnt += 1
            self.stc.GotoPos(lastIdx)
            self.stc.SetSelection(lastIdx, lastIdx+len(replaceTxt))
            self.stc.SetFocus()
    
    # --------------------------------------------------
    
    def onNavMarkers(self, event):
        if DEBUGGING: print('ScriptPanel.onNavMarkers()')
        if self.markerIds == []:
            show_msg("No markers found.\n(Markers will be added when a marker button is pressed in the center panel or new script lines are added.)", size=(300,170))
            return
       
        if type(event) == str:
            obj_name = event
        else:
            event.Skip()
            obj = event.GetEventObject()
            obj_name = obj.GetName()
        
        ### move screen and caret to the next or prev marker
        if obj_name == 'nextM':
            self.cmi += 1
            if self.cmi >= len(self.markerIds): self.cmi = 0
        elif obj_name == 'prevM':
            self.cmi -= 1
            if self.cmi < 0: self.cmi = len(self.markerIds)-1
        line_num = self.stc.MarkerLineFromHandle(self.markerIds[self.cmi])
        self.stc.GotoLine(line_num)
        #if self.stc.GetLineVisible(line_num) == False: # the line is not visible
        #    vl = max(1, line_num-10)
        #    self.stc.SetFirstVisibleLine(vl)
        self.stc.SetSelection(self.stc.GetCurrentPos(), self.stc.GetLineEndPosition(line_num))
    
    # --------------------------------------------------
   
    def onChoiceMarkerTag(self, event):
        ''' Certain marker tags were added to base.py to help quick browsing of base.py
        When user chose one of those tags with Choice widget, show markers for it.
        '''
        cho = event.GetEventObject()
        tag = cho.GetStringSelection().replace("Show: ","")
        self.dispMarkers(tag)

    # --------------------------------------------------

    def dispMarkers(self, item):
    # Display markers on lines related to item. The lines are marked by flag text in the base.py script 
        if DEBUGGING: print('ScriptPanel.dispMarkers()')
        self.delAllMarkers()
        st = "#[flag_marker:%s]"%(item) # search text
        idx = None 
        while idx != -1:
            if idx == None: self.stc.GotoPos(0) # go to the beginning of the script
            else:
                self.stc.GotoPos(idx)
                line_num = self.stc.GetCurrentLine()
                self.markerIds.append( self.stc.MarkerAdd(line_num,0) )
                self.stc.GotoPos(idx+len(st)+1)
            self.stc.SearchAnchor()
            idx = self.stc.SearchNext(0, st)
        self.cmi = -1 # current marker index
        if len(self.markerIds) > 0: self.onNavMarkers('nextM')
        ### set marked line in the middle
        line_num = self.stc.GetCurrentLine()
        line_num = max(0, line_num-self.stc.LinesOnScreen()/2)
        self.stc.SetFirstVisibleLine(line_num)
    
    # --------------------------------------------------
    
    def delAllMarkers(self):
        if DEBUGGING: print('ScriptPanel.delAllMarkers()')
        self.stc.MarkerDeleteAll(-1)
        self.markerIds = []
    
    # --------------------------------------------------
   
    def onZoom(self, event):
        if DEBUGGING: print('ScriptPanel.onZoom()')
        event.Skip()
        obj = event.GetEventObject()
        obj_name = obj.GetName()
        if obj_name == 'zoom+':
            self.fSzSTC = min(self.fSzSTC+2, 30)
            self.stc.setStyle(sz=self.fSzSTC)
        elif obj_name == 'zoom-':
            self.fSzSTC = max(4, self.fSzSTC-2)
            self.stc.setStyle(sz=self.fSzSTC)

    # --------------------------------------------------
    
    def onRun(self, event):
        if DEBUGGING: print('ScriptPanel.onRun()')
        event.Skip()

        obj = wx.FindWindowByName( "fn", self )
        script_fn = obj.GetValue().strip()
        if path.isfile(script_fn) == False:
            show_msg("File, %s, doesn't exist"%(script_fn))
            return

        f = open(script_fn, 'r')
        fileScript = f.read()
        f.close()
        currScript = self.stc.GetText() # current script in the script panel

        if fileScript != currScript: # script from file and script panel is different
            dlg = PopupDialog(inString="This will run the file, %s.\nThe contents of the file and the current script in this script panel is different.\nPress Okay to overwrite the file with the current script and run.\nPress Cancel to run the file as it is."%(script_fn), title="Overwriting",  size=(400,200), cancel_btn=True)
            result = dlg.ShowModal()
            dlg.Destroy()
            if result == wx.ID_OK: self.onSave(None, flag_overwrite=True) 
        
        cmd = ['pythonw', script_fn]
        stdout = ''
        try:
            p = subprocess.Popen(cmd, stderr=subprocess.STDOUT, stdout=subprocess.PIPE)
            stdout, stderr = p.communicate()
            p.terminate()
            p.wait()
        except:
            pass
        title = "stdout"
        if 'error' in str(stdout).lower(): title += ": ERROR"
        show_msg(msg=stdout.strip(), size=(700,350), title=title)
    
    # --------------------------------------------------
    
    def updateMainPanelFromScript(self, txt):
        ''' Update main panel widgets with contents from script, when laoding script from file or saving occurs.
        'txt': script text
        '''
        ### delete (hide from screen) current optional item widgets in main-panel 
        for item in self.parent.iPanel.item_info[1]:
            btn_name = "%s_del_btn"%(item)
            del_btn_obj = wx.FindWindowByName( btn_name, self.parent.mPanel )
            if del_btn_obj != None: # object found
                self.parent.mPanel.onDelItem(btn_name) # delete
        
        ### update or add items in main-panel with the loaded script 
        # basic items
        err_msg = ""
        for item in sorted(self.parent.iPanel.item_info[0].keys()): # iterate basic items
            idx1 = txt.find("#[flag:%s]"%(item))
            if idx1 == -1: # flag was not found
                err_msg += "#[flag:%s] was not found.\n"%(item)
                continue
            idx2 = copy(idx1)
            while txt[idx1] != '=': idx1 -= 1 # move index to the previous '=' sign
            val = txt[idx1+1:idx2].strip().replace('\n','').replace(' ','')
            if val[0] != '[' and val[-1] != ']': # it's not a list
                if '"' in val: val = val.replace('"', '') # get rid of double quote marks
                if "'" in val: val = val.replace("'", '') # get rid of single quote marks 
            self.parent.mPanel.setItemVal(item, val)
        if err_msg != "": err_msg += "\n\n"
        # stimulus items
        _list = list(self.parent.iPanel.item_info[2].keys())
        _list.remove('s_type')
        _list.insert(0, 's_type') # s_type;stimulus-type should be processed first, because others (clickable, etc) refers s_type's values
        for item in _list: # iterate stimulus items
            idx1 = txt.find("#[flag:%s]"%(item))
            if idx1 == -1: # flag was not found
                err_msg += "#[flag:%s] was not found.\n"%(item)
                continue
            idx2 = copy(idx1)
            while txt[idx1] != '=': idx1 -= 1 # move index to the previous '=' sign
            val = txt[idx1+1:idx2].strip().replace('\n','').replace(' ','')
            self.parent.mPanel.add_del_item(item, item_list_idx=2)
            self.parent.mPanel.setItemVal(item, val)
        if err_msg != "": err_msg += "\n\n"
        # optional items
        for item in sorted(self.parent.iPanel.item_info[1].keys()): # iterate optional items
            idx1 = txt.find("#[flag:%s]"%(item))
            if idx1 == -1: continue # continue, if the flag was not found.
            idx2 = copy(idx1)
            while txt[idx1] != '=': idx1 -= 1 # move index to the previous '=' sign
            val = txt[idx1+1:idx2].strip().replace('\n','').replace(' ','')
            if val == 'False': continue
            if val[0] != '[' and val[-1] != ']': # it's not a list
                if '"' in val: val = val.replace('"', '') # get rid of double quote marks
                if "'" in val: val = val.replace("'", '') # get rid of single quote marks 
            self.parent.mPanel.add_del_item(item, item_list_idx=1)
            self.parent.mPanel.setItemVal(item, val)
        if err_msg != "": show_msg(err_msg)
        # audio_output
        idx = txt.find("class Output_AudioData")
        if idx != -1: # the class was found
            self.parent.mPanel.items['audio_output'] = "added"
        # movie
        idx = txt.find("class MovPlayer")
        if idx != -1: # the class was found
            self.parent.mPanel.items['movie'] = "added"
    
    # --------------------------------------------------
    
    def onLoad(self, event):
        if DEBUGGING: print('ScriptPanel.onLoad()')
        event.Skip()
        f = wx.FileDialog(self, "Choose a Python file you saved before.", getcwd(), wildcard="Python files (*.py)|*.py", style=wx.FD_DEFAULT_STYLE|wx.FD_OPEN|wx.FD_FILE_MUST_EXIST)
        if f.ShowModal() == wx.ID_CANCEL: return
        fp = f.GetPath()
        f = open(fp, "r")
        txt = f.read()
        f.close()
        if (not 'class Experimenter' in txt) or (not '#[flag:' in txt):
            show_msg("The chosen file is not an Experimenter Python file.")
            return
        
        self.updateMainPanelFromScript(txt) # update main panel widgets with the script text

        self.stc.SetText(txt) # load the script text to STC
        self.stc.SetFirstVisibleLine(0)
        self.stc.ScrollToColumn(0)
    
    # --------------------------------------------------
    
    def onSave(self, event, flag_overwrite=False):
        if DEBUGGING: print('ScriptPanel.onSave()')
        if event != None: event.Skip()
        obj = wx.FindWindowByName( "fn", self )
        fn = obj.GetValue().strip()
        if fn == '':
            dlg = wx.MessageDialog(self, 'Filename is empty.', style=wx.OK|wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        savePath = path.join( getcwd(), path.basename(fn) )
        file_exists = path.isfile(savePath)
        if file_exists:
            if flag_overwrite != True: # if it's not already instructed to overwrite
                ### ask whether to overwrite
                dlg = PopupDialog(inString="File already exists. Overwrite it?", size=(300,100), cancel_btn=True)
                result = dlg.ShowModal()
                dlg.Destroy()
                if result == wx.ID_CANCEL: return
        txt = self.stc.GetText()
        f = open(savePath, 'wb')
        f.write(txt.encode('utf8'))
        f.close()

        if txt != self.scriptChangedByMainPanel: # manual script change occurred
            self.updateMainPanelFromScript(txt) # update main panel widgets with the script text, because user might have edited script manually.
            self.scriptChangedByMainPanel = txt

        if not file_exists: show_msg("File is saved at\n%s"%(savePath))

# ======================================================

if __name__ == "__main__": pass



