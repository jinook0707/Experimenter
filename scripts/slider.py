    # --------------------------------------------------
    #[flag:functionInExperimenterClass-begin] !!! DO NOT EDIT THIS LINE !!!
    
    def init_slider(self, rect):
        self.slider = wx.Slider(self.mainPanel, -1, value=5, minValue=0, maxValue=10, pos=(0, 0), size = (rect[2], -1), style = wx.       SL_HORIZONTAL | wx.SL_AUTOTICKS )
        self.slider.Bind(wx.EVT_SLIDER, self.onSliderResponse)
        x = int(self.mainPanel.GetSize()[0]*rect[0] - rect[2]/2)
        y = int(self.mainPanel.GetSize()[1]*rect[1] - self.slider.GetSize()[1]/2)
        self.slider.SetPosition((x,y))
        '''
        wx.StaticText(self.mainPanel, -1, "min", pos = (x, y+labelOffset))
        wx.StaticText(self.mainPanel, -1, "max", pos = (x+w-30, y+labelOffset))
        wx.StaticText(self.mainPanel, -1, label, pos = (x+int(w/2.0)+labelOffset, 10))
        self.slider.SetTickFreq(5, 1) # only avaiable for MSW
        '''
    
    # --------------------------------------------------
    
    def onSliderResponse(self, event):
        writeFile(self.expmt_log_fp, "%s, Experiment.onSliderResponse()\n"%(get_time_stamp()))
        if self.response_enabled == False:
            ma = self.slider.GetMax(); mi = self.slider.GetMin()
            self.slider.SetValue( mi+(ma-mi)/2 ) # center the slider position 
            return
        mouseState = wx.GetMouseState()
        if mouseState.LeftIsDown() == True or mouseState.RightIsDown() == True: return
        # Sliders send a stream of events to both mouse down and drag events. Only take a final value by checking mouse states
        event.Skip()
            
        slider_value = str(self.slider.GetValue())
        if self.response_str == '': self.response_str = str(slider_value)
        else: self.response_str += '/' + str(slider_value)
        self.response_enabled = False # Disable the user-response
        #if self.flag_stim_presentation_end == True: self.end_trial() # if flag_end_trial is True, finish this trial
        self.end_trial()
    
    #[flag:functionInExperimenterClass-end] !!! DO NOT EDIT THIS LINE !!!
