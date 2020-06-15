# coding: UTF-8

from os import path, rename
from math import sqrt
from glob import glob

import wx
from wx.lib.wordwrap import wordwrap
from modules.fFuncNClasses import writeFile, get_time_stamp, show_msg, set_img_for_btn, load_img

DEBUGGING = False

#====================================================

class SetupStimuliDialog(wx.Dialog):
    def __init__(self, parent):
        if DEBUGGING: print('SetupStimuliDialog.__init__()')
        
        self.parent = parent
        self.e_gui_path = parent.parent.e_gui_path

        self.main_param = ['number_of_trials', 'number_of_experimental_stimuli', 'number_of_response_stimuli']
        self.return_val = dict( number_of_trials = 0, 
                                number_of_experimental_stimuli = 0,
                                number_of_response_stimuli = 0,
                                types_of_es = [],
                                types_of_rs = [],
                                rects_of_es = [],
                                rects_of_rs = [],
                                paths_of_es = [],
                                paths_of_rs = [],
                                movie_module = None )
        self.setting_p_sz = (350, 400)
        self.ds_sz = (100, 100) # default size of a stimulus rectangle
        self.esRectTxts = [] # textctrls for experimental stimuli rects
        self.rsRectTxts = [] # textctrls for response stimuli rects
        self.esOpenBtns = [] # buttons for opening folder for experimental stimuli
        self.rsOpenBtns = [] # buttons for opening folder for response stimuli
        self.rsCorrectBtns = [] # buttons for selecting correct response stimulus
        self.rsCorrIdx = -1 # index of response stimuli, indicating correct response
        self.sliders = [] # user response slider 
        ### for show/hide-setting animation
        self.showHideAnimation = ""
        self.ani_fr = 15 # frames for animation
        self.ani_intv = 200/self.ani_fr # interval between frames (in milliseconds)
        
        w_pos = (0, 25) 
        w_size = (wx.Display(0).GetGeometry()[2], wx.Display(0).GetGeometry()[3]-w_pos[1])  
        self.w_sz = w_size 
        wx.Dialog.__init__(self, parent, -1, "Stimuli setup", pos=w_pos, size=w_size)
        self.SetBackgroundColour('#AAAABB')

        self.setting_p = wx.Panel(self, -1, pos=(5,5), size=self.setting_p_sz)
        self.setting_p.SetBackgroundColour('#999999')
        self.gbs = wx.GridBagSizer(0,0)
        bw=5; row=0; col=0
        sTxt = wx.StaticText(self.setting_p, -1, "")
        self.gbs.Add(sTxt, pos=(row,col), span=(1,2), flag=wx.ALL, border=bw)
        col += 2
        self.showHideBtn = wx.Button(self.setting_p, -1, "", size=(30,30))
        set_img_for_btn(path.join(self.e_gui_path, "input/img_arrow_left.png"), self.showHideBtn)
        self.showHideBtn.Bind(wx.EVT_LEFT_DOWN, self.onShowHideParamPanel)
        self.gbs.Add(self.showHideBtn, pos=(row,col), flag=wx.ALL, border=bw)
        
        row += 1; col = 0 
        sTxt = wx.StaticText(self.setting_p, -1, "Please specify below three parameters first.")
        self.gbs.Add(sTxt, pos=(row,col), span=(1,3), flag=wx.ALL, border=bw)

        row += 1; col = 0 
        sTxt = wx.StaticText(self.setting_p, -1, "")
        self.gbs.Add(sTxt, pos=(row,col), span=(1,3), flag=wx.ALL, border=bw)

        row += 1; col = 0 
        sTxt = wx.StaticText(self.setting_p, -1, "Number of trials")
        self.gbs.Add(sTxt, pos=(row,col), flag=wx.ALL, border=bw)
        col += 1
        txt = wx.TextCtrl(self.setting_p, -1, value = "0", name="number_of_trials", size=(35,-1), style=wx.TE_PROCESS_ENTER)
        txt.Bind(wx.EVT_TEXT_ENTER, self.onClickApply)
        self.gbs.Add(txt, pos=(row,col), flag=wx.ALL, border=bw)
        col += 1
        sTxt = wx.StaticText(self.setting_p, -1, "")
        self.gbs.Add(sTxt, pos=(row,col), flag=wx.ALL, border=bw)

        row += 1; col = 0 
        sTxt = wx.StaticText(self.setting_p, -1, "")
        self.gbs.Add(sTxt, pos=(row,col), span=(1,3), flag=wx.ALL, border=bw)
         
        row += 1; col = 0 
        sTxt = wx.StaticText(self.setting_p, -1, "Number of experimental stimuli per trial")
        self.gbs.Add(sTxt, pos=(row,col), flag=wx.ALL|wx.ALIGN_BOTTOM, border=bw)
        col += 1
        txt = wx.TextCtrl(self.setting_p, -1, value = "0", name="number_of_experimental_stimuli", size=(35,-1), style=wx.TE_PROCESS_ENTER)
        txt.Bind(wx.EVT_TEXT_ENTER, self.onClickApply)
        self.gbs.Add(txt, pos=(row,col), flag=wx.ALL, border=bw)
        col += 1
        sTxt = wx.StaticText(self.setting_p, -1, "")
        self.gbs.Add(sTxt, pos=(row,col), flag=wx.ALL, border=bw)

        row += 1; col = 0
        sTxt = wx.StaticText(self.setting_p, -1, "Number of response stimuli per trial")
        self.gbs.Add(sTxt, pos=(row,col), flag=wx.ALL|wx.ALIGN_BOTTOM, border=bw)
        col += 1
        txt = wx.TextCtrl(self.setting_p, -1, value = "0", name="number_of_response_stimuli", size=(35,-1), style=wx.TE_PROCESS_ENTER)
        txt.Bind(wx.EVT_TEXT_ENTER, self.onClickApply) 
        self.gbs.Add(txt, pos=(row,col), flag=wx.ALL, border=bw)
        col += 1
        sTxt = wx.StaticText(self.setting_p, -1, "")
        self.gbs.Add(sTxt, pos=(row,col), flag=wx.ALL, border=bw)

        row += 1; col = 0
        btn = wx.Button(self.setting_p, -1, "Apply", size=(self.setting_p_sz[0]-40,-1))
        btn.Bind(wx.EVT_LEFT_DOWN, self.onClickApply)
        self.gbs.Add(btn, pos=(row,col), span=(1,2), flag=wx.ALL|wx.ALIGN_RIGHT|wx.ALIGN_TOP, border=0)
        col += 2 
        sTxt = wx.StaticText(self.setting_p, -1, "")
        self.gbs.Add(sTxt, pos=(row,col), flag=wx.ALL, border=bw)

        row += 1; col = 0 
        sTxt = wx.StaticText(self.setting_p, -1, "")
        self.gbs.Add(sTxt, pos=(row,col), span=(1,3), flag=wx.ALL, border=bw)

        row += 1; col = 0 
        sTxt = wx.StaticText(self.setting_p, -1, " * Response stimulus is a clickable text or image to accept user-response. If there will be no dedicated response text or image and experimental stimuli will be also used for user-response, just consider them as response stimuli in this setup window.")
        sTxt.Wrap(self.setting_p_sz[0]-50)
        self.gbs.Add(sTxt, pos=(row,col), span=(1,2), flag=wx.ALL|wx.ALIGN_TOP, border=0)
        col += 2
        sTxt = wx.StaticText(self.setting_p, -1, "")
        self.gbs.Add(sTxt, pos=(row,col), flag=wx.ALL, border=bw) 

        self.setting_p.SetSizer(self.gbs)
        self.gbs.Layout()

        okButton = wx.Button(self, wx.ID_OK, "Finish setup")
        okButton.SetPosition( (self.w_sz[0]-okButton.GetSize()[0]*2-20, self.w_sz[1]-75) )
        okButton.Bind(wx.EVT_LEFT_DOWN, self.onCheck)
        cancelButton = wx.Button(self, wx.ID_CANCEL, "Cancel")
        cancelButton.SetPosition( (okButton.GetPosition()[0]+okButton.GetSize()[0]+5, self.w_sz[1]-75) )

        self.Bind(wx.EVT_PAINT, self.onPaint)
    
    #------------------------------------------------
    
    def onPaint(self, event):
        if DEBUGGING: print('SetupStimuliDialog.onPaint()')
        
        event.Skip()
        dc = wx.PaintDC(self)
        dc.Clear()

        ### draw experimental & response stimuli
        for i in range(2):
            if i == 0:
                st = "es"
                dc.SetBrush(wx.Brush(wx.Colour(100,100,100)))
            elif i == 1:
                st = "rs"
                dc.SetBrush(wx.Brush(wx.Colour(50,50,50)))
            rects = self.return_val["rects_of_%s"%(st)]
            if rects != None:
                for idx in range(len(rects)):
                    sType = str(self.return_val["types_of_%s"%(st)][idx]) # stimulus type
                    r = rects[idx]
                    x = r[0]; y = r[1]; w = r[2]; h = r[3]
                    if sType != 'None':
                        sp = self.return_val["paths_of_%s"%(st)][idx][0] # first stimulus of the stimulus at 'idx'
                    if sType == 'None':
                        if w == -1: w = self.ds_sz[0]
                        if h == -1: h = self.ds_sz[1]
                        x = int(x*self.w_sz[0]) - w/2
                        y = int(y*self.w_sz[1]) - h/2
                        dc.DrawRectangle(x, y, w, h)
                    elif sType == 'txt':
                        if "_c" in sp: sp = sp[:sp.find("_c")] # cut off correct stimulus tag
                        font = self.parent.parent.base_script_font
                        dc.SetFont(font)
                        if w != -1:
                            sp = wordwrap(sp, w, dc)
                            nl = sp.count('\n') + 1
                            tSz = (w, font.GetPixelSize()[1]*nl)
                        else:
                            tSz = (font.GetPixelSize()[0]*len(sp), font.GetPixelSize()[1])
                        dc.SetBrush(wx.Brush(wx.Colour(50,50,50)))
                        x = x*self.parent.parent.w_sz[0]-tSz[0]/2
                        y = y*self.parent.parent.w_sz[1]-tSz[1]/2
                        dc.DrawText(sp, x, y)
                    elif sType in ['img', 'snd', 'mov']:
                        if sType == 'img': img = load_img(sp)
                        elif sType == 'snd': img = load_img("input/img_musical_note.png")
                        elif sType == 'mov': img = load_img("input/img_movie.png")
                        new_sz = list(img.GetSize())
                        if w != -1: new_sz[0] = w
                        if h != -1: new_sz[1] = h
                        if w != -1 or h != -1: img = img.Rescale(new_sz[0], new_sz[1])
                        changed_img_sz = img.GetSize()
                        x = int(x*self.parent.parent.w_sz[0])-changed_img_sz[0]/2
                        y = int(y*self.parent.parent.w_sz[1])-changed_img_sz[1]/2
                        bmp = wx.Bitmap(img)
                        dc.DrawBitmap(bmp, x, y, True)
                    elif sType == 'slider':
                        if w == -1: w = 300
                        h = self.sliders[idx].GetSize()[1]
                        x = x*self.parent.parent.w_sz[0]-w/2
                        y = y*self.parent.parent.w_sz[1]-h/2
                        if self.sliders[idx] != None:
                            self.sliders[idx].SetPosition((x,y))
                            self.sliders[idx].SetSize((w,h))
            
    #------------------------------------------------
    
    def onShowHideParamPanel(self, event):
        if DEBUGGING: print('SetupStimuliDialog.onShowHideParamPanel()')

        pos = list(self.setting_p.GetPosition())
        if self.showHideAnimation == "":  # not during animation
            lbl = self.showHideBtn.GetLabel()
            if pos[0] < 0: self.showHideAnimation = "show"
            else: self.showHideAnimation = "hide"
        w = self.setting_p_sz[0]
        btn_w = self.showHideBtn.GetSize()[0]
        mDist = (w-btn_w) / self.ani_fr 
        if self.showHideAnimation == "show":
            pos[0] += mDist
            self.setting_p.SetPosition(tuple(pos))
            if pos[0] >= 5:
                self.showHideAnimation = ""
                set_img_for_btn(path.join(self.e_gui_path, "input/img_arrow_left.png"), self.showHideBtn)
            else: wx.CallLater(self.ani_intv, self.onShowHideParamPanel, None)
        elif self.showHideAnimation == "hide": 
            pos[0] -= mDist
            self.setting_p.SetPosition(tuple(pos))
            if pos[0] <= -w+btn_w+mDist:
                self.showHideAnimation = ""
                set_img_for_btn(path.join(self.e_gui_path, "input/img_arrow_right.png"), self.showHideBtn)
            else: wx.CallLater(self.ani_intv, self.onShowHideParamPanel, None)
    
    #------------------------------------------------
    
    def onClickApply(self, event):
        ''' clicked apply button 
        (for number_of_trials, number_of_experimental_stimuli or number_of_response_stimuli)
        '''
        if DEBUGGING: print('SetupStimuliDialog.onClickApply()')

        for key in self.main_param:
            valObj = wx.FindWindowByName( key, self )
            val = valObj.GetValue()
            val_int = None
            try: val_int = int(val)
            except: pass
            if val_int == None:
                valObj.SetValue("0")
                show_msg("%s has invalid number"%(key))
                return
            self.return_val[key] = val_int

        #objName = event.GetEventObject().GetName()
        #if objName.startswith("apply_"): key = objName.replace("apply_", "")
        #else: key = objName
        
        if key == "number_of_trials":
        # if number_of_trials chnages, init other numbers
            self.return_val["number_of_experimental_stimuli"] = 0
            valObj = wx.FindWindowByName( "number_of_experimental_stimuli", self )
            valObj.SetValue("0")
            self.return_val["number_of_response_stimuli"] = 0
            valObj = wx.FindWindowByName( "number_of_response_stimuli", self )
            valObj.SetValue("0")

        self.return_val["types_of_es"] = []
        self.return_val["types_of_rs"] = []
        self.return_val["rects_of_es"] = []
        self.return_val["rects_of_rs"] = []
        self.return_val["paths_of_es"] = []
        self.return_val["paths_of_rs"] = []
        self.sliders = []

        ### set up rects
        for txt in self.esRectTxts: txt.Destroy()
        self.esRectTxts = []
        for btn in self.esOpenBtns: btn.Destroy()
        self.esOpenBtns = []
        for txt in self.rsRectTxts: txt.Destroy()
        self.rsRectTxts = []
        for btn in self.rsOpenBtns: btn.Destroy()
        self.rsOpenBtns = []
        for btn in self.rsCorrectBtns: btn.Destroy()
        self.rsCorrectBtns = []
        nes = self.return_val["number_of_experimental_stimuli"]
        nrs = self.return_val["number_of_response_stimuli"] 
        num_of_stim = nes + nrs
        if num_of_stim == 1: rects = [[0.5, 0.5, -1, -1]]
        elif num_of_stim == 2:
            if nes == 1 and nrs == 1: rects = [[0.5, 0.5, -1, -1], [0.5, 0.8, -1, -1]]
            else: rects = [[0.25, 0.5, -1, -1], [0.75, 0.5, -1, -1]]
        elif num_of_stim == 3: rects = [[0.5, 0.5, -1, -1], [0.25, 0.8, -1, -1], [0.75, 0.8, -1, -1]]
        else:
            columns = sqrt(num_of_stim)
            rows = int(columns)
            if columns % 1 > 0: columns += 1
            columns = int(columns)
            rects = []
            for r in range(rows):
                if r == rows-1: # last row
                    w = 1.0 / (num_of_stim-columns*(rows-1))
                else:
                    w = 1.0 / columns # width for each stimulus
                h = 1.0 / rows # height for each stimulus
                for c in range(columns):
                    rects.append( [w*c+w/2, h*r+h/2, -1, -1] )
        self.return_val["rects_of_es"] = rects[:nes]
        self.return_val["rects_of_rs"] = rects[nes:]
        for si in range(num_of_stim):
            if si < nes: tName = "es_rect_%i"%(si)
            else: tName = "rs_rect_%i"%(si-nes)
            r = rects[si]
            txt = wx.TextCtrl(self, -1, value="[%.3f, %.3f, -1, -1]"%(r[0], r[1]), name=tName, size=(170,-1), style=wx.TE_PROCESS_ENTER)
            txt.Bind(wx.EVT_TEXT_ENTER, self.onRectTextChange)
            pos = ( int(self.w_sz[0]*r[0])-txt.GetSize()[0]/2, int(self.w_sz[1]*r[1])+self.ds_sz[1]/2+5 )
            txt.SetPosition(pos)
            bName = tName.replace("_rect_", "_open_btn_")
            oBtn = wx.Button(self, -1, label='', name=bName, size=(20,20))
            oBtn.Bind(wx.EVT_LEFT_DOWN, self.onSelectStim)
            set_img_for_btn(path.join(self.e_gui_path, "input/img_open_folder.png"), oBtn)
            pos = ( int(self.w_sz[0]*r[0])-oBtn.GetSize()[0]/2, int(self.w_sz[1]*r[1])-oBtn.GetSize()[1]/2-self.ds_sz[1]/2 )
            oBtn.SetPosition(pos)
            lName = tName.replace("_rect_", "_stim_list_") 
            if si >= nes: # this is response stimulus
                bName = tName.replace("_rect_", "_correct_btn_")
                cBtn = wx.Button(self, -1, label='', name=bName, size=(20,20))
                cBtn.Bind(wx.EVT_LEFT_DOWN, self.onSelectCorrectStim)
                set_img_for_btn(path.join(self.e_gui_path, "input/img_apply.png"), cBtn)
                pos = ( int(self.w_sz[0]*r[0])+self.ds_sz[0]/2-cBtn.GetSize()[0], int(self.w_sz[1]*r[1])-cBtn.GetSize()[1]/2-self.ds_sz[1]/2 )
                cBtn.SetPosition(pos)
            if si < nes: # this is experimental stimulus
                self.esRectTxts.append(txt)
                self.esOpenBtns.append(oBtn)
                self.return_val["types_of_es"].append(None)
                self.return_val["paths_of_es"].append([])
            else: # response stimulus
                self.rsRectTxts.append(txt)
                self.rsOpenBtns.append(oBtn)
                self.rsCorrectBtns.append(cBtn)
                self.sliders.append(None)
                self.return_val["types_of_rs"].append(None)
                self.return_val["paths_of_rs"].append([])

        self.Refresh()
        self.setting_p.Raise()
    
    #------------------------------------------------
    
    def onRectTextChange(self, event):
        ''' apply manually changed stimulus rect 
        '''
        if DEBUGGING: print('SetupStimuliDialog.onRectTextChange()')

        obj = event.GetEventObject()
        objName = obj.GetName()
        val = obj.GetValue().strip('[]')
        r = val.split(",")
        if len(r) != 4: return
        try:
            r[0] = float(r[0]); r[1] = float(r[1])
            r[2] = int(r[2]); r[3] = int(r[3])
        except:
            show_msg("Invalid number")
            return
        if r[0] < 0.0 or r[0] > 1.0 or r[1] < 0.0 or r[1] > 1.0:
            show_msg("Invalid x/y")
            return
        if r[2] < -1 or r[2] == 0 or r[3] < -1 or r[3] == 0:
            show_msg("Invalid width/height")
            return
        if r[3] == -1: hh = self.ds_sz[1] 
        else: hh = r[3]/2
        pos = ( int(self.w_sz[0]*r[0])-obj.GetSize()[0]/2, int(self.w_sz[1]*r[1])+hh/2+5 )
        obj.SetPosition(pos)
        btn = wx.FindWindowByName( objName.replace("_rect_", "_open_btn_"), self )
        pos = ( int(self.w_sz[0]*r[0])-btn.GetSize()[0]/2, int(self.w_sz[1]*r[1])-btn.GetSize()[1]/2-self.ds_sz[1]/2 )
        btn.SetPosition(pos)
        if objName.startswith('rs'): # response stimulus rect
            btn = wx.FindWindowByName( objName.replace("_rect_", "_correct_btn_"), self )
            pos = ( int(self.w_sz[0]*r[0])+self.ds_sz[0]/2-btn.GetSize()[0], int(self.w_sz[1]*r[1])-btn.GetSize()[1]/2-self.ds_sz[1]/2 )
            btn.SetPosition(pos)
        idx = int(objName.split("_")[-1])
        if objName.startswith('es_'): self.return_val["rects_of_es"][idx] = r
        elif objName.startswith('rs_'): self.return_val["rects_of_rs"][idx] = r
        self.Refresh()
    
    #------------------------------------------------
    
    def query(self, flag, size, *args):
        if DEBUGGING: print('SetupStimuliDialog.query()')
        
        dlg = QueryDialog(self, -1, "Query-%s"%(flag), flag, size, *args)
        result = dlg.ShowModal()
        info = None
        if result == wx.ID_OK: info = dlg.GetValues()
        dlg.Destroy()
        return info

    #------------------------------------------------
    
    def onSelectStim(self, event):
        ''' select and set up stimuli (selecting folder, entering texts, choosing slider, choosing correct response, etc)
        '''
        if DEBUGGING: print('SetupStimuliDialog.onSelectStim()')
        
        obj = event.GetEventObject()
        objName = obj.GetName()
     
        ss = objName.split("_")
        sTag = ss[0] # es (experimental stimuli) or rs (response stimuli)
        sIdx = int(ss[-1])
        tKey = "types_of_%s"%(sTag)
        pKey = "paths_of_%s"%(sTag)
        rKey = "rects_of_%s"%(sTag)

        if sTag == "rs" and self.sliders[sIdx] != None:
            self.sliders[sIdx].Destroy()
            self.sliders[sIdx] = None

        type_of_stim = self.query("type_of_stim", (350,150), sTag)
        if type_of_stim == None:
            return
        elif type_of_stim == "text":
            ### enter text stimuli
            txt_stim = self.query("text_stim", (500,350))
            if txt_stim == None: return
            txt_stim = [x.strip() for x in txt_stim.split(",")]
            if len(txt_stim) != 1 and len(txt_stim) != self.return_val["number_of_trials"]:
                show_msg("Number of stimuli should match with 'Number of trials' you entered. (Or one in case the same stimulus is used for all trials).")
                return
            self.return_val[tKey][sIdx] = "txt"
            self.return_val[pKey][sIdx] = txt_stim

        elif type_of_stim == "slider":
            self.return_val[tKey][sIdx] = "slider"
            self.return_val[pKey][sIdx] = ["slider"]
            r = self.return_val[rKey][sIdx]
            w = r[2]
            if w == -1: w = 300
            self.sliders[sIdx] = wx.Slider(self, -1, 5, 0, 10, pos=(1, 1), size = (w, -1), style = wx.SL_HORIZONTAL | wx.SL_AUTOTICKS)
            x = r[0]*self.parent.parent.w_sz[0]-w/2
            y = r[1]*self.parent.parent.w_sz[0]-self.sliders[sIdx].GetSize()[1]/2
            self.sliders[sIdx].SetPosition((x,y))
            rt = [x.strip() for x in self.rsRectTxts[sIdx].GetValue().strip("[]").split(",")]
            self.rsRectTxts[sIdx].SetValue( "[%s, %s, %i, %s]"%(rt[0], rt[1], w, rt[3]) )
            self.return_val[rKey][sIdx] = [float(rt[0]), float(rt[1]), w, int(rt[3])]

        else: # image
            ### choose a folder, containing stimuli files for this stimulus 
            dlg = wx.DirDialog(self, "Choose a folder for this stimulus.", self.e_gui_path, wx.DD_DEFAULT_STYLE|wx.DD_DIR_MUST_EXIST)
            if dlg.ShowModal() == wx.ID_CANCEL: return
            cnt = [0,0,0] # img, snd, mov
            cnt_lbl = ["img", "snd", "mov"]
            sfp = [] # stimuli file path 
            fl = sorted(glob(path.join(dlg.GetPath(), "*.*")))
            for f in fl:
                ext = path.basename(f).split('.')[-1]
                if ext in self.parent.parent.allowed_img_ext: cnt[0] += 1 
                elif ext in self.parent.parent.allowed_snd_ext: cnt[1] += 1 
                elif ext in self.parent.parent.allowed_mov_ext: cnt[2] += 1 
            if sum(cnt) == 0:
                show_msg("No stimuli files is recognized in the selected folder.")
                return
            max_cnt = max(cnt)
            if max_cnt != 1 and max_cnt != self.return_val["number_of_trials"]:
                show_msg("Number of stimuli should match with 'Number of trials' you entered. (Or one in case the same stimulus is used for all trials).")
                return
            st = cnt_lbl[cnt.index(max_cnt)] # stimulus type
            if sTag == "rs" and st != 'img':
                show_msg("Response stimulus could be image, text, or slider. Sound or movie is not allowed.")
                return
            if st == "img": allowed_ext = self.parent.parent.allowed_img_ext
            elif st == "snd": allowed_ext = self.parent.parent.allowed_snd_ext
            elif st == "mov": allowed_ext = self.parent.parent.allowed_mov_ext
            for f in fl:
                ext = path.basename(f).split('.')[-1]
                if ext in allowed_ext: sfp.append(f)
            self.return_val[tKey][sIdx] = st 
            self.return_val[pKey][sIdx] = sfp
            tName = "%s_rect_%i"%(sTag, sIdx)
            rectObj = wx.FindWindowByName( tName, self )
            if st == "snd": rectObj.Disable()
            else: rectObj.Enable() 

        if type_of_stim == "image": self.rsCorrectBtns[sIdx].Show()
        else: self.rsCorrectBtns[sIdx].Hide()
        
        self.Refresh()
    
    #------------------------------------------------
    
    def onSelectCorrectStim(self, event):
        if DEBUGGING: print('SetupStimuliDialog.onSelectCorrectStim()')
        
        objName = event.GetEventObject().GetName()
        clicked_idx = int(objName.split("_")[-1]) # index of clicked response stimulus
        for cbi in range(len(self.rsCorrectBtns)):
            cBtn = self.rsCorrectBtns[cbi]
            if cbi == clicked_idx:
                if self.rsCorrIdx != cbi:
                    set_img_for_btn(path.join(self.e_gui_path, "input/img_apply_c.png"), cBtn)
                    self.rsCorrIdx = clicked_idx
                else:
                    set_img_for_btn(path.join(self.e_gui_path, "input/img_apply.png"), cBtn)
                    self.rsCorrIdx = -1
            else:
                set_img_for_btn(path.join(self.e_gui_path, "input/img_apply.png"), cBtn)
    
    #------------------------------------------------
    
    def onCheck(self, event):
        ''' Fisnish_setup button is clicked.
        Process some check-up procedures.
        '''
        if DEBUGGING: print('SetupStimuliDialog.onCheck()')
        
        rv = self.return_val
        if rv["number_of_trials"]==0 or rv["number_of_experimental_stimuli"]+rv["number_of_response_stimuli"]==0:
            show_msg("'Number of trials' should be greater than zero and there should be, at least, one stimulus.")
            return

        if 'mov' in rv["types_of_es"]:
            rslt = self.query("movie_module", (300,300))
            if rslt == None: return
            rv["movie_module"] = rslt

        ### if response stimulus (such as 'yes/no' string) is only one (meaning the same string will be used for all trials)
        ### make it for the number of trials. e.g.) ['yes']*3 ---> ['yes', 'yes', 'yes'] (when number_of_trials == 3)
        if rv["number_of_trials"] > 1:
            for pi in range(len(rv["paths_of_rs"])):
                if len(rv["paths_of_rs"][pi]) == 1:
                    rv["paths_of_rs"][pi] = rv["paths_of_rs"][pi] * rv["number_of_trials"]

        if self.rsCorrIdx != -1: # there is an index indicating a folder with correct responses
            if rv["types_of_rs"][self.rsCorrIdx] != "txt": 
                ### add the correct response tag, "_c", at the end of filename
                for f in rv["paths_of_rs"][self.rsCorrIdx]:
                    bn = path.basename(f)
                    ext = bn.split(".")[-1]
                    new_bn = bn.replace("."+ext, "")
                    if (new_bn[-2:]=="_c") or ("_c-" in new_bn): continue # filename already has the correct response tag 
                    new_bn = new_bn + "_c." + ext 
                    new_f = f.replace(bn, new_bn)
                    rename(f,  new_f)
                    rv["paths_of_rs"] = new_f
        event.Skip()
    
    #------------------------------------------------
    
    def GetValues(self):
        if DEBUGGING: print('SetupStimuliDialog.GetValues()')
        return self.return_val 

#====================================================

class QueryDialog(wx.Dialog):
    def __init__(self, parent=None, id=-1, title="Query", flag="", size=(300,200), *args):
        if DEBUGGING: print('QueryDialog.__init__()')
        self.parent = parent
        self.flag = flag
        wx.Dialog.__init__(self, parent, id, title, size=size)
        self.gbs = wx.GridBagSizer(0,0)
        bw = 5
        row=0; col=0
        if flag == "type_of_stim":
            sTag = args[0]
            sTxt = wx.StaticText(self, -1, "Type of stimulus")
            self.gbs.Add(sTxt, pos=(row,col), flag=wx.ALL, border=bw)
            col += 1
            if sTag == "es": _choices = ["image/sound/movie", "text"]
            elif sTag == "rs": _choices = ["image", "text", "slider"]
            self.choiceCtrl = wx.Choice(self, -1, choices = _choices)
            self.gbs.Add(self.choiceCtrl , pos=(row,col), flag=wx.ALL, border=bw)
            row += 1; col = 0
        elif flag == "text_stim":
            sTxt = wx.StaticText(self, -1, "Please enter text stimuli. Text for each trial should be separated by comma. If the same text will be used for all tirals, you can enter just one text.")
            sTxt.Wrap(size[0]-50)
            self.gbs.Add(sTxt, pos=(row,col), span=(1,2), flag=wx.ALL, border=bw)
            row += 1
            self.textCtrl = wx.TextCtrl(self, -1, value = "", size=(size[0]-50,200), style = wx.TE_LEFT|wx.TE_MULTILINE)
            self.gbs.Add(self.textCtrl, pos=(row,col), span=(1,2), flag=wx.ALL, border=bw)
            row += 1
        elif flag == "movie_module":
            sTxt = wx.StaticText(self, -1, "Choose a video module to play movie stimulus.")
            sTxt.Wrap(size[0]-50)
            self.gbs.Add(sTxt, pos=(row,col), span=(1,2), flag=wx.ALL, border=bw)
            row += 1
            self.choiceCtrl = wx.Choice(self, -1, choices = ['wx.media', 'vlc'])
            self.gbs.Add(self.choiceCtrl, pos=(row,col), span=(1,2), flag=wx.ALL, border=bw)
            row += 1
            sTxt = wx.StaticText(self, -1, "* Note: wx.media cannot resize video. It will show video with its original size. If you give smaller rect, part of video will not be visible. You might want to resize video files to the size you want to show, using other programs such as ffmpeg. If you choose VLC, VLC will show video with the size you entered in rect.")
            sTxt.Wrap(size[0]-50)
            self.gbs.Add(sTxt, pos=(row,col), span=(1,2), flag=wx.ALL, border=bw)
            row += 1

        okButton = wx.Button(self, wx.ID_OK, "OK")
        okButton.SetDefault()
        self.gbs.Add(okButton, pos=(row,col), flag=wx.ALL, border=bw)
        col += 1
        cancelButton = wx.Button(self, wx.ID_CANCEL, "Cancel")
        self.gbs.Add(cancelButton, pos=(row,col), flag=wx.ALL, border=bw)
        self.SetSizer(self.gbs)
        self.gbs.Layout()
        self.SetPosition( (parent.w_sz[0]/2-self.GetSize()[0]/2, parent.w_sz[1]/2-self.GetSize()[1]/2) )

    #------------------------------------------------
    
    def GetValues(self):
        if DEBUGGING: print('QueryDialog.GetValues()')
        if self.flag in ["type_of_stim", "movie_module"]:
            return self.choiceCtrl.GetStringSelection()
        elif self.flag == "text_stim":
            return self.textCtrl.GetValue()

#====================================================

if __name__ == "__main__": pass
