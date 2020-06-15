#[flag:import-begin] !!! DO NOT EDIT THIS LINE !!!
import wx.media
#[flag:import-end] !!! DO NOT EDIT THIS LINE !!!

# ===========================================================
#[flag:class-begin] !!! DO NOT EDIT THIS LINE !!!

class MovPlayer(wx.Panel): #[flag:movie] #[flag:wx.media]
    def __init__(self, parent, panel, pos, size=(-1,-1)): #[flag_marker:movie]
        writeFile(parent.expmt_log_fp, "%s, MovPlayer.__init__()\n"%get_time_stamp())
        self.parent = parent
        wx.Panel.__init__(self, parent, -1, pos=pos, size=size)
        self.pos = pos
        self.size = size
        self.video_len = -1

    # --------------------------------------------------
    
    def load(self, file_path, showControls=False): #[flag_marker:movie]
        writeFile(self.parent.expmt_log_fp, "%s, MovPlayer.load_movie()\n"%get_time_stamp())
        try:
            self.player = wx.media.MediaCtrl(self, style=wx.SIMPLE_BORDER,
                                       #szBackend=wx.media.MEDIABACKEND_DIRECTSHOW
                                       #szBackend=wx.media.MEDIABACKEND_QUICKTIME
                                       #szBackend=wx.media.MEDIABACKEND_WMP10
            )
            self.player.Load(file_path)
            self.player.SetInitialSize()
        except NotImplementedError:
            raise
        if self.size == (-1,-1): self.size = self.player.GetBestSize()
        else: self.player.Size = self.size
        x = self.pos[0] - self.size[0]/2
        y = self.pos[1] - self.size[1]/2
        self.SetPosition((x,y))
        self.SetSize(self.size)
        if showControls: self.player.ShowPlayerControls(flags = wx.media.MEDIACTRLPLAYERCONTROLS_STEP)
        self.video_len = self.player.Length()
        return self.video_len

    # --------------------------------------------------

    def play(self): #[flag_marker:movie]
        writeFile(self.parent.expmt_log_fp, "%s, MovPlayer.play()\n"%get_time_stamp())
        self.player.SetInitialSize()
        self.player.Play()

    # --------------------------------------------------
    
    def stop(self): #[flag_marker:movie]
        writeFile(self.parent.expmt_log_fp, "%s, MovPlayer.stop()\n"%get_time_stamp())
        try:
            self.player.Stop()
            self.player.Destroy()
            self.SetSize((1,1))
        except: pass

# ===========================================================
#[flag:class-end] !!! DO NOT EDIT THIS LINE !!!


    

