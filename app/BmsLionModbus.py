import threading
import serial
import time
import os.path
import re
import platform
import html
import struct

from struct import *
from pymodbus.client.sync import ModbusSerialClient
from pymodbus.exceptions import ModbusException

# separated process for reading serial port and parsing data
class BmsLionModbus:
    
    #init
    def __init__(self, configuration):
        self.config = configuration
        self.client = 0
        self.busy = 0
        self.device = ''
        self.datalayer = 0
        self.thread = 0
        self.connection = 0
        self.connected = 0
        self.terminate_flag = 0
        self.running_flag = 0
        self.commands = ['v','t','b','c','e','s']
        self.logfile = ''
        self.logfileH = ''
        self.filemode = False
        self.clearFileFlag = False
    
    #join
    def terminate(self):
        self.terminate_flag = 1
        self.thread.join()
    
    #module can receive GET messages
    def http_get(self, key, name, value):
        # we receive only string at the moment and pass it over serial (=value)
        
        # we only get further when key = pass
        if key != "pass":
            return
        
        if (name == "download"):
            return "not implemented yet!"
            # TODO: sd card readout
            # self.datalayer.allfile
        if name == "configload":
            self.readConfig()
            
        if name == "configsave":
            print("Will send following config regs to CPU module:")
            #struct to 16bit register conversion (big endian)
            regs = [ int(value[i:i+4],16) for i in range(0, len(value), 4)]
            #struct to 16bit register conversion (little endian)
            #regs = [ int(value[i:i+2],16)+int(value[i+2:i+4],16)*256 for i in range(0, len(value), 4)]
            print(regs)
            try:
                rq = self.client.write_registers(4000,regs,unit=1)
                print ("Config registers written!")
            except Exception as e:
                print ("Could not write CONFIG registers!")
        
        return ''
        
    def status(self):
        
        return "OK, PEC: "+str(self.datalayer.cpuPEC)+"%"
        
    # menu items offered by module
    # each menu item is connected with a view
    def menu(self):
        return {
        'view_modulesm' :'overview',
        'view_settingsm':'settings',
        }
    
    #items visible on each page  
    def sticky(self):
        return {}
    
    #fork    
    def start(self):
        self.datalayer = Datalayer()
        self.datalayer.sqllog = 0
        
        if 0 == self.running_flag:
            self.thread = threading.Thread(target=self.run)
            self.terminate_flag = 0
            self.thread.start()
            self.datalayer.message = "started new reading process"
        else:
            self.datalayer.message = "one process already running"
        
    def run(self):
        self.running_flag = 1
        currentMod = 0
        
        while not self.terminate_flag:

            if not self.connected:
                for self.device in self.config['ports']:
                    try:
                        self.datalayer.status = 'opening '+self.device
                        self.client = ModbusSerialClient(method = "rtu", port=self.device, baudrate=self.config['modbus_speed'], stopbits=1, bytesize=8, timeout=self.config['modbus_timeout'])
                        time.sleep(0.1)
                        if not self.client.connect():
                            self.connected = 0
                            self.datalayer.status = 'retry in 2s, no connection '+self.device
                            time.sleep(1)
                            continue
                        self.connected = 1
                        self.datalayer.receivecounter = 0
                        self.datalayer.status = 'connected to '+self.device
                    except Exception as e:
                        
                        print(str(e))
                        self.connected = 0
                        time.sleep(1)
                        continue
                        
                    if not self.readConfig():
                        continue
                    
                    # must exit "connection trying loop" because when it gets here --> successfully made connection
                    break
            
            # this is needed when for loop per device finishes
            # we cannot continue without proper connection
            if not self.connected:
                print ("No success with connection. Will test configured devices again...")
                time.sleep(1)
                continue            
            
            # here is the "worker code"    
            error = 0
            try:
                if self.busy:
                    time.sleep(self.config['sleeptime_comm'])
                    continue
                self.busy = 1;
                rq = self.client.read_holding_registers(1000+currentMod*100,30,unit=1)
                #if hasattr(rq, 'registers'):
                self.datalayer.modulesRegsParse(currentMod, rq.registers)
                self.datalayer.receivecounter += 1
                currentMod += 1
                if currentMod == self.datalayer.numModules:
                    currentMod = 0
                    
                self.busy = 0;
                # configurable delay
                time.sleep(self.config['sleeptime_comm'])
                self.datalayer.status = "connected: "+self.device
            
            except AttributeError:
                self.datalayer.status = 'Read holding registers exception (attr error): '+self.device
                print(self.datalayer.status)
                self.busy = 0;
                
            except ModbusException as e:
                self.busy = 0;
                self.datalayer.status = 'Read holding registers exception: '+self.device
                print(self.datalayer.status)
                self.connected = 0
                self.client.close()
                time.sleep(1)
        
        #cleanup only if connection was established...
        if self.connected:
            self.client.close()          
            self.connected = 0
            self.datalayer.message = "closing connection, thread exit"
            self.running_flag = 0
            
    def readConfig(self):
        # read config
        print ("MODBUS connected - will read config 58 regs")
        timeout = 10
        while (self.busy == 1) and (timeout > 0):
            print ("Waiting for connection 100ms")
            timeout -= 1
            time.sleep(0.1)
        
        if timeout == 0:
            print("Timeout - no configuration read")
            return False
            
        try:
            self.busy = 1;
            rq = self.client.read_holding_registers(4000,58,unit=1)
            self.datalayer.configRegsParse(rq.registers)
            self.busy = 0;
        except Exception as e:
            print ("Could not read BMS config! Maybe some other program blocks the connection?")
            self.connected = 0
            self.busy = 0;
            return False
        print ("Config successfully loaded!")
        return True


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
        self.tpcb = [0,0,0]
        self.Cells = [Cell() for x in range(self.MAX_CELLS)]

class Datalayer:
    
    numModules = 0
    numCells = 0
    numTemps = 5
    
    # must calculate cell config, number of modules
    #
    def configRegsParse (self, regs):
        
        print("Config registers hex: ")
        self.eepromOUT = "".join(format(x, '04x') for x in regs)
        print(self.eepromOUT)
        
        #get total count of modules and cells
        modulesbits = 0
        for index in range(0,18):
            modulesbits |= regs[index]
            self.numCells += bin(regs[index]).count("1")
        
        offset = 18
        for index in range(0,12):
            self.numTemps += bin(regs[index+offset]).count("1")
        
        # create objects for modules and cells
        self.updateNumModules(bin(modulesbits).count("1"))
    
    # "parse" for cell voltages, temperatures, ...
    #
    def modulesRegsParse (self, currentMod, regs):
        
        try:
            # voltage
            offset = 0
            for index in range(0,Module.MAX_CELLS):
                self.Modules[currentMod].Cells[index].volt = regs[index]
            
            # temperature
            offset = 12
            for index in range(0,Module.MAX_CELLS):
                self.Modules[currentMod].Cells[index].temp = regs[index+offset]
                
            # balancing
            # TODO fill this data
            
            # pcb temperature
            offset = 27
            self.Modules[currentMod].tpcb[0] = regs[offset]
            self.Modules[currentMod].tpcb[1] = regs[offset+1]
            self.Modules[currentMod].tpcb[2] = regs[offset+2]
        except Exception:
            print("modulesRegsParse - data out of bounds...")

    
    def getConsoleHTML(self):
        text = self.consoleHTML
        self.consoleHTML = ""
        return text
    
    def updateNumModules(self, num):
        self.numModules = num
        self.Modules = [Module() for x in range(self.numModules)]
    
    def __init__(self):
        self.size = 1
        self.sqllog = 0
        self.message = ""
        self.alert = ""
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
        self.cpuAI = [-1,-1,-1,-1,-1,-1]
        self.cpuAIcalc = [-1,-1,-1,-1,-1,-1]
        self.status = 'not connected'
        self.eepromOUT = 'no data received yet'
        self.settingsOUT = 'no data received yet'
        self.linux = platform.platform()
        self.console     = ""
        self.consoleHTML = ""
        self.filelink = ""
        self.allfile = "you need to upload file from CPU module first!"
