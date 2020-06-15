# coding: UTF-8

#----------------------------------------------
# !!! DO NOT EDIT any comment with '#[flag' !!!
#----------------------------------------------

#[flag:import-begin] !!! DO NOT EDIT THIS LINE !!!
import sys, wave, queue, string
from os import path, mkdir, remove, getcwd
from random import uniform, randint, shuffle, choice
from time import time, sleep
from datetime import datetime
from glob import glob
from copy import copy
from threading import Thread

import wx # External package, wxPython. You can download it from http://www.wxpython.org/
#[flag:import-end] !!! DO NOT EDIT THIS LINE !!!


# ===========================================================
#[flag:class-begin] !!! DO NOT EDIT THIS LINE !!!

class Experimenter(wx.Frame):
    def __init__(self):
        ''' Class for running experiment
        '''
        self.screenPos = (0, 0)
        self.screenSize = (wx.Display(0).GetGeometry()[2], wx.Display(0).GetGeometry()[3])
        wx.Frame.__init__(self, None, -1, 'Experiment', pos = self.screenPos, size = self.screenSize)
        self.ShowFullScreen(True, style=wx.FULLSCREEN_ALL)
        self.mainPanel = wx.Panel(self, pos = (0,0), size = (self.GetSize()[0], self.GetSize()[1]))
        self.mainPanel_bgcolor = '#AAAABB'
        self.trigger_img_path = 'input/trigger.png' #[flag_marker:trigger]
        self.mainPanel.SetBackgroundColour(self.mainPanel_bgcolor)
        font_size = 20
        self.font = wx.Font(font_size, wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.FONTWEIGHT_NORMAL, False, "Courier", wx.FONTENCODING_SYSTEM)
        self.get_subject_info()
        ### key binding
        key_list = ['CTRL+Q', 'CTRL+S', 'CTRL+L'] #[flag:key_bindings] #[flag_marker:key_bindings] #[flag_marker:key_stroke]
        accel_tbl_key_list = []
        self.keyId = {}
        for key in key_list:
            keys_ = [ item.strip().upper() for item in key.split('+') ]
            keyId = wx.NewIdRef(count=1)
            self.keyId[keyId] = key
            self.Bind(wx.EVT_MENU, self.onKeyPress, id=keyId)
            if keys_[0] == 'CTRL': modifier = wx.ACCEL_CTRL
            elif keys_[0] == 'SHIFT': modifier = wx.ACCEL_SHIFT
            elif keys_[0] == 'ALT': modifier = wx.ACCEL_ALT
            else: modifier = wx.ACCEL_NORMAL
            if keys_[1] in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890': key_ = ord(keys_[1])
            else: exec("key_ = wx.WXK_%s"%(keys_[1]))
            accel_tbl_key_list.append( (modifier, key_, keyId) )
        accel_tbl = wx.AcceleratorTable(accel_tbl_key_list)
        self.SetAcceleratorTable(accel_tbl)
        self.mainPanel.SetFocus()
        ### start experiment
        if self.subject_info == None:
            wx.CallLater(10, self.Destroy)
        else:
            wx.CallLater(10, self.init_expmt)
            
    # --------------------------------------------------
    
    def init_expmt(self):
        ### experiment setting
        self.feedback = "visual" #[flag:feedback] #[flag_marker:feedback]
        self.vis_neg_fb_time = 500 # time (in ms) for visual negative feedback
        self.inter_trial_interval = 1000 #[flag:inter_trial_interval] #[flag_marker:inter_trial_interval] inter-trial-interval in millisecond
        self.number_of_stimuli_per_trial = 1 #[flag:number_of_stimuli_per_trial] #[flag_marker:number_of_stimuli_per_trial]
        self.number_of_trials = 1 #[flag:number_of_trials] #[flag_marker:number_of_trials]
        self.randomize_trials = True #[flag:randomize_trials] #[flag_marker:randomize_trials]
        self.randomize_stimuli = False #[flag:randomize_stimuli] #[flag_marker:randomize_stimuli]
        self.randomize_stimuli_idx = [0] #[flag:randomize_stimuli_idx] #[flag_marker:randomize_stimuli_idx] Normally all stimuli will be randomized. But this list of indices does not include all stimuli indices, stimuli only with these indices will be randomized, while other stimuli will be fixed. 
        self.reaction_time_delay = 0 #[flag:reaction_time_start] #[flag_marker:reaction_time_start]
        stimuliFilePaths = [] #[flag:setup_stimuli] #[flag_marker:setup_stimuli]
        self.trial_timeout = -1 #[flag:trial_timeout] #[flag_marker:trial_timeout] Timeout time in milliseconds, -1 means there's no time-out.
        self.user_response = "mouse_click" #[flag:user_response] #[flag_marker:user_response]
        self.user_response_start = 0 #[flag:user_response_start] #[flag_marker:user_response_start]
        self.correction_trial = False #[flag:correction_trial] #[flag_marker:correction_trial]
        self.is_ct_correction_trial = False # whether the current trial is correction-trial or not
        self.trigger = False #[flag:trigger] #[flag_marker:trigger] show trigger image to start trial
        self.is_ct_trig_clicked = False # whether the current trial's trigger image was clicked
        self.back_to_trigger_time = 5000 #[flag_marker:trigger] # in ms. How long program waits for a response after the trigger image is clicked
        self.train_or_test = False #[flag:train_or_test] #[flag_marker:train_or_test] if this is True, certain percetage will be test trials and others will be training trials. Check 'start_session' function to see how it's determined.
        ### stimuli parameters
        clickable = [] #[flag:clickable] #[flag_marker:clickable]
        present_time = [] #[flag:present_time] #[flag_marker:present_time]
        rect = [] #[flag:rect] #[flag_marker:rect]
        s_type = [] #[flag:s_type] #[flag_marker:s_type]
        
        ### set up expmt_details (stimulus filepath, correct_response and how to present the stimulus)
        self.expmt_details = {} #[flag_marker:Stimuli_set-up]
        for ti in range(len(stimuliFilePaths)): #[flag_marker:setup_stimuli] #[flag_marker:Stimuli_set-up]
            self.expmt_details[ti] = {} # dictionary for a trial #[flag_marker:Stimuli_set-up]
            cr = None #[flag_marker:Stimuli_set-up]
            for si in range(len(stimuliFilePaths[ti])): #[flag_marker:setup_stimuli] #[flag_marker:Stimuli_set-up]
                fp = stimuliFilePaths[ti][si] #[flag_marker:setup_stimuli] #[flag_marker:Stimuli_set-up]
                if fp == 'slider' and hasattr(self, 'slider') == False: self.init_slider(rect[si]) #[flag_marker:Stimuli_set-up]
                fn = path.basename(fp) # file name #[flag_marker:Stimuli_set-up]
                if s_type[si] != 'txt': # Text stimulus's fp is not file-path, but text itself. #[flag_marker:Stimuli_set-up]
                    ### Get rid of file extension from filename
                    ext = "."+fn.split(".")[-1] #[flag_marker:Stimuli_set-up]
                    fn = fn.replace(ext, "") #[flag_marker:Stimuli_set-up]
                _tmp = fn.split("_") #[flag_marker:Stimuli_set-up]
                # correct response is filename of a file with a marker, _c.
                # When there's no _c, but there's _c- marker, string behind _c- will be the correct response.
                if _tmp[-1] == "c": #[flag_marker:Stimuli_set-up]
                    if s_type[si] == 'txt': cr = fn.replace("_c", "") #[flag_marker:correct_response] #[flag_marker:Stimuli_set-up]
                    else: cr = fn #[flag_marker:correct_response] #[flag_marker:key_stroke] #[flag_marker:Stimuli_set-up]
                elif _tmp[-1].startswith("c-") and cr == None: cr = _tmp[-1][2:].lower() #[flag_marker:correct_response] #[flag_marker:key_stroke] #[flag_marker:Stimuli_set-up]
                self.expmt_details[ti][si] = {} # dictionary for a stimulus #[flag_marker:Stimuli_set-up]
                if s_type[si] == "txt": #[flag_marker:Stimuli_set-up]
                    # Text stimulus's fp is not file-path, but text itself.
                    # if there is a correct response tag, get rid of it from text which should be displayed as a stimulus
                    if "_c" in fp: fp = fp[:fp.find("_c")] #[flag_marker:Stimuli_set-up]
                    self.expmt_details[ti][si]["stimulus"] = fp #[flag_marker:Stimuli_set-up]
                else: #[flag_marker:Stimuli_set-up]
                    self.expmt_details[ti][si]["stimulus"] = fp #[flag_marker:Stimuli_set-up]
                if clickable != None: self.expmt_details[ti][si]["clickable"] = copy(clickable[si]) #[flag_marker:clickable] #[flag_marker:Stimuli_set-up]
                if rect != None: self.expmt_details[ti][si]["rect"] = copy(rect[si]) #[flag_marker:rect] #[flag_marker:Stimuli_set-up]
                self.expmt_details[ti][si]["present_time"] = copy(present_time[si]) #[flag_marker:present_time] #[flag_marker:Stimuli_set-up]
                self.expmt_details[ti][si]["s_type"] = copy(s_type[si]) #[flag_marker:s_type] #[flag_marker:Stimuli_set-up]
            if hasattr(self, 'slider'): self.expmt_details[ti]['correct_response'] = None # no correct response when there's a slider #[flag_marker:Stimuli_set-up]
            else: self.expmt_details[ti]['correct_response'] = cr #[flag_marker:correct_response] #[flag_marker:key_stroke] #[flag_marker:Stimuli_set-up]

        ### output path & data files setup
        fn = path.basename(sys.argv[0])
        self.output_path = "%s_result"%(fn.replace('.py',''))
        if path.isdir(self.output_path) == False: mkdir(self.output_path)
        self.expmt_start_time = get_time_stamp()
        self.expmt_result_fp = path.join(self.output_path, fn.replace('.py', '') + '_' + self.expmt_start_time + ".csv")
        self.expmt_log_fp = self.expmt_result_fp.replace('.csv', '.log')
        ### init log file entry
        _txt = "* Time-stamp (year_month_day_hour_minute_second_microsecond) was obtained from built-in <datetime> function of Python.\n"
        _txt += "* Python script file: %s\n"%(fn)
        _txt += "----------------------------\n"
        _txt += "Time-stamp, Log\n"
        _txt += "----------------------------\n"
        writeFile(self.expmt_log_fp, _txt)
        ### init result csv file entry
        _txt = "Python script file, %s\n"%(fn)
        _txt += "Experiment start time, %s\n"%self.expmt_start_time
        for key in self.subject_info: _txt += "%s, %s\n"%(key, self.subject_info[key])
        _txt += "----------------------------\nTrial_index, "
        if self.train_or_test == True: _txt += "Trial_type, " #[flag_marker:train_or_test]
        _txt += "Reaction_Time, Response_string, Correct_response, Correctness, Presented_stimuli_list\n"
        _txt += "----------------------------\n"
        writeFile(self.expmt_result_fp,  _txt)

        ### where Audio setup occurs when necessary
        self.audio = None
        _fb_snds = [] # sounds for feedback
        self.main_snd_cnt = 0
        _flag_audio_play_occurs = False
        if 'snd' in s_type: _flag_audio_play_occurs = True
        if self.feedback.lower() in ['auditory', 'both']: #[flag_marker:feedback]
            _flag_audio_play_occurs = True
            _fb_snds = [ "input/AudFB_Pos.wav", "input/AudFB_Neg.wav" ] # giving paths to the positive and negavtive feedback sounds
        if _flag_audio_play_occurs == True:
            self.audio = Output_AudioData(parent=self, output_dev_keywords=['built-in']) # initializing Output_AudioData class
            if self.audio.device_index_list == []:
                self.audio = None
            else:
                self.audio.init_sounds() # intializing or simply emptying the some sound variables of the class
                if _fb_snds != []:
                    self.audio.load_sounds(_fb_snds) # load sounds for auditory feedback
                    self.main_snd_cnt = 2 # count of main sounds, which are the sounds for Experimenter itself, such as feedback sounds.
        if ARDUINO_PORT != "": self.send_arduino_msg() #[flag_marker:arduino] # If the ARDUINO-chip is connected, activate it 
        self.start_session()

    # --------------------------------------------------        
    
    def quit_app(self):
        writeFile(self.expmt_log_fp, "%s, Experimenter.quit_app()\n"%get_time_stamp())
        self.Destroy()
        #sys.exit()

    # --------------------------------------------------

    def get_subject_info(self):
        dlg = SubjectInfoDialog()
        result = dlg.ShowModal()
        self.subject_info = None
        if result == wx.ID_OK:
            self.subject_info = dlg.GetValues() 
        dlg.Destroy()

    # --------------------------------------------------

    def start_session(self):
        writeFile(self.expmt_log_fp, "%s, Experiment.start_session()\n"%get_time_stamp())
        self.trial_cnt = 0
        
        ### procedure when 'train_or_test' is True, meaning that
        ### only certain number of trails will be actual test trials and others will be training trials
        if self.train_or_test == True: #[flag_marker:train_or_test]
        ### when 'train_or_test' is True, make 'trial_idx' with specific rules, following 'make_trial_idx' function #[flag_marker:train_or_test]
            test_trial_ratio = 0.2 # float number between 0 and 1
            self.trial_idx = []
            def make_trial_idx():
                self.trial_idx = []
                self.number_of_test_trials = int(self.number_of_trials * test_trial_ratio) #[flag_marker:number_of_trials]
                test_idx_pool = list(range(self.number_of_test_trials))
                train_idx_pool = list(range(self.number_of_trials-self.number_of_test_trials)) #[flag_marker:number_of_trials]
                for i in range(len(train_idx_pool)): train_idx_pool[i] += self.number_of_test_trials
                self.trial_idx.append( choice(train_idx_pool) ) # 1st should be a training trial
                train_idx_pool.remove(self.trial_idx[0])
                for i in range(1, self.number_of_trials): #[flag_marker:number_of_trials]
                    if self.trial_idx[i-1] < self.number_of_test_trials: # previous trial was test trial
                        if len(train_idx_pool) == 0: break
                        num = choice(train_idx_pool) # pick a training trial index
                        train_idx_pool.remove(num)
                    else:
                        if uniform(0,1) < 0.5:
                            if len(test_idx_pool) > 0:
                                num = choice(test_idx_pool) # pick a test trial index
                                test_idx_pool.remove(num)
                            else:
                                num = choice(train_idx_pool) # pick a training trial index
                                train_idx_pool.remove(num)
                        else:
                            if len(train_idx_pool) > 0:
                                num = choice(train_idx_pool)
                                train_idx_pool.remove(num)
                            else:
                                num = choice(test_idx_pool)
                                test_idx_pool.remove(num)
                    self.trial_idx.append(num)
            while len(self.trial_idx) != self.number_of_trials: make_trial_idx() #[flag_marker:number_of_trials]
        else:
            self.trial_idx = list(range(self.number_of_trials)) #[flag_marker:number_of_trials]
            if self.randomize_trials == True: shuffle(self.trial_idx) #[flag_marker:randomize_trials]

        dlg = PopupDialog(self, -1, "Note", "Experiment starts.", None, pos=(0,0), size=(350, 200), cancel_btn=False)
        dlg.ShowModal()
        dlg.Destroy()
        self.start_trial()

    # --------------------------------------------------

    def start_trial(self):
        writeFile(self.expmt_log_fp, "%s, Experimenter.start_trial()\n"%get_time_stamp())
        self.curr_ti = self.trial_idx[self.trial_cnt] # currently chosen trial index
        self.stim_cnt = 0
        writeFile(self.expmt_log_fp, "%s, Experiment.start_trial(), trial %.3i\n"%(get_time_stamp(), self.curr_ti)) 
        if (self.correction_trial == False) or (self.correction_trial == True and self.is_ct_correction_trial == False): #[flag_marker:correction_trial]
        # if correction_trial is turned off or
        # correction is on and this is the 1st attempt (= if this is the correction-trial, don't randomize)
            self.stim_idx = list(range(self.number_of_stimuli_per_trial)) #[flag_marker:number_of_stimuli_per_trial]
            if self.randomize_stimuli == True: #[flag_marker:randomize_stimuli] 
                ### randomize only indices, indicated in self.randomize_stimuli_idx
                _idx = copy(self.randomize_stimuli_idx) #[flag_marker:randomize_stimuli_idx]
                shuffle(_idx)
                for i in range(len(self.stim_idx)):
                    if self.stim_idx[i] in self.randomize_stimuli_idx: #[flag_marker:randomize_stimuli_idx]
                        self.stim_idx[i] = _idx[0]
                        _idx.pop(0)
        self.trial_correctness = "NONE"
        self.reaction_time = -1
        self.trial_start_time = -1
        self.trial_stim_timers = [] # timers of presenting stimuli
        self.trial_timers = [] # list containing all other timers used for this trial
        self.trial_txts = [] # list containing all the texts (wx.StaticText) for this trial
        self.trial_imgs = [] # list containing all the images used for this trial
        self.trial_snds = [] # list containing all the sounds used for this trial
        self.trial_movs = [] # list containing all the movies used for this trial
        if hasattr(self, 'slider'):
            ma = self.slider.GetMax(); mi = self.slider.GetMin()
            self.slider.SetValue( mi+(ma-mi)/2 ) # center the slider position 
        self.response_enabled = False
        self.response_str = '' 
        if self.trigger == True: self.is_ct_trig_clicked = False #[flag_marker:trigger]
        
        #self.flag_stim_presentation_end = False # Multiple responses could be recorded in a trial. Thus this flag is for determining whether to proceed to the 'end_trial' or not in a function, which take care of a user-response.
        # Comment out this flag for now. Currently user needs to program a bit to make multiple responses possible.
        # This flag becomes True in user response functions (onClick, onKeyPress, onSliderResponse).
        # To make multiple responses working, what ends a trial (such as number of responses or specific image click, etc) should be programmed in those user response function. 
        
        _stim = ""
        for si in range(self.number_of_stimuli_per_trial):
            _fp = str(self.expmt_details[self.curr_ti][self.stim_idx[si]]["stimulus"])
            _stim += _fp + " | "
        _stim = _stim.rstrip(" | ")
        writeFile(self.expmt_log_fp, "%s, Experiment.start_trial(), trial stimuli: %s\n"%(get_time_stamp(), str(_stim)))
        self.schedule_trial_procedure()

    # --------------------------------------------------

    def back_to_trigger_img(self): #[flag_marker:trigger]
        writeFile(self.expmt_log_fp, "%s, Experimenter.back_to_trigger_img()\n"%get_time_stamp())
        if self.response_str == "": # there has been no response
            ### delete every stimuli
            if len(self.trial_txts) > 0: self.destroy_all_txts()
            if len(self.trial_imgs) > 0: self.destroy_all_imgs()
            if len(self.trial_movs) > 0: self.destroy_all_movs()
            self.response_enabled = False # Disable the user-response
            self.is_ct_trig_clicked = False
            self.schedule_trial_procedure()

    # --------------------------------------------------

    def schedule_trial_procedure(self): #[flag_marker:Scheduling_stimuli_presentation]
        writeFile(self.expmt_log_fp, "%s, Experimenter.schedule_trial_procedure()\n"%get_time_stamp())
        if self.trigger == True and self.is_ct_trig_clicked == False: #[flag_marker:trigger]
            self.trial_timers.append( wx.CallLater(1, self.present_img_setup, -1, -1, show_trigger_img=True) ) #[flag_marker:trigger]
            self.enable_user_response() #[flag_marker:trigger]
            return #[flag_marker:trigger]
            
        for i in range(self.number_of_stimuli_per_trial): #[flag_marker:number_of_stimuli_per_trial]
            curr_sti = self.stim_idx[i] # current stimulus index
            present_time = self.expmt_details[self.curr_ti][i]["present_time"] #[flag_marker:present_time]
            s_type = self.expmt_details[self.curr_ti][curr_sti]["s_type"] #[flag_marker:s_type]
            ### presenting the stimulus
            if s_type == 'txt': #[flag_marker:s_type]
                self.trial_timers.append( wx.CallLater(present_time[0], self.present_txt_setup, i, curr_sti) ) #[flag_marker:present_time]
            elif s_type == 'img': #[flag_marker:s_type]
                self.trial_timers.append( wx.CallLater(present_time[0], self.present_img_setup, i, curr_sti) ) #[flag_marker:present_time]
            elif s_type == 'snd': #[flag_marker:s_type]
                self.trial_timers.append( wx.CallLater(present_time[0], self.present_snd_setup, curr_sti) ) #[flag_marker:present_time]
            elif s_type == 'mov': #[flag_marker:s_type]
                self.trial_timers.append( wx.CallLater(present_time[0], self.present_mov_setup, i, curr_sti) ) #[flag_marker:present_time]
            elif s_type == 'slider': self.chk_end_stim()

    # --------------------------------------------------

    def present_txt_setup(self, pos_si, si): #[flag_marker:Presenting_text]
        writeFile(self.expmt_log_fp, "%s, Experimenter.present_txt_setup()\n"%get_time_stamp())
        clickable = self.expmt_details[self.curr_ti][si]["clickable"] #[flag_marker:clickable]
        present_time = self.expmt_details[self.curr_ti][si]["present_time"] #[flag_marker:present_time]
        p_sz = self.mainPanel.GetSize()
        x = p_sz[0] * self.expmt_details[self.curr_ti][pos_si]["rect"][0] #[flag_marker:rect]
        y = p_sz[1] * self.expmt_details[self.curr_ti][pos_si]["rect"][1] #[flag_marker:rect]
        w = self.expmt_details[self.curr_ti][pos_si]["rect"][2] #[flag_marker:rect] 
        stim = self.expmt_details[self.curr_ti][si]["stimulus"]
        sTxt = wx.StaticText(self.mainPanel, -1, label=stim)
        sTxt.SetFont(self.font)
        if w == -1: sTxt.Wrap(p_sz[0]-50)
        else: sTxt.Wrap(w)
        self.trial_txts.append(sTxt)
        self.trial_txts[-1].file_name = path.basename(stim).lower() # store the text as "file_name"
        sz = self.trial_txts[-1].GetSize()
        self.trial_txts[-1].SetPosition(( x-sz[0]/2, y-sz[1]/2 ))
        if self.user_response == 'mouse_click' and clickable == True: #[flag_marker:user_response] #[flag_marker:clickable] 
            self.trial_txts[-1].Bind(wx.EVT_LEFT_UP, self.onClick)
            c = wx.Cursor(wx.CURSOR_HAND)
            self.trial_txts[-1].SetCursor(c)
        self.schedule_post_stim_presentation('img', present_time)
        
    # --------------------------------------------------

    def present_img_setup(self, pos_si, si, show_trigger_img=False): #[flag_marker:Presenting_image]
        writeFile(self.expmt_log_fp, "%s, Experimenter.present_img_setup()\n"%get_time_stamp())
        if show_trigger_img == True: #[flag_marker:trigger]
            clickable = True #[flag_marker:trigger] #[flag_marker:clickable]
            present_time = [1, -1] #[flag_marker:trigger] #[flag_marker:present_time]
            x = 0.5; y = 0.5; w = -1; h = -1 #[flag_marker:trigger]
            stim = self.trigger_img_path #[flag_marker:trigger]
        else:
            clickable = self.expmt_details[self.curr_ti][si]["clickable"] #[flag_marker:clickable]
            present_time = self.expmt_details[self.curr_ti][si]["present_time"] #[flag_marker:present_time]
            x = self.expmt_details[self.curr_ti][pos_si]["rect"][0] #[flag_marker:rect]
            y = self.expmt_details[self.curr_ti][pos_si]["rect"][1] #[flag_marker:rect]
            w = self.expmt_details[self.curr_ti][pos_si]["rect"][2] #[flag_marker:rect]
            h = self.expmt_details[self.curr_ti][pos_si]["rect"][3] #[flag_marker:rect]
            try: w = int(w); h = int(h)
            except: pass
            stim = self.expmt_details[self.curr_ti][si]["stimulus"]
        tmp_null_log = wx.LogNull() # this is for not seeing the tif Library warning
        img = wx.Image(stim, wx.BITMAP_TYPE_ANY) # Load the image
        del tmp_null_log # delete the null-log to restore the logging
        isz = list(img.GetSize())
        flag_sz_changed = False
        if type(w) == int and w > 0: isz[0] = w; flag_sz_changed = True
        if type(h) == int and h > 0: isz[1] = h; flag_sz_changed = True
        if flag_sz_changed == True: img = img.Rescale(isz[0], isz[1]) 
        isz = tuple(isz)
        imgPos = (int(self.mainPanel.GetSize()[0]*x - isz[0]/2), int(self.mainPanel.GetSize()[1]*y - isz[1]/2))
        bmp = img.ConvertToBitmap()
        self.trial_imgs.append( wx.StaticBitmap(self.mainPanel, -1, bmp, imgPos, tuple(isz)) )
        self.trial_imgs[-1].file_name = path.basename( stim.replace("."+stim.split(".")[-1],"") ) # store the image's filename without extension. 
        if self.user_response == 'mouse_click' and clickable == True:
            self.trial_imgs[-1].Bind(wx.EVT_LEFT_UP, self.onClick) #[flag_marker:user_response] #[flag_marker:clickable]
            c = wx.Cursor(wx.CURSOR_HAND)
            self.trial_imgs[-1].SetCursor(c)

        flag_chk_end_stim = not show_trigger_img #[flag_marker:trigger]
        self.schedule_post_stim_presentation('img', present_time, flag_chk_end_stim)

    # --------------------------------------------------

    def present_snd_setup(self, si): #[flag_marker:Presenting_sound]
        writeFile(self.expmt_log_fp, "%s, Experimenter.present_snd_setup()\n"%get_time_stamp())
        present_time = self.expmt_details[self.curr_ti][si]["present_time"] #[flag_marker:present_time]
        file_path = self.expmt_details[self.curr_ti][si]["stimulus"]
        dur = 0
        if self.audio != None:
            self.audio.load_sounds( [ file_path ] )
            if present_time[1] == -1: dur = self.audio.sound_lengths[-1] #[flag_marker:present_time]
            else: dur = present_time[1] - present_time[0] #[flag_marker:present_time]
            self.audio.play_sound( snd_idx = len(self.audio.wfs)-1 )
        self.schedule_post_stim_presentation('snd', present_time, dur)

    # --------------------------------------------------
    
    def present_mov_setup(self, pos_si, si): #[flag_marker:Presenting_movie]
        writeFile(self.expmt_log_fp, "%s, Experimenter.present_mov_setup()\n"%get_time_stamp())
        clickable = self.expmt_details[self.curr_ti][si]["clickable"] #[flag_marker:clickable]
        present_time = self.expmt_details[self.curr_ti][si]["present_time"] #[flag_marker:present_time]
        stim = self.expmt_details[self.curr_ti][si]["stimulus"]
        r = self.expmt_details[self.curr_ti][pos_si]["rect"] #[flag_marker:rect]
        x = int(self.mainPanel.GetSize()[0]*r[0])
        y = int(self.mainPanel.GetSize()[1]*r[1])
        self.trial_movs.append( MovPlayer(self, self.mainPanel, (x,y), (r[2],r[3])) )
        dur = self.trial_movs[-1].load(stim)
        '''
        ### disable for now. VLC object can be clicked, but not wx.media.MediaCtrl object (it accepts clicks as play/pause movie)
        if self.user_response == 'mouse_click' and clickable == True:
            if self.trial_movs[-1].m_name == 'wx.media':
                self.trial_movs[-1].Bind(wx.EVT_LEFT_UP, self.onClick) #[flag_marker:user_response] #[flag_marker:clickable]
            elif self.trial_movs[-1].m_name == 'VLC':
                self.trial_movs[-1].player.Bind(wx.EVT_LEFT_UP, self.onClick) #[flag_marker:user_response] #[flag_marker:clickable]
            c = wx.Cursor(wx.CURSOR_HAND)
            self.trial_movs[-1].SetCursor(c)
        '''
        self.trial_movs[-1].file_name = path.basename( stim.replace("."+stim.split(".")[-1],"") ) # store the filename without extension.
        self.trial_movs[-1].play()
        self.schedule_post_stim_presentation('mov', present_time, dur)

    # --------------------------------------------------
    
    def schedule_post_stim_presentation(self, stim_type, present_time, stim_dur=0, flag_chk_end_stim=True):
        chk_end_stim_time = copy(stim_dur)

        ### process user defined presentation time
        if present_time[1] != -1:
            chk_end_stim_time = present_time[1] #[flag_marker:present_time]
            if stim_type == 'txt': self.trial_timers.append( wx.CallLater(present_time[1], self.destroy_txt, self.trial_txts[-1]) )
            elif stim_type == 'img': self.trial_timers.append( wx.CallLater(present_time[1], self.destroy_img, self.trial_imgs[-1]) )
            elif stim_type == 'snd': self.trial_timers.append( wx.CallLater(present_time[1], self.audio.stop_all_curr_snds) )
            elif stim_type == 'mov': self.trial_timers.append( wx.CallLater(present_time[1], self.trial_movs[-1].stop) ) #[flag_marker:present_time]
        ### schedule checking end of presentation of all stimuli
        if flag_chk_end_stim == True:
            if chk_end_stim_time > 0: self.trial_stim_timers.append( wx.CallLater(chk_end_stim_time, self.chk_end_stim) )
            else: self.chk_end_stim()
        ### check & schedule early (meaning before end of stimuli presentation) user response, also scheduling reaction-time and timeout
        if self.user_response.lower() != 'none' and self.user_response_start < 0: #[flag_marker:user_response] #[flag_marker:user_response_start]
            if present_time[1] == -1: ur_start_time = present_time[0]+stim_dur
            if present_time[1] != -1 and present_time[1] < ur_start_time: ur_start_time = present_time[1]
            ur_start_time = max(0, ur_start_time+self.user_response_start) #[flag_marker:user_response_start]
            if ur_start_time == 0: self.enable_user_response()
            else: self.trial_timers.append( wx.CallLater(ur_start_time, self.enable_user_response) )
            rt_start_time = max(0, ur_start_time+self.reaction_time_delay) #[flag_marker:reaction_time_start]
            if rt_start_time == 0: self.set_ts_time()
            else: self.trial_timers.append( wx.CallLater(rt_start_time, self.set_ts_time) ) #[flag_marker:reaction_time_start]
            if self.trial_timeout != -1: #[flag_marker:trial_timeout]
                self.trial_timers.append( wx.CallLater(ur_start_time+self.trial_timeout, self.end_trial, 'TIMEOUT') ) #[flag_marker:trial_timeout]
         
    
    # --------------------------------------------------
    
    def chk_end_stim(self):
        ''' if no stimulus presentation is going on,
        prepare for the end of this trial (end_stim_presentation)
        '''
        writeFile(self.expmt_log_fp, "%s, Experimenter.chk_end_stim()\n"%get_time_stamp())
        self.stim_cnt += 1
        if self.stim_cnt >= self.number_of_stimuli_per_trial: # if there's no more stimuli #[flag_marker:number_of_stimuli_per_trial]
            for timer in self.trial_stim_timers:
                if timer.IsRunning() == True: return
            self.end_stim_presentation()

    # --------------------------------------------------
    
    def end_stim_presentation(self):
        writeFile(self.expmt_log_fp, "%s, Experimenter.end_stim_presentation()\n"%get_time_stamp())
        # the current trial can be ended either by a user-response or timeout time
        #self.flag_stim_presentation_end = True
        if self.user_response.lower() == 'none': self.end_trial() #[flag_marker:user_response]
      
        ### schedule user-response-start, reaction-time-start and timeout
        if self.user_response_start >= 0: #[flag_marker:user_response_start]
            if self.user_response_start == 0: self.enable_user_response() #[flag_marker:user_response_start]
            else: self.trial_timers.append( wx.CallLater(self.user_response_start, self.enable_user_response) ) #[flag_marker:user_response_start] 
            rt_start_time = max(0, self.user_response_start+self.reaction_time_delay) #[flag_marker:reaction_time_start] #[flag_marker:reaction_time_start]
            if rt_start_time == 0: self.set_ts_time()
            else: self.trial_timers.append( wx.CallLater(rt_start_time, self.set_ts_time) ) #[flag_marker:reaction_time_start]
            if self.trial_timeout != -1: #[flag_marker:trial_timeout]
                self.trial_timers.append( wx.CallLater(self.user_response_start+self.trial_timeout, self.end_trial, 'TIMEOUT') ) #[flag_marker:trial_timeout]

    # --------------------------------------------------
    
    def set_ts_time(self):
        writeFile(self.expmt_log_fp, "%s, Experimenter.set_ts_time()\n"%get_time_stamp())
        self.trial_start_time = time()

    # --------------------------------------------------
    
    def enable_user_response(self):
        writeFile(self.expmt_log_fp, "%s, Experimenter.enable_user_response()\n"%get_time_stamp())
        self.response_enabled = True
    
    # --------------------------------------------------

    def end_trial(self, response_str='', flag_end_only=False):
        writeFile(self.expmt_log_fp, "%s, Experiment.end_trial(), trial#%.3i\n"%(get_time_stamp(), self.curr_ti))
        if self.trial_start_time == -1: self.reaction_time = -1 # RT not available
        else: self.reaction_time = time() - self.trial_start_time
        for i in range(len(self.trial_timers)): self.trial_timers[i].Stop() # stop all the timers
        for i in range(len(self.trial_stim_timers)): self.trial_stim_timers[i].Stop()

        if response_str != '': # for TIMEOUT
            if self.response_str == '': self.response_str = response_str
            else: self.response_str += '/' + response_str

        ### remove stimuli of the previous trial
        if len(self.trial_txts) > 0: self.destroy_all_txts()
        if len(self.trial_imgs) > 0: self.destroy_all_imgs()
        if len(self.trial_movs) > 0: self.destroy_all_movs()
        if hasattr(self, 'audio') and self.audio != None:
            if len(self.audio.wfs) > self.main_snd_cnt:
                self.audio.stop_all_curr_snds()
                removal_indices = range( self.main_snd_cnt, len(self.audio.wfs) )
                self.audio.remove_sounds( removal_indices )

        ### stop recording if the previous trial's recording has not been done yet
        if hasattr(self, 'mic_in') and isinstance(self.mic_in, Input_AudioData) and self.mic_in.r_q != None:
            self.mic_in.r_q.put('terminate', True, None)
            self.mic_in.r_t.join()

        if flag_end_only == True: return # end all timers and stimuli, but don't proceed further

        self.determine_trial_correctness()
        self.write_response()
        if self.correction_trial == True: #[flag_marker:correction_trial] # if correction-trial is turned on
            if self.train_or_test == True: #[flag_marker:train_or_test] # there are train/test trials
                ### proceed to the next trial when it's a test trial or it's a training trial and the response was correct
                if (self.curr_ti < self.number_of_test_trials) or \
                   (self.curr_ti >= self.number_of_test_trials and self.trial_correctness in ['CORRECT','NONE']):
                    self.trial_cnt += 1
                    self.is_ct_correction_trial = False
                else:
                    self.is_ct_correction_trial = True
            else:
                ### proceed to the next trial only with correct response    
                if self.trial_correctness in ['CORRECT','NONE']:
                    self.trial_cnt += 1
                    self.is_ct_correction_trial = False
                else:
                    self.is_ct_correction_trial = True
        else:
            self.trial_cnt += 1

        ### give feedback if necessary
        time_for_feedback = self.determine_trial_feedback()
        
        total_delay = self.inter_trial_interval #[flag_marker:inter_trial_interval]
        if time_for_feedback != -1: total_delay += time_for_feedback
        ### move to the next trial or end session
        if self.trial_cnt < len(self.trial_idx): # there are more trials
            wx.CallLater(total_delay, self.start_trial)
        else:
            wx.CallLater(total_delay, self.end_session)

    # --------------------------------------------------        

    def end_session(self):
        writeFile(self.expmt_log_fp, "%s, Experiment.end_session()\n"%(get_time_stamp()))
        if hasattr(self, 'audio') and self.audio != None: self.audio.close_output_streams()
        if hasattr(self, 'mic_in'): self.mic_in.close()
        dlg = PopupDialog(self, -1, "Acknowledgement", "Experiment Finished.\nThank you for participating!", None, pos=(0,0), size=(350, 200), cancel_btn=False)
        dlg.ShowModal()
        dlg.Destroy()
        self.Destroy()
        #sys.exit()

    # --------------------------------------------------

    def determine_trial_correctness(self):
        writeFile(self.expmt_log_fp, "%s, Experiment.determine_trial_correctness()\n"%(get_time_stamp()))
        cr = self.expmt_details[self.curr_ti]["correct_response"]
        if cr == None or cr.lower() == 'none':
            self.trial_correctness = 'NONE'
        else:
            if self.response_str.lower() == cr.lower():
                self.trial_correctness = 'CORRECT'
            else:
                if self.response_str[-7:] == 'TIMEOUT': self.trial_correctness = 'TIMEOUT'
                else: self.trial_correctness = 'INCORRECT'

    # --------------------------------------------------
    
    def write_response(self): #[flag_marker:Writing_result]
    # record the result of the current trial to the result CSV file
        writeFile(self.expmt_log_fp, "%s, Experiment.write_response()\n"%(get_time_stamp()))
        ### get a list of stimuli used in this trial
        _presented_stimuli = ''
        for si in range(self.number_of_stimuli_per_trial): #[flag_marker:number_of_stimuli_per_trial]
            _fp = str(self.expmt_details[self.curr_ti][self.stim_idx[si]]["stimulus"])
            _presented_stimuli += _fp + " | "
        _presented_stimuli = _presented_stimuli.rstrip(" | ")
        # correct response of this trial
        _corr_resp = self.expmt_details[self.curr_ti]["correct_response"]
        # self.response_str: participant's responses kept as string 
        # Go to onClick('Mouse click') or other 'User Response' type functions 
        # to change how this string is collected
        _resp_str = self.response_str
        trial_type = ""
        if self.train_or_test == True: #[flag_marker:train_or_test]
            if self.curr_ti < self.number_of_test_trials: trial_type = ", [test]" #[flag_marker:train_or_test]
            else: trial_type = ", [train]" #[flag_marker:train_or_test]
        # contents will be recorded in the result file
        _txt = '%i%s, %.3f, %s, %s, %s, %s\n'%( self.curr_ti,
                                                trial_type, 
                                                self.reaction_time, 
                                                _resp_str, 
                                                _corr_resp, 
                                                self.trial_correctness, 
                                                _presented_stimuli )
        writeFile(self.expmt_result_fp,  _txt) # write to the result file

    # --------------------------------------------------

    def onClick(self, event):
        event.Skip()
        writeFile(self.expmt_log_fp, "%s, Experiment.onClick()\n"%(get_time_stamp()))
        if self.response_enabled == False: return
            
        clicked_stim_fn = event.GetEventObject().file_name # get the filename of the clicked image or movie. (simply text itself when it's a text stimulus)
        if self.trigger == True and self.is_ct_trig_clicked == False: #[flag_marker:trigger]
            self.trial_timers.append( wx.CallLater(1, event.GetEventObject().Destroy) ) #[flag_marker:trigger] # destroy the trigger image
            self.is_ct_trig_clicked = True #[flag_marker:trigger]
            self.schedule_trial_procedure() #[flag_marker:trigger]
            self.trial_timers.append( wx.CallLater(self.back_to_trigger_time, self.back_to_trigger_img) ) #[flag_marker:trigger] # the subject has to respond in certain time after touching(clicking) the trigger image
            self.response_enabled = False # disable user response for experimental stimuli presentations
        else:
            ### attach the filename of the clicked image to 'response string'
            if self.response_str == '': self.response_str = clicked_stim_fn
            else: self.response_str += '/' + clicked_stim_fn
            self.response_enabled = False # Disable the user-response
            #if self.flag_stim_presentation_end == True: self.end_trial() # if flag_end_trial is True, finish this trial
            self.end_trial()

    # --------------------------------------------------

    def onKeyPress(self, event): #[flag_marker:key_bindings] #[flag_marker:key_stroke]
        event.Skip()
        writeFile(self.expmt_log_fp, "%s, Experiment.onKeyPress()\n"%(get_time_stamp()))
        key = self.keyId[event.GetId()]
        if key == 'CTRL+Q': self.quit_app()
        elif key == 'CTRL+S': self.onSave()
        elif key == 'CTRL+L': self.onLoad()
        else:
            if self.response_enabled == True: # if user-response is enabled
                if key.startswith('NONE+'): key = key.replace('NONE+','') #[flag_marker:key_stroke]
                ### attach the pressed key to 'response string'
                if self.response_str == '': self.response_str = key #[flag_marker:key_stroke]
                else: self.response_str += '/' + key #[flag_marker:key_stroke]
                self.response_enabled = False # Disable the user-response #[flag_marker:key_stroke]
                #if self.flag_stim_presentation_end == True: self.end_trial() # if flag_end_trial is True, finish this trial #[flag_marker:key_stroke]
                self.end_trial()

    # --------------------------------------------------

    def determine_trial_feedback(self):
        writeFile(self.expmt_log_fp, "%s, Experiment.determine_trial_feedback()\n"%(get_time_stamp()))
        time_for_feedback = -1
        if self.trial_correctness == 'NONE': return -1
        if self.trial_correctness == 'CORRECT': positive_FB = True
        else: positive_FB = False
        if self.feedback.lower() in ['visual', 'auditory', 'both']: #[flag_marker:feedback]
            if self.train_or_test == True: #[flag_marker:train_or_test] # there are training/test trials 
                # give feedback only when this is a training trial
                if self.curr_ti >= self.number_of_test_trials: time_for_feedback = self.present_feedback(positive_FB)
                else: time_for_feedback = -1
            else: time_for_feedback = self.present_feedback(positive_FB)
        else:
            time_for_feedback = -1
        return time_for_feedback

    # --------------------------------------------------

    def change_bg_color(self, color):
        writeFile(self.expmt_log_fp, "%s, Experiment.change_bg_color()\n"%(get_time_stamp()))
        self.SetBackgroundColour(color)
        self.mainPanel.SetBackgroundColour(color)
        self.Refresh()

    # --------------------------------------------------

    def present_feedback(self, positive_FB=True): #[flag_marker:Presenting_feedback] 
        ''' Function for giving feedback
        '''
        writeFile(self.expmt_log_fp, "%s, Experiment.present_feedback()\n"%(get_time_stamp()))
        time_for_feedback = -1
        if positive_FB == True:
            if self.feedback.lower() in ['auditory', 'both']: #[flag_marker:feedback]
                if self.audio != None:
                    self.audio.play_sound(snd_idx=0, stream_idx=0, stop_prev_snd=True) # sound_idx(0:positive, 1:negative)
                    time_for_feedback = self.audio.sound_lengths[0]
            if ARDUINO_PORT != "": #[flag_marker:arduino]
                self.send_arduino_msg() #[flag_marker:arduino] # If the ARDUINO-chip is connected, activate it
        else:
            if self.feedback.lower() in ['auditory', 'both']: #[flag_marker:feedback]
                if self.audio != None:
                    self.audio.play_sound(snd_idx=1, stream_idx=0, stop_prev_snd=True) # sound_idx(0:positive, 1:negative), stream_idx
                    time_for_feedback = self.audio.sound_lengths[1]
            if self.feedback.lower() in ['visual', 'both']: #[flag_marker:feedback]
                self.change_bg_color('#AA0000')
                wx.CallLater(self.vis_neg_fb_time, self.change_bg_color, self.mainPanel_bgcolor)
                if time_for_feedback < self.vis_neg_fb_time+1: time_for_feedback = self.vis_neg_fb_time+1
        writeFile(self.expmt_log_fp, "%s, Experiment.present_feedback(), Positive:%s\n"%(get_time_stamp(), str(positive_FB)))
        return time_for_feedback

    # --------------------------------------------------

    def destroy_txt(self, txtObj):
    # destroy one image object
        writeFile(self.expmt_log_fp, "%s, Experiment.destroy_txt()\n"%(get_time_stamp()))
        try: txtObj.Destroy()
        except: pass
        
    # --------------------------------------------------

    def destroy_img(self, imgObj):
    # destroy one image object
        writeFile(self.expmt_log_fp, "%s, Experiment.destroy_img()\n"%(get_time_stamp()))
        try: imgObj.Destroy()
        except: pass

    # --------------------------------------------------

    def destroy_all_txts(self):
    # destroy all the texts displayed on the screen for the trial
        writeFile(self.expmt_log_fp, "%s, Experiment.destroy_all_txts()\n"%(get_time_stamp()))
        for i in range(len(self.trial_txts)):
            wx.CallLater(1, self.destroy_txt, self.trial_txts[i])
            
    # --------------------------------------------------

    def destroy_all_imgs(self):
    # destroy all the images displayed on the screen for the trial
        writeFile(self.expmt_log_fp, "%s, Experiment.destroy_all_imgs()\n"%(get_time_stamp()))
        for i in range(len(self.trial_imgs)):
            wx.CallLater(1, self.destroy_img, self.trial_imgs[i])

    # --------------------------------------------------

    def destroy_all_movs(self):
    # destroy all the movies displayed on the screen for the trial
        writeFile(self.expmt_log_fp, "%s, Experiment.destroy_all_movs()\n"%(get_time_stamp()))
        for i in range(len(self.trial_movs)):
            wx.CallLater(1, self.trial_movs[i].stop)

    # --------------------------------------------------
    
    def send_arduino_msg(self): #[flag_marker:arduino]
        writeFile(self.expmt_log_fp, "%s, Experiment.send_arduino_msg()\n"%(get_time_stamp()))
        aConn.write(ARDUINO_MSG)
        aConn.flush()

    # --------------------------------------------------

    def chooseFile(self, msg='Choose file', extension='*'):
        writeFile(self.expmt_log_fp, "%s, Experiment.chooseFile()\n"%(get_time_stamp()))
        dlg = wx.FileDialog(self, msg, getcwd(), "", "*.%s"%(extension), wx.OPEN)
        dlgResult = dlg.ShowModal()
        if dlgResult == wx.ID_OK:
            fp = dlg.GetPath()
            dlg.Destroy()
        elif dlgResult == wx.ID_CANCEL:
            fp = None
            dlg.Destroy()
        return fp

    # --------------------------------------------------

    def onSave(self):
        '''save the current point in the session and exptDetails
        '''
        writeFile(self.expmt_log_fp, "%s, Experiment.onSave()\n"%(get_time_stamp()))
        fn = path.basename(self.expmt_result_fp).replace('.csv', '.sav')
        fp = path.join(self.output_path, fn)
        f = open(fp, "w") 
        if f:
            _txt = "Python script file, %s\n"%(path.basename(sys.argv[0]))
            _txt += "Experiment start time, %s\n"%self.expmt_start_time
            for key in self.subject_info: _txt += "%s, %s\n"%(key, self.subject_info[key])
            _txt += "----------------------------\n"
            f.write(_txt)
            f.write("#SAVEDATA" + '\n')
            f.write(str(self.expmt_result_fp) + '\n')
            f.write(str(self.trial_cnt) + '\n')
            f.write( '%s\n'%(str(self.trial_idx).strip('[]')) )
            f.close()
            writeFile(self.expmt_result_fp, "# The session was saved @ %s\n"%get_time_stamp())
        else:
            writeFile(self.expmt_log_fp, "%s, unable to save.\n"%get_time_stamp())
            raise Exception("unable to save.")

        msg = "Saving complete.\nGenerated file (in the output folder):\n%s\n\nThe program will be closed."%(fn)
        dlg = PopupDialog(self, -1, "Note", msg, None, size=(400, 250), cancel_btn=False)
        dlg.ShowModal()
        dlg.Destroy()
        self.Destroy()

    # --------------------------------------------------

    def onLoad(self):
        ''' load a file to restore the point where in the session and EventFile(exptDetails)
        '''
        writeFile(self.expmt_log_fp, "%s, Experiment.onLoad()\n"%(get_time_stamp()))
        ### Warning
        msg = "WARNING : If there was any, the data of the current session will be lost."
        msg += "(The CSV and LOG files will be deleted.)\n"
        msg += "Proceed?"
        dlg = PopupDialog(self, -1, "Note", msg, None, size=(450, 200))
        result = dlg.ShowModal()
        dlg.Destroy()
        if result == wx.ID_CANCEL: return

        sav_fp = self.chooseFile("Please choose a file to load.", "sav")
        if sav_fp == None: return

        remove(self.expmt_result_fp) # delete the result file generated when this script started
        remove(self.expmt_log_fp) # delete the log file generated when this script started
        ### load the sav file
        f = open(sav_fp, "r")
        if f:
            flag_start = False
            data = []
            for line in f:
                line = line.strip()
                if flag_start:
                    data.append(line)
                if line == '#SAVEDATA': flag_start = True
            f.close()
            self.expmt_result_fp = data[0]
            self.expmt_log_fp = self.expmt_result_fp.replace('.csv', '.log')
            self.trial_cnt = int(data[1])
            self.trial_idx = [ int(ti_str) for ti_str in data[2].split(",") ]
            writeFile(self.expmt_result_fp, "# The session was loaded @ %s\n"%get_time_stamp())
        else:
            writeFile(self.expmt_log_fp, "%s, unable to load.\n"%get_time_stamp())
            raise Exception("unable to load.")
        remove(sav_fp) # delete the saved data file
        self.end_trial(flag_end_only=True)
        ### Complete message
        if self.trial_cnt == 0: t_cnt = '1st'
        elif self.trial_cnt == 1: t_cnt = '2nd'
        elif self.trial_cnt == 2: t_cnt = '3rd'
        else: t_cnt = '%ith'%((self.trial_cnt+1))
        msg = "Loading complete.\nThe %s trial will start."%(t_cnt)
        dlg = PopupDialog(self, -1, "Note", msg, None, size=(350, 200), cancel_btn=False)
        dlg.ShowModal()
        dlg.Destroy()

        self.start_trial()

    # --------------------------------------------------

    #[flag:functionInExperimenterClass-begin] !!! DO NOT EDIT THIS LINE !!!

    #[flag:functionInExperimenterClass-end] !!! DO NOT EDIT THIS LINE !!!

# ===========================================================

class Experimenter_App(wx.App):
    def OnInit(self):
        self.frame = Experimenter()
        self.frame.Show()
        self.SetTopWindow(self.frame)
        return True

# ===========================================================

class SubjectInfoDialog(wx.Dialog):
    ''' Class for taking subject information
    '''
    def __init__(self, parent = None, id = -1, title = "Paricipant Info", size = (300, 300) ):
        wx.Dialog.__init__(self, parent, id, title, size = size)
        dlgWidth = self.GetSize()[0]
        init_pos = (15, 15)
        pos = list(init_pos)
        margin = [5, 10]
        sTxt_name = wx.StaticText(self, -1, label = "ID or Name:", pos = tuple(pos))
        pos[0] += sTxt_name.GetSize()[0] + margin[0]
        self.name = wx.TextCtrl(self, value = "P.001", pos = tuple(pos))
        pos[0] = init_pos[0]
        pos[1] += self.name.GetSize()[1] + margin[1]
        sTxt_age = wx.StaticText(self, -1, label = "Age:", pos = tuple(pos))
        pos[0] += sTxt_age.GetSize()[0] + margin[0]
        self.age = wx.TextCtrl(self, value = "18", pos = tuple(pos), validator = CharValidator('digit-only'))
        pos[0] = init_pos[0]
        pos[1] += self.age.GetSize()[1] + margin[1]
        self.sex = wx.RadioBox(self, -1, "Gender:", tuple(pos), wx.DefaultSize, ["Male", "Female"])
        pos[1] += self.sex.GetSize()[1] + margin[1]
        okButton = wx.Button(self, wx.ID_OK, "OK")
        okBtnSize = okButton.GetSize()
        okButton.SetDefault()
        cancelButton = wx.Button(self, wx.ID_CANCEL, "Cancel")
        cancelBtnSize = cancelButton.GetSize()
        okButton.SetPosition( (dlgWidth - (okBtnSize[0] + cancelBtnSize[0]) - (margin[0]*2), pos[1]) )
        cancelButton.SetPosition( (dlgWidth - cancelBtnSize[0] - margin[0], pos[1]) )
        dlgHeight = pos[1] + okBtnSize[1] + margin[1]
        self.SetSize( (dlgWidth, dlgHeight+30) )
        self.Center()

    # --------------------------------------------------
    
    def GetValues(self):
        values = dict( id = self.name.GetValue(),
                       age = self.age.GetValue(),
                       sex = self.sex.GetStringSelection() )
        return values

# ===========================================================

class CharValidator(wx.Validator):
    def __init__(self, flag):
        '''This validator prevents the entry of invalid characters
        '''
        wx.Validator.__init__(self)
        self.flag = flag
        self.Bind(wx.EVT_CHAR, self.OnChar)

    def Clone(self):
        return CharValidator(self.flag)

    def Validate(self, win):
        return True

    def TransferToWindow(self):
        return True
     
    def TransferFromWindow(self):
        return True

    def OnChar(self, evt):
        keycode = evt.GetKeyCode()
        key = None
        try: key = chr(keycode)
        except: pass
        if keycode == 8 or keycode == 127 or keycode == 314 or keycode == 316: # backspace, delete, left, right arrow key
            evt.Skip()
        else:
            if key == None: return
            elif self.flag == "letter-only" and not key in string.letters: return
            elif self.flag == "digit-only" and not key in string.digits: return
            evt.Skip()

# ===========================================================

class PopupDialog(wx.Dialog):
    def __init__(self, parent = None, id = -1, title = "Message", inString = "", font = None, pos = None, size = (200, 150), cancel_btn = True):
        ''' Class for showing any message to the participant
        '''
        wx.Dialog.__init__(self, parent, id, title)
        self.SetSize(size)
        if pos == None: self.Center()
        else: self.SetPosition(pos)
        txt = wx.StaticText(self, -1, label = inString, pos = (20, 20))
        txt.SetSize(size)
        if font == None: font = wx.Font(14, wx.MODERN, wx.NORMAL, wx.FONTWEIGHT_NORMAL, False, "Arial", wx.FONTENCODING_SYSTEM)
        txt.SetFont(font)
        txt.Wrap(size[0]-30)
        okButton = wx.Button(self, wx.ID_OK, "OK")
        b_size = okButton.GetSize()
        okButton.SetPosition((size[0] - b_size[0] - 20, size[1] - b_size[1] - 40))
        okButton.SetDefault()
        if cancel_btn == True:
            cancelButton = wx.Button(self, wx.ID_CANCEL, "Cancel")
            b_size = cancelButton.GetSize()
            cancelButton.SetPosition((size[0] - b_size[0]*2 - 40, size[1] - b_size[1] - 40))
        self.Center()

# ===========================================================
#[flag:class-end] !!! DO NOT EDIT THIS LINE !!!


# --------------------------------------------------
#[flag:function-begin] !!! DO NOT EDIT THIS LINE !!!

def get_time_stamp(flag_ms=False):
    ''' returns the timestamp of the current time
    '''
    ts = datetime.now()
    ts = ('%.4i_%.2i_%.2i_%.2i_%.2i_%.2i')%(ts.year, ts.month, ts.day, ts.hour, ts.minute, ts.second)
    if flag_ms == True: ts += '_%.6i'%(ts.microsecond)
    return ts

# --------------------------------------------------

def writeFile(file_path, txt):
    ''' Function for writing texts into a file
    '''
    file = open(file_path, 'a')
    if file:
        file.write(txt)
        file.close()
    else:
        raise Exception("unable to open [" + file_path + "]")

# --------------------------------------------------
#[flag:function-end] !!! DO NOT EDIT THIS LINE !!!


if __name__ == "__main__":
    #[flag:init-begin] !!! DO NOT EDIT THIS LINE !!!
    ARDUINO_PORT = "" #[flag_marker:arduino] # port name for ARDUINO-chip 
    #[flag:init-end] !!! DO NOT EDIT THIS LINE !!!
    app = Experimenter_App(redirect = False)
    app.MainLoop()


