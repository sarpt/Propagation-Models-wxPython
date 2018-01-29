#rTINFrame
import wx
import os
import mT2pPageFuncs
import mT2pModelfuncs
#import numpy as np
#import pylab as P

from matplotlib.figure import Figure
from wx.lib.masked.numctrl import NumCtrl
from matplotlib.backends.backend_wxagg import \
    FigureCanvasWxAgg, \
    NavigationToolbar2WxAgg

class mT2pPlotFrame(wx.Frame):

    def __init__(self, parent, id, title):
 
        wx.Frame.__init__(self, parent, id, title)
        self.panelmain = wx.Panel(self)

        ### --- PASEK MENU --- ###

        # Stworzenie paska menu
        menuBar = wx.MenuBar()
        
        # Dodanie paska do frame'a
        self.SetMenuBar(menuBar) 

         # Stworzenie menu, jako pojedynczego pionowego elementu
        menu_file= wx.Menu()
        
        m_expt = menu_file.Append(-1, "&Zapisz wykres\tCtrl-Z", "Zapisz wykres do pliku")
        menu_file.AppendSeparator()
        menu_exit = menu_file.Append(wx.ID_EXIT,"Wyjsci&e","Wyjscie z programu")

        # Dodanie menu do paska menu
        menuBar.Append(menu_file,"&Plik") 

        self.Bind(wx.EVT_MENU, self.OnSave, m_expt)
        self.Bind(wx.EVT_MENU, self.OnExit, menu_exit)

        self.dpi = 100
        self.fig = Figure((3.0, 3.0), dpi=self.dpi)
        self.axes = self.fig.add_subplot(111)
        
        self.canvas = FigureCanvasWxAgg(self.panelmain, -1, self.fig)

        self.vbox = wx.BoxSizer(wx.VERTICAL)
        self.vbox.Add(self.canvas, 1, flag=wx.GROW)  
        self.panelmain.SetSizer(self.vbox)
        self.vbox.Fit(self)
        return

    def drawPlot(self,data):
        
        self.fig.canvas.mpl_connect('button_press_event',lambda evt,datapass=data:self.on_click(evt,datapass))

        if data.mode:
            self.axes.set_title('Tlumienie w dziedzine odleglosci dla czestotliwosci '+str(data.freqm)+' Mhz', size=12)
        else:
            self.axes.set_title('Moc sygnalu w dziedzine odleglosci dla czestotliwosci '+str(data.freqm)+' Mhz oraz EIRP='+str(data.power)+' dBm', size=12)

        if data.oneslope_list:
            wyn = self.axes.plot(data.xgen,data.oneslope_list,'b+',linewidth=1,label='One-Slope Model')
        if data.kamerman_list:
            wyn = self.axes.plot(data.xgen,data.kamerman_list,'g-',linewidth=1, label='Kamerman Model')
        if data.lam_list:
            wyn = self.axes.plot(data.xgen,data.lam_list,'k--',linewidth=1,label='Linear Attenuation Model')

        if data.extdata and not data.mode:
            wyn = self.axes.plot(data.xgen,data.extdata,'r',linewidth=1,label='Ray Launching')
            
        self.axes.legend()
        xmin = min(data.xgen)
        xmax = max(data.xgen)
        self.axes.set_xbound(lower=xmin, upper=xmax)
        #ymin = 0
        #ymax = -50
        #self.axes.set_ybound(lower=min(data.oneslope_list), upper=max(data.oneslope_list))

        self.axes.set_xlabel("Odleglosc [m]")
        if data.mode:
            self.axes.set_ylabel("Tlumienie [dB]")
        else:
            self.axes.set_ylabel("Moc sygnalu [dBm]")

        self.canvas.draw()

    def OnExit(self, event):
        self.axes.cla()
        self.fig.clf()
        self.Close(True)

    def OnSave(self, event):
        file_choices = "PNG (*.png)|*.png"
        
        dlg = wx.FileDialog(
            self, 
            message="Zapisz wykres jako...",
            defaultDir=os.getcwd(),
            defaultFile="plot.png",
            wildcard=file_choices,
            style=wx.SAVE)
        
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            self.canvas.print_figure(path, dpi=self.dpi)

    def on_click(self,event,data):
        if event.inaxes is not None:

            foundx = mT2pPageFuncs.takeClosest(data.xgen,event.xdata)
            foundelem = data.xgen.index(foundx)
            
            text = ""
            if data.oneslope_list: text += "One-Slope Model: "+"%.1f"%data.oneslope_list[foundelem]+" dBm\n"
            if data.kamerman_list: text += "Kamerman Model: "+"%.1f"%data.kamerman_list[foundelem]+" dBm\n"
            if data.lam_list: text += "Linear Attenuation Model: "+"%.1f"%data.lam_list[foundelem]+" dBm\n"
            if data.extdata and not data.mode: text += "Ray Launching: "+str(data.extdata[foundelem])+" dBm"
            
            dlg = wx.MessageDialog(self,text,"Wartosci dla odleglosci "+str(foundx)+"m",wx.OK)
            dlg.ShowModal()
            dlg.Destroy()
 
# Create a new frame class, derived from the wxPython Frame.
class mT2pFrame(wx.Frame):

    OnNotification = mT2pPageFuncs.OnNotification
    OnExit = mT2pPageFuncs.OnExit
    labelOnHover = mT2pPageFuncs.labelOnHover
    statusboxOnLeave = mT2pPageFuncs.statusboxOnLeave
    DataClick = mT2pPageFuncs.DataClick
    DataClear = mT2pPageFuncs.DataClear
    modeChange = mT2pPageFuncs.modeChange
    checkboxOneSlope = mT2pPageFuncs.checkboxOneSlope
    checkboxKamerman = mT2pPageFuncs.checkboxKamerman
    checkboxLam = mT2pPageFuncs.checkboxLam
    
    plotdata = mT2pModelfuncs.mT2pPlotData()

    mode = 0

    def __init__(self, parent, id, title):

        # konstruktor klasy bazowej
        wx.Frame.__init__(self, parent, id, title)

        # minimialna wielkosc okna
        #self.SetSizeHints(450,300)

        # Status bar
        self.CreateStatusBar() # A Statusbar in the bottom of the window

### --- PASEK MENU --- ###

        # Stworzenie paska menu
        menuBar = wx.MenuBar()
        
        # Dodanie paska do frame'a
        self.SetMenuBar(menuBar) 

### --- MENU --- ###

        # Stworzenie menu, jako pojedynczego pionowego elementu
        filemenu= wx.Menu()

        # dodanie do menu elementow
        # wx.ID_ABOUT to wx.ID_EXIT standardowe ID od wx widgets ale moga byc jakies inne czy cos...
        menu_about = filemenu.Append(wx.ID_ABOUT, "&Info","Informacje na temat programu")
        filemenu.AppendSeparator()
        menu_exit = filemenu.Append(wx.ID_EXIT,"Wyjsci&e","Wyjscie z programu")

        # Dodanie menu do paska menu
        menuBar.Append(filemenu,"&Plik") 
        

        ### --- EVENT HANDLERY --- ###
        AboutText = "Program stworzony na potrzeby projektu z przedmiotu Media Transmisyjne 2 - Projekt, przez Michala Michalskiego, W-4, TIN"
        self.Bind(wx.EVT_MENU, lambda evt, text=AboutText:self.OnNotification(evt,text), menu_about)
        self.Bind(wx.EVT_MENU, self.OnExit, menu_exit)

        ### --- GLOWNY PANEL --- ###
        panelmain = wx.Panel(self, -1)

            #wybor trybu
        sampleList = ["Moc odebrana","Tlumienie"]
        self.radio_mode = wx.RadioBox(panelmain, -1, "Tryb wyswietlania", wx.DefaultPosition, wx.DefaultSize,sampleList,2, wx.RA_SPECIFY_COLS)
        self.radio_mode.Bind(wx.EVT_RADIOBOX,self.modeChange)
        
            #czestotliwosc
        self.freqctrltext = wx.StaticText(panelmain, -1, "Czestotliwosc [Mhz]: ")
        self.freqctrltext.Bind(wx.EVT_ENTER_WINDOW,lambda evt, text="Wartosc czestotliwosci dla kazdego z badanych modeli w MHz":self.labelOnHover(evt,text))
        self.freqctrltext.Bind(wx.EVT_LEAVE_WINDOW,self.statusboxOnLeave)
        
        self.freqctrlinput = NumCtrl(panelmain, -1)
        self.freqctrlinput.SetParameters(integerWidth=15, fractionWidth=0, allowNegative=False)
        #self.freqctrlinput.Bind(wx.EVT_KEY_UP,self.p3OnChange)
        
            #odleglosc
        self.distctrltext = wx.StaticText(panelmain, -1, "Odleglosc [m]: ")
        self.distctrltext.Bind(wx.EVT_ENTER_WINDOW,lambda evt, text="Granica koncowa dziedziny odleglosci dla badanych modeli":self.labelOnHover(evt,text))
        self.distctrltext.Bind(wx.EVT_LEAVE_WINDOW,self.statusboxOnLeave)
        
        self.distctrlinput = NumCtrl(panelmain, -1)
        self.distctrlinput.SetParameters(integerWidth=15, fractionWidth=0, allowNegative=False)
        
            #step
        self.diststepctrltext = wx.StaticText(panelmain, -1, "Precyzja [m]: ")
        self.diststepctrltext.Bind(wx.EVT_ENTER_WINDOW,lambda evt, text="Roziar kroku pomiedzy mierzonymi wartosciami w metrach":self.labelOnHover(evt,text))
        self.diststepctrltext.Bind(wx.EVT_LEAVE_WINDOW,self.statusboxOnLeave)
        
        self.diststepctrlinput = NumCtrl(panelmain, -1)
        self.diststepctrlinput.SetParameters(integerWidth=15, fractionWidth=2, allowNegative=False)
        
            #moc nadajnika
        self.powctrltext = wx.StaticText(panelmain, -1, "Moc Tx (EIRP) [dBm]: ")
        self.powctrltext.Bind(wx.EVT_ENTER_WINDOW,lambda evt, text="Wyjsciowa moc nadajnika w dBm":self.labelOnHover(evt,text))
        self.powctrltext.Bind(wx.EVT_LEAVE_WINDOW,self.statusboxOnLeave)
        
        self.powctrlinput = NumCtrl(panelmain, -1)
        self.powctrlinput.SetParameters(integerWidth=15, fractionWidth=0, allowNegative=False)
        
            #sizer
        freqsizer = wx.FlexGridSizer(4, 2, 5, 5)
        freqsizer.Add(self.freqctrltext,1,wx.EXPAND)
        freqsizer.Add(self.freqctrlinput,1,wx.EXPAND)
        freqsizer.Add(self.distctrltext,1,wx.EXPAND)
        freqsizer.Add(self.distctrlinput,1,wx.EXPAND)
        freqsizer.Add(self.diststepctrltext,1,wx.EXPAND)
        freqsizer.Add(self.diststepctrlinput,1,wx.EXPAND)
        freqsizer.Add(self.powctrltext,1,wx.EXPAND)
        freqsizer.Add(self.powctrlinput,1,wx.EXPAND)
        
        ### --- INFOBOX #1 --- ###
        ### ONE-SLOPE ###
        infobox_oneslope = wx.StaticBox(panelmain,label="One-Slope Model")

        self.checkbox_oneslope = wx.CheckBox(infobox_oneslope,label="Uwzglednij na wykresie")
        self.checkbox_oneslope.Bind(wx.EVT_CHECKBOX,self.checkboxOneSlope)
        self.checkbox_oneslope.SetValue(True)
        
        self.infobox_oneslope_ntext = wx.StaticText(infobox_oneslope, -1, "Wsploczynnik N: ")
        self.infobox_oneslope_ntext.Bind(wx.EVT_ENTER_WINDOW,lambda evt, text="Skalarna, bezwymiarowa wartosc wspolczynnika N propagacji":self.labelOnHover(evt,text))
        self.infobox_oneslope_ntext.Bind(wx.EVT_LEAVE_WINDOW,self.statusboxOnLeave)
        
        self.infobox_oneslope_ninput = NumCtrl(infobox_oneslope, -1)
        self.infobox_oneslope_ninput.SetParameters(integerWidth=15, fractionWidth=2, allowNegative=False)
        
            #sizer kontrolek
        oneslopesizer = wx.FlexGridSizer(1, 2, 5, 5)
        oneslopesizer.Add(self.infobox_oneslope_ntext,1,wx.EXPAND)
        oneslopesizer.Add(self.infobox_oneslope_ninput,1,wx.EXPAND)
        
            #sizer infoboxa
        oneslopeinfoboxsizer = wx.StaticBoxSizer(infobox_oneslope,wx.VERTICAL)
        oneslopeinfoboxsizer.Add(self.checkbox_oneslope, 0, wx.ALIGN_CENTER)
        oneslopeinfoboxsizer.Add(oneslopesizer, 0, wx.ALIGN_CENTER)
        
        ### --- INFOBOX #2 --- ###
        ### KAMERMAN ###
        infobox_kamerman = wx.StaticBox(panelmain,label="Kamerman Model")

        self.checkbox_kamerman = wx.CheckBox(infobox_kamerman,label="Uwzglednij na wykresie")
        self.checkbox_kamerman.Bind(wx.EVT_CHECKBOX,self.checkboxKamerman)
        self.checkbox_kamerman.SetValue(True)
        
        #self.infobox_kamerman_alfatext = wx.StaticText(infobox_kamerman, -1, "Wsploczynnik alfa: ")
        #self.infobox_kamerman_alfatext.Bind(wx.EVT_ENTER_WINDOW,lambda evt, text="Skalarna, bezwymiarowa wartosc wspolczynnika alfa":self.labelOnHover(evt,text))
        #self.infobox_kamerman_alfatext.Bind(wx.EVT_LEAVE_WINDOW,self.statusboxOnLeave)
        
        #self.infobox_kamerman_alfainput = NumCtrl(infobox_kamerman, -1)
        #self.infobox_kamerman_alfainput.SetParameters(integerWidth=15, fractionWidth=0, allowNegative=False)
        
            #sizer kontrolek
        #kamermansizer = wx.FlexGridSizer(1, 2, 5, 5)
        #kamermansizer.Add(self.infobox_kamerman_alfatext,1,wx.EXPAND)
        #kamermansizer.Add(self.infobox_kamerman_alfainput,1,wx.EXPAND)
        
            #sizer infoboxa
        kamermaninfoboxsizer = wx.StaticBoxSizer(infobox_kamerman,wx.VERTICAL)
        kamermaninfoboxsizer.Add(self.checkbox_kamerman, 0, wx.ALIGN_CENTER)
        #kamermaninfoboxsizer.Add(kamermansizer, 0, wx.ALIGN_CENTER | wx.EXPAND)
        
        ### --- INFOBOX #3 --- ###
        ### LINEAR ATTENTUATION ###
        infobox_lam = wx.StaticBox(panelmain,label="Linear Attenuation Model")

        self.checkbox_lam = wx.CheckBox(infobox_lam,label="Uwzglednij na wykresie")
        self.checkbox_lam.Bind(wx.EVT_CHECKBOX,self.checkboxLam)
        self.checkbox_lam.SetValue(True)
        
        self.infobox_lam_ntext = wx.StaticText(infobox_lam, -1, "Wsploczynnik alfa: ")
        self.infobox_lam_ntext.Bind(wx.EVT_ENTER_WINDOW,lambda evt, text="Skalarna, bezwymiarowa wartosc wspolczynnika alfa":self.labelOnHover(evt,text))
        self.infobox_lam_ntext.Bind(wx.EVT_LEAVE_WINDOW,self.statusboxOnLeave)
        
        self.infobox_lam_ninput = NumCtrl(infobox_lam, -1)
        self.infobox_lam_ninput.SetParameters(integerWidth=15, fractionWidth=2, allowNegative=False)
        
            #sizer kontrolek
        lamsizer = wx.FlexGridSizer(1, 2, 5, 5)
        lamsizer.Add(self.infobox_lam_ntext,1,wx.EXPAND)
        lamsizer.Add(self.infobox_lam_ninput,1,wx.EXPAND)
        
            #sizer infoboxa
        laminfoboxsizer = wx.StaticBoxSizer(infobox_lam, wx.VERTICAL)
        laminfoboxsizer.Add(self.checkbox_lam, 0, wx.ALIGN_CENTER )
        laminfoboxsizer.Add(lamsizer, 0, wx.ALIGN_CENTER)
         
        ### --- INFOBOX #4 --- ###
        ### DANE ZEWNETRZNE ###
        infobox_extdata = wx.StaticBox(panelmain,label="Dane zewnetrzne")

        self.infobox_extdata_filename = wx.StaticText(infobox_extdata, -1, "Wczytany plik: Brak")
        self.infobox_extdata_filename.Bind(wx.EVT_ENTER_WINDOW,lambda evt, text="Nazwa wczytanego pliku z danymi":self.labelOnHover(evt,text))
        self.infobox_extdata_filename.Bind(wx.EVT_LEAVE_WINDOW,self.statusboxOnLeave)
        
        self.databutton = wx.Button(infobox_extdata,wx.ID_OPEN,"Wczytaj zewnetrzne dane")
        self.databutton.Bind(wx.EVT_ENTER_WINDOW,lambda evt, text="Wczytanie danych do porownania na wykresie":self.labelOnHover(evt,text))
        self.databutton.Bind(wx.EVT_LEAVE_WINDOW,self.statusboxOnLeave)
        self.databutton.Bind(wx.EVT_BUTTON,self.DataClick)

        self.clear_databutton = wx.Button(infobox_extdata,wx.ID_OPEN,"Usun zewnetrzne dane")
        self.clear_databutton.Bind(wx.EVT_ENTER_WINDOW,lambda evt, text="Usuwanie zewnetrznych danych z pamieci programu":self.labelOnHover(evt,text))
        self.clear_databutton.Bind(wx.EVT_LEAVE_WINDOW,self.statusboxOnLeave)
        self.clear_databutton.Bind(wx.EVT_BUTTON,self.DataClear)

        extdatasizer = wx.FlexGridSizer(3, 1, 5, 5)
        extdatasizer.Add(self.infobox_extdata_filename,1,wx.EXPAND)
        extdatasizer.Add(self.databutton,1,wx.EXPAND)
        extdatasizer.Add(self.clear_databutton,1,wx.EXPAND)

        extdatainfoboxsizer = wx.StaticBoxSizer(infobox_extdata,wx.VERTICAL)
        extdatainfoboxsizer.Add(extdatasizer, 0, wx.ALIGN_CENTER)
        
        ### --- PRZYCISKI KONCOWE --- ###
        plotbutton = wx.Button(panelmain,wx.ID_OPEN,"Generuj wykresy")
        plotbutton.Bind(wx.EVT_ENTER_WINDOW,lambda evt, text="Generowanie wykresow strat propagacji dla zaznaczonych modeli":self.labelOnHover(evt,text))
        plotbutton.Bind(wx.EVT_LEAVE_WINDOW,self.statusboxOnLeave)
        plotbutton.Bind(wx.EVT_BUTTON,self.showPlot)
        
        ### --- GLOWNE SIZERY I KONIEC KLASY--- ###
        mainsizer = wx.BoxSizer(wx.VERTICAL)
        mainsizer.Add(self.radio_mode,1,wx.ALIGN_CENTER)
        mainsizer.Add(freqsizer,1,wx.ALIGN_CENTER)
        mainsizer.Add(oneslopeinfoboxsizer,1,wx.EXPAND)
        mainsizer.Add(kamermaninfoboxsizer,1,wx.EXPAND)
        mainsizer.Add(laminfoboxsizer,1,wx.EXPAND)
        mainsizer.Add(extdatainfoboxsizer,1,wx.EXPAND)
        mainsizer.Add(plotbutton,1,wx.EXPAND)
        panelmain.SetSizerAndFit(mainsizer)

        self.Fit()
        #self.SetDimensions(50,50,600,250)
        
    def showPlot(self,event):
        #zebranie informacji z kontrolek i przekazanie do struktury
		frequency = self.freqctrlinput.GetValue()
		if frequency == 0:
                    self.OnNotification(0,"Nie podano czestotliwosci!\nProsze podac wartosc czestotliwosci wieksza od 0")
                    return
                    
		distance = self.distctrlinput.GetValue()
		if distance == 0 and not self.plotdata.xgen:
                    self.OnNotification(0,"Odleglosc nie moze byc zerowa w przypadku braku wybranego pliku!\nProsze wybrac plik lub wprowadzic odleglosc wieksza od 0")
                    return
                
		distancestep = self.diststepctrlinput.GetValue()
                if distancestep == 0 and not self.plotdata.xgen:
                    self.OnNotification(0,"Precyzja nie moze byc zerowa w przypadku braku wybranego pliku!\nProsze wybrac plik lub wprowadzic precyzje wieksza od 0")
                    return
		
		power = self.powctrlinput.GetValue()
		
		oneslope_n = self.infobox_oneslope_ninput.GetValue()
		lam_n = self.infobox_lam_ninput.GetValue()
		
        #inicjalizacja list z wartosciami zebranymi z kontorolek
		self.plotdata.dataInit(frequency,distance,distancestep,power,self.mode)
		if self.checkbox_oneslope.GetValue(): self.plotdata.ModelOneSlope(oneslope_n)
		if self.checkbox_kamerman.GetValue(): self.plotdata.ModelKamerman()
		if self.checkbox_lam.GetValue(): self.plotdata.ModelLAM(lam_n)
        
        #tworzenie wykresu
		if self.mode:
                    win_text = "Wykres tlumienia w dziedzinie odleglosci"
                else:
                    win_text = "Wykres poziomu mocy w dziedzinie odleglosci"
                    
		plotframe = mT2pPlotFrame(None, -1, win_text)
		plotframe.Show(True)
		plotframe.drawPlot(self.plotdata)

# Every wxWidgets application must have a class derived from wx.App
class mT2pApp(wx.App):

    # wxWindows calls this method to initialize the application
    def OnInit(self):

        # Create an instance of our customized Frame class
        frame = mT2pFrame(None, -1, "MT2Prop")
        frame.Show(True)

        # Tell wxWindows that this is our main window
        self.SetTopWindow(frame)

        # Return a success flag
        return True
