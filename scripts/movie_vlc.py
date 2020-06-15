#[flag:import-begin] !!! DO NOT EDIT THIS LINE !!!
sys.path.append('scripts/') # due to vlc.py
import vlc # 'vlc.py' file in 'scripts' folder. Python binding for using libvlc API. Refer https://wiki.videolan.org/Python_bindings
# vlc.py version could mismatch with the VLC app you have in your system. In that case, the Python binding file, vlc.py, should be downloaded and replaced.
#[flag:import-end] !!! DO NOT EDIT THIS LINE !!!

# ===========================================================
#[flag:class-begin] !!! DO NOT EDIT THIS LINE !!!

class MovPlayer(wx.Panel): #[flag:movie] #[flag:vlc]
    def __init__(self, parent, panel, pos, size=(-1,-1)): #[flag_marker:movie]
        writeFile(parent.expmt_log_fp, "%s, MovPlayer.__init__()\n"%get_time_stamp())
        self.m_name = "VLC"
        self.parent = parent
        wx.Panel.__init__(self, parent, -1, pos=pos, size=size)
        self.pos = pos
        self.size = size
        self.vlcInst = vlc.Instance()
        self.player = self.vlcInst.media_player_new()
        self.video_len = -1
        ### set the window id where to render VLC's video output
        if sys.platform.startswith('win'): self.player.set_hwnd(self.GetHandle())
        elif sys.platform.startswith('linux'): self.player.set_xwindow(self.GetHandle())
        else: self.player.set_nsobject(self.GetHandle())

    # --------------------------------------------------

    def load(self, filePath): #[flag_marker:movie]
        writeFile(self.parent.expmt_log_fp, "%s, MovPlayer.load()\n"%get_time_stamp())
        self.filePath = filePath
        self.media = self.vlcInst.media_new(unicode(filePath))
        sleep(0.1)
        self.player.set_media(self.media)
        self.play()
        self.loading_start = time()
        self.video_len = 0
        wx.FutureCall(10, self.onLoad)
        return self.video_len

    # --------------------------------------------------

    def onLoad(self): #[flag_marker:movie]
        writeFile(self.parent.expmt_log_fp, "%s, MovPlayer.onLoad()\n"%get_time_stamp())
        self.video_len = self.player.get_length()
        if self.video_len == 0:
            wx.FutureCall(10, self.onLoad)
        else:
            self.player.set_position(0.0)
            elapsed_time = time()-self.loading_start
            log = "%s, Loading time of '%s' : %.3f\n"%(get_time_stamp(), self.filePath, elapsed_time)
            writeFile(self.parent.expmt_log_fp, log)
            if self.size == (-1,-1):
                w = int(self.player.video_get_width())
                h = int(self.player.video_get_height())
            else:
                w = self.size[0]
                h = self.size[1]
            x = self.pos[0] - w/2
            y = self.pos[1] - h/2
            self.SetSize((w,h))
            self.SetPosition(( x, y ))
            #self.parent.onVideoLoaded()

    # --------------------------------------------------

    def play(self): #[flag_marker:movie]
        writeFile(self.parent.expmt_log_fp, "%s, MovPlayer.play()\n"%get_time_stamp())
        if self.player.play() == -1:
            log = "Unable to play, %s"%(self.filePath)
            writeFile(self.parent.expmt_log_fp, log)
            dlg = wx.MessageDialog(self, log, style=wx.OK|wx.ICON_WARNING)
            dlg.ShowModal()
            dlg.Destroy()
        else:
            writeFile(self.parent.expmt_log_fp, 'movie plays')

    # --------------------------------------------------

    def pause(self): #[flag_marker:movie]
        writeFile(self.parent.expmt_log_fp, "%s, MovPlayer.pause()\n"%get_time_stamp())
        if self.player.get_media():
            if self.player.get_time() == -1: self.playMedia()
            else: self.player.pause()

        if self.player.get_media():
            if self.player.get_state() == vlc.State.Paused:
                writeFile(self.parent.expmt_log_fp, 'movie plays')
            elif self.player.get_state() == vlc.State.Playing:
                writeFile(self.parent.expmt_log_fp, 'movie pauses')
            self.player.pause()

    # --------------------------------------------------

    def stop(self): #[flag_marker:movie]
        writeFile(self.parent.expmt_log_fp, "%s, MovPlayer.stop()\n"%get_time_stamp())
        if hasattr(self, 'player') == False: return
        if self.player.get_media():
            self.player.stop()
            writeFile(self.parent.expmt_log_fp, 'movie stops')
        del(self.vlcInst)
        del(self.player)
        self.SetSize((1,1))

# ===========================================================
#[flag:class-end] !!! DO NOT EDIT THIS LINE !!!

