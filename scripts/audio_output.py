#[flag:import-begin] !!! DO NOT EDIT THIS LINE !!!
import pyaudio # External package, PyAudio. You can download it from http://people.csail.mit.edu/hubert/pyaudio/
#[flag:import-end] !!! DO NOT EDIT THIS LINE !!!

# ===========================================================
#[flag:class-begin] !!! DO NOT EDIT THIS LINE !!!

class Output_AudioData: #[flag:audio_output]
    def __init__(self, parent, output_dev_keywords=['built-in'], sample_width=2, rate=44100, wav_buffer=1024, channels=1): #[flag_marker:audio_output]
        ''' class for playing sounds
        '''
        self.parent = parent
        writeFile(self.parent.expmt_log_fp, "%s, Output_AudioData.__init__()\n"%get_time_stamp())
        self.pa = pyaudio.PyAudio()
        self.w_buffer = wav_buffer
        self.channels = channels
        self.sample_width = sample_width
        self.rate = rate
        self.ps_th = [] # play-sound thread
        self.ps_q = [] # play_sound queue
        self.init_sounds()
        
        for i in range(len(output_dev_keywords)): output_dev_keywords[i] = output_dev_keywords[i].lower()
        self.device_index_list, self.device_name_list = self.find_output_device(output_dev_keywords)

        self.streams = []
        self.open_output_streams()
        print('%i streams are open.'%len(self.streams))

    # --------------------------------------------------

    def init_sounds(self): #[flag_marker:audio_output]
        writeFile(self.parent.expmt_log_fp, "%s, Output_AudioData.init_sounds()\n"%get_time_stamp())
        self.wfs = []
        self.sound_lengths = []

    # --------------------------------------------------

    def load_sounds(self, snd_files=[]): #[flag_marker:audio_output]
        writeFile(self.parent.expmt_log_fp, "%s, Output_AudioData.load_sounds()\n"%get_time_stamp())
        if snd_files == []: return
        for snd_file in snd_files:
            self.wfs.append(wave.open(snd_file, 'rb'))
            numFrames = self.wfs[-1].getnframes() # this is accurate whether for stereo or mono
            sRate = float(self.wfs[-1].getframerate())
            self.sound_lengths.append(round(1000*numFrames/sRate)) # length in msecs

    # --------------------------------------------------

    def remove_sounds(self, rem_idx=[]): #[flag_marker:audio_output]
        ''' remove sounds with indices, indicated in rem_idx
        '''
        writeFile(self.parent.expmt_log_fp, "%s, Output_AudioData.remove_sounds()\n"%get_time_stamp())
        if rem_idx == []: return
        for ri in rem_idx:
            self.wfs[ri] = None
            self.sound_lengths[ri] = None
        while None in self.wfs: self.wfs.remove(None)
        while None in self.sound_lengths: self.sound_lengths.remove(None)

    # --------------------------------------------------

    def open_output_streams(self): #[flag_marker:audio_output]
        writeFile(self.parent.expmt_log_fp, "%s, Output_AudioData.open_output_streams()\n"%get_time_stamp())
        for i in range(len(self.device_index_list)):
            try:
                self.streams.append( self.pa.open(format = self.pa.get_format_from_width(self.sample_width),
                                                channels = self.channels,
                                                rate = self.rate,
                                                output_device_index = self.device_index_list[i],
                                                output = True) )
                self.ps_th.append(None)
                self.ps_q.append(queue.Queue())
            except:
                pass

    # --------------------------------------------------

    def close_output_streams(self): #[flag_marker:audio_output]
        writeFile(self.parent.expmt_log_fp, "%s, Output_AudioData.close_output_streams()\n"%get_time_stamp())
        if len(self.streams) > 0:
            for i in range(len(self.streams)):
                self.streams[i].close()
        self.streams = []

    # --------------------------------------------------

    def find_output_device(self, output_dev_keywords): #[flag_marker:audio_output]
        writeFile(self.parent.expmt_log_fp, "%s, Output_AudioData.find_output_device()\n"%get_time_stamp())
        built_in_output_idx = -1
        device_index_list = []       
        device_name_list = []
        for i in range( self.pa.get_device_count() ):     
            devinfo = self.pa.get_device_info_by_index(i) 
            print("Device #%i: %s"%(i, devinfo["name"]))
            for j in range(len(output_dev_keywords)):
                if devinfo["maxOutputChannels"] > 0:
                    print("Found an audio-output: device %d - %s"%(i,devinfo["name"]))
                    device_index_list.insert(0, i)
                    device_name_list.insert(0, devinfo["name"])
                    if output_dev_keywords[j] in devinfo["name"].lower():
                        break # break if found the preferred output device
        if device_index_list == []: print("WARNING:: No audio-output found")
        return device_index_list, device_name_list

    # --------------------------------------------------

    def play_sound_run(self, snd_idx, stream_idx=0): #[flag_marker:audio_output]
        writeFile(self.parent.expmt_log_fp, "%s, Output_AudioData.play_sound_run()\n"%get_time_stamp())
        audio_output_data = self.wfs[snd_idx].readframes(self.w_buffer)
        msg = ''
        while audio_output_data != b'':
            self.streams[stream_idx].write(audio_output_data)
            audio_output_data = self.wfs[snd_idx].readframes(self.w_buffer)
            try: msg = self.ps_q[stream_idx].get(False)
            except queue.Empty: pass
            if msg == 'terminate': break
        self.wfs[snd_idx].rewind()
        self.ps_th[stream_idx] = None

    # --------------------------------------------------

    def play_sound(self, snd_idx=0, stream_idx=0, stop_prev_snd=False): #[flag_marker:audio_output]
        ''' This function works with 'play_sound_run'. Generate a thread and use it for playing a sound once. 'stop_prev_snd = False' indicates that if the requested stream is busy, it ignores the request to play sound.
        '''
        writeFile(self.parent.expmt_log_fp, "%s, Output_AudioData.play_sound()\n"%get_time_stamp())
        if self.ps_th[stream_idx] != None:
            if stop_prev_snd == True:
                self.ps_q[stream_idx].put('terminate', True, None)
                self.ps_th[stream_idx].join()
                self.ps_th[stream_idx] = None
            else:
                return False
        self.ps_th[stream_idx] = Thread(target=self.play_sound_run, args=(snd_idx, stream_idx))
        self.ps_th[stream_idx].start()
        return True

    # --------------------------------------------------

    def stop_all_curr_snds(self, stream_idx=None):
        ''' stop any currently playing sounds
        '''
        writeFile(self.parent.expmt_log_fp, "%s, Output_AudioData.stop_all_curr_snds()\n"%get_time_stamp())
        if stream_idx == None: r = list(range(len(self.streams)))
        else: r = [stream_idx]
        for stream_idx in r:
            th = self.ps_th[stream_idx]
            if th != None and th.isAlive() == True:
                self.ps_q[stream_idx].put('terminate', True, None)
                while th != None and th.isAlive() == True: sleep(0.01)
        
# ===========================================================
#[flag:class-end] !!! DO NOT EDIT THIS LINE !!!

