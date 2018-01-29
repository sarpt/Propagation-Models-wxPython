import math

class mT2pPlotData:

    extdata = []
    xgen = []
    oneslope_list = []
    kamerman_list = []
    lam_list = []
    
    def dataInit(self,freq,dist,diststep,power,mode):
        del self.oneslope_list[:]
        del self.kamerman_list[:]
        del self.lam_list[:]
    
        self.freq = freq*1000000 #zamiana z Mhz na Hz
        self.freqm = freq        #w Mhz dla LAM
        self.power = power
        self.l0 = -1*20*math.log10((3*pow(10,8))/(4*3.14159*self.freq))
        self.mode = mode
        
        #generowanie dziedziny odleglosci dla wykresu jesli nie istnieja dane
        if (self.extdata == [] or self.mode):
            del self.xgen[:]
            self.dist = dist
            self.diststep = diststep
            start = 1;
            while start <= self.dist:
                self.xgen.append(start)
                start += self.diststep
            #print self.l0
        
    def ModelOneSlope(self,n):  

        for i in self.xgen:
            result = self.l0+(n*10*(math.log10(i)))

            if self.mode:
                self.oneslope_list.append(result)
            else:
                self.oneslope_list.append(self.power-result)
        return
        
    def ModelKamerman(self):

        for i in self.xgen:
            if i<=8:
                result = self.l0+(20*(math.log10(i)))
            else:
                result = self.l0+(20*(math.log10(8)))+(33*(math.log10(i/8)))

            if self.mode:
                self.kamerman_list.append(result)
            else:
                self.kamerman_list.append(self.power-result)
        return
        
        
    def ModelLAM(self,alfa):

        for i in self.xgen:
            fspl = 20*math.log10(float(i)/1000)+20*math.log10(self.freqm)+32.44
            result = fspl+alfa*i
            
            if self.mode:
                self.lam_list.append(result)
            else:
                self.lam_list.append(self.power-result)
        return
