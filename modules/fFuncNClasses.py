# coding: UTF-8
"""
Frequenty used functions and classes
(for Experimenter_GUI)
"""

import wx
import wx.lib.scrolledpanel as sPanel
from datetime import datetime

# ------------------------------------------------------

def GNU_notice(idx=0):
    '''
      function for printing GNU copyright statements
    '''
    if idx == 0:
        year = datetime.now().year
        print('''
Copyright (c) %i Jinook Oh, W. Tecumseh Fitch.
This program comes with ABSOLUTELY NO WARRANTY; for details run this program with the option `-w'.
This is free software, and you are welcome to redistribute it under certain conditions; run this program with the option `-c' for details.
'''%year)
    elif idx == 1:
        print('''
THERE IS NO WARRANTY FOR THE PROGRAM, TO THE EXTENT PERMITTED BY APPLICABLE LAW. EXCEPT WHEN OTHERWISE STATED IN WRITING THE COPYRIGHT HOLDERS AND/OR OTHER PARTIES PROVIDE THE PROGRAM "AS IS" WITHOUT WARRANTY OF ANY KIND, EITHER EXPRESSED OR IMPLIED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE. THE ENTIRE RISK AS TO THE QUALITY AND PERFORMANCE OF THE PROGRAM IS WITH YOU. SHOULD THE PROGRAM PROVE DEFECTIVE, YOU ASSUME THE COST OF ALL NECESSARY SERVICING, REPAIR OR CORRECTION.
''')
    elif idx == 2:
        print('''
You can redistribute this program and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
''')

# ------------------------------------------------------

def get_time_stamp(flag_ms=False):
    ts = datetime.now()
    ts = ('%.4i_%.2i_%.2i_%.2i_%.2i_%.2i')%(ts.year, ts.month, ts.day, ts.hour, ts.minute, ts.second)
    if flag_ms == True: ts += '_%.6i'%(ts.microsecond)
    return ts

# ------------------------------------------------------

def writeFile(file_path, txt='', mode='a', method=None, np=None, arr=None):
    f = open(file_path, mode)
    if method == None:
        f.write(txt)
    else:
        m = method.split('_')
        if m[0] == 'np': # saving numpy array into a file
            if np == None:
                print('NumPy instance is None.')
            else:
                if m[1] == 'save': # binary '.npy'
                    np.save(f, arr)
                elif m[1] == 'savetxt': # text file. can be gzipped file '.gz'
                    np.savetxt(f, arr)
    f.close()

#------------------------------------------------

def load_img(file_path, size=(-1,-1)):
    tmp_null_log = wx.LogNull() # for not displaying the tif library warning
    img = wx.Image(file_path, wx.BITMAP_TYPE_ANY)
    del tmp_null_log
    if size != (-1,-1) and type(size[0]) == int and type(size[1]) == int: 
        if img.GetSize() != size: img = img.Rescale(size[0], size[1])
    return img

#------------------------------------------------

def set_img_for_btn(imgPath, btn, flag_label=True):
    img = load_img(imgPath)
    bmp = wx.Bitmap(img)
    if flag_label == True: btn.SetBitmapLabel(bmp)
    else: btn.SetBitmap(bmp)

#------------------------------------------------

def convert_idx_to_ordinal(number):
    ''' convert zero-based index number to ordinal number string
    0->1st, 1->2nd, ...
    '''
    if number == 0: return "1st"
    elif number == 1: return "2nd"
    elif number == 2: return "3rd"
    else: return "%ith"%(number+1)

#------------------------------------------------

def show_msg(msg, size=(400,200), title="Message"):
    err_msg = PopupDialog(title=title, inString=msg, size=size)
    err_msg.ShowModal()
    err_msg.Destroy()

#====================================================

class PopupDialog(wx.Dialog):
# Class for showing any message to the participant
    def __init__(self, parent = None, id = -1, title = "Message", inString = "", font = None, pos = None, size = (200, 150), cancel_btn = False, default_ok = False):
        wx.Dialog.__init__(self, parent, id, title)
        self.SetSize(size)
        if pos == None: self.Center()
        else: self.SetPosition(pos)
        self.Center()
        
        self.panel = sPanel.ScrolledPanel(self, -1, pos=(0,0), size=size)
        vbox = wx.BoxSizer(wx.VERTICAL)
        
        sTxt = wx.StaticText(self.panel, -1, label = inString, pos = (20, 20))
        sTxt.SetSize((size[0]-50, size[1]-30))
        if font == None: font = wx.Font(14, wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.FONTWEIGHT_NORMAL, False, "Arial", wx.FONTENCODING_SYSTEM)
        sTxt.SetFont(font)
        sTxt.Wrap(size[0]-60)
        vbox.Add(sTxt, 0, wx.ALIGN_LEFT|wx.ALL, 2)
        vbox.Add((20,20))
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        okButton = wx.Button(self.panel, wx.ID_OK, "OK", size=(100,-1))
        hbox.Add(okButton, 0, wx.ALIGN_RIGHT|wx.ALL, 2)
        if cancel_btn == True:
            cancelButton = wx.Button(self.panel, wx.ID_CANCEL, "Cancel", size=(100,-1))
            hbox.Add(cancelButton, 0, wx.ALIGN_RIGHT|wx.ALL, 2)
        vbox.Add(hbox, 0, wx.ALIGN_RIGHT|wx.ALL, 2)

        self.panel.SetSizer(vbox)
        self.panel.SetupScrolling()

        if cancel_btn == False or default_ok == True:
            self.panel.Bind(wx.EVT_KEY_DOWN, self.onKeyPress)
            okButton.SetDefault()

    #------------------------------------------------

    def onKeyPress(self, event):
        if event.GetKeyCode() == wx.WXK_RETURN: 
            self.EndModal(wx.ID_OK)

#====================================================

if __name__ == '__main__':
    pass
