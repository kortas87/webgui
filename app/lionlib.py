
#linux system info
import platform

class Config:
    
    def __init__(self):
        self.Cells = [0 for x in range(12)]

class Cell:
    
    def __init__(self):
        self.volt = 0
        self.temp = 0
        self.bal = 0

class Module:
    MAX_CELLS = 12
    
    def __init__(self):
        self.vref = 0
        self.vmod1 = 0 #by LTC        
        self.vmod2 = 0 #by mux
        self.tpcb = 0
        self.Cells = [Cell() for x in range(self.MAX_CELLS)]

class Datalayer:
    MAX_MODULES = 16
    
    def __init__(self):
        self.sqllog = 0
        self.message = ""
        self.alert = ""
        self.uptime = 0
        self.Modules = [Module() for x in range(self.MAX_MODULES)]
        self.cputemp = 0
        self.eepromNewest = 0
        self.cputime = 0
        self.message = 0
        self.cpuV33 = 0
        self.cpuVsupply = 0
        self.cpuPEC = 0
        self.cpuPECpercent = 0
        self.receivecounter = 0
        self.stackmaxtemp = 0
        self.stackmintemp = 0
        self.stackmincell = 0
        self.stackmaxcell = 0
        self.stackvolt = 0
        self.stacksoc = 0
        self.stackI = 0
        self.stackpower = 0
        self.cpuAI = [-1,-1,-1,-1]
        self.cpuAIcalc = [-1,-1,-1,-1]
        self.status = 'not connected'
        self.eepromOUT = 'no data received yet'
        self.settingsOUT = 'no data received yet'
        self.linux = platform.platform()
