import wx
from bisect import bisect_left

def takeClosest(myList, myNumber):
    """
    Assumes myList is sorted. Returns closest value to myNumber.

    If two numbers are equally close, return the smallest number.
    """
    pos = bisect_left(myList, myNumber)
    if pos == 0:
        return myList[0]
    if pos == len(myList):
        return myList[-1]
    before = myList[pos - 1]
    after = myList[pos]
    if after - myNumber < myNumber - before:
       return after
    else:
       return before

def isfloat(text):
    try:
        inNumberfloat = float(text)
        return True
    except ValueError:
        pass
    return False
    
def OnNotification(self, event, text):
    dlg = wx.MessageDialog(self,text,"Informacja od programu",wx.OK)
    dlg.ShowModal()
    dlg.Destroy()
        
def OnExit(self, event):
    self.Close(True)

def labelOnHover(self,event,text):
    self.SetStatusText(text)

def DataClick(self,event):
    openFileDialog = wx.FileDialog(self, "Otworz plik z pomiarami", "", "",
                                       "TXT files (*.txt)|*.txt", wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
    if openFileDialog.ShowModal() == wx.ID_CANCEL:
        return     # the user changed idea...

    # proceed loading the file chosen by the user
    # this can be done with e.g. wxPython input streams:
    with open(openFileDialog.GetPath(),'r') as input_stream:
        rextdata = input_stream.readlines()
    input_stream.close()
    
    splitextdata = []
    for istr in rextdata:
        istr = istr.replace(',','.')
        splitextdata.append(istr.split('\t'))
     
    diff = float(splitextdata[2][0])-float(splitextdata[1][0])

    del self.plotdata.xgen[:]
    del self.plotdata.extdata[:]
    
    for istr in splitextdata:
        if isfloat(istr[1]):
            if float(istr[0]) >= 1:
                self.plotdata.xgen.append(float(istr[0]))
                self.plotdata.extdata.append(float(istr[1]))
    
    #print self.plotdata.extdata
    self.infobox_extdata_filename.SetLabel("Wczytany plik: %s" % openFileDialog.GetFilename())
    self.distctrlinput.Enable(False)
    self.diststepctrlinput.Enable(False)

def DataClear(self,event):

    del self.plotdata.extdata[:]
    del self.plotdata.xgen[:]
    self.infobox_extdata_filename.SetLabel("Wczytany plik: Brak")
    self.distctrlinput.Enable(True)
    self.diststepctrlinput.Enable(True)
    

def statusboxOnLeave(self, event):
    self.SetStatusText("")

def modeChange(self,event):
    selection = self.radio_mode.GetSelection()
    if selection == 0:
        self.mode = 0
        self.powctrlinput.Enable(True)
        self.databutton.Enable(True)
        self.clear_databutton.Enable(True)
    elif selection == 1:
        self.mode = 1
        self.DataClear(1)
        self.powctrlinput.Enable(False)
        self.databutton.Enable(False)
        self.clear_databutton.Enable(False)
    else:
        self.mode = 0
        self.powctrlinput.Enable(True)
        self.databutton.Enable(True)
        self.clear_databutton.Enable(True)

def checkboxOneSlope(self,event):

    if self.checkbox_oneslope.GetValue():
        self.infobox_oneslope_ninput.Enable()
    else:
        self.infobox_oneslope_ninput.Enable(False)
    return

def checkboxKamerman(self,event):
    return

def checkboxLam(self,event):
    if self.checkbox_lam.GetValue():
        self.infobox_lam_ninput.Enable()
    else:
        self.infobox_lam_ninput.Enable(False)
    return
