import threading
import serial
import time
import os.path
import re
import platform
import html

from struct import *
from pymodbus.client.sync import ModbusSerialClient
from pymodbus.exceptions import ModbusException

# separated process for reading serial port and parsing data
class BmsLionModbus:
    
    #init
    def __init__(self, configuration):
        self.config = configuration
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
        if name == "configsave":
            print("Will send following config regs to CPU module:")
            regs = [ int(value[i:i+4],16) for i in range(0, len(value), 4)]
            print(regs)
        
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

    
    # TODO: this function may be deleted probably...
    def send(self, what):
        
        self.clearFileFlag = True
        strtowrite = what+"\n"
        
        cmd = what[1:2]
        data = what[2:]
        
        #we need to send data in packages of max size 64 chars (32bytes)
        #address 2bytes (4chars)
        #command + colon + linefeed (can include \r) 2bytes (4chars)
        #data then max 28bytes (56chars)
        if (cmd == "e"):
            if ((len(data) % 2) != 0):
                self.datalayer.alert = "Data is not divisible by 2"
                return
            #if len(data) > 68:
            #    self.datalayer.settingsOUT = self.datalayer.eepromOUT = "data too long (max 32 bytes)"
            #    return
            if len(data) < 4:
                self.datalayer.alert = "Data is too short (need at least address 16bit)!"
                return
            try:
                test = int(what[2:],16)
            except Exception as e:
                self.datalayer.alert = "Data are not in hex format!"
                return
            
            #we need to split cmd to several chunks because of the usb limit 64 chars... (TODO better settings for m-stack USB?)
            if len(data) > 60:
                address = data[:4]
                rest = data[4:]
                #data length 56 char + 4 char address + 2 char cmd + 1 char \n
                length = 56
                length_bytes = 28
                for idx,chunk in enumerate(rest[0+i:length+i] for i in range(0, len(rest), length)):
                    address_new = "{:0>4x}".format(int(address,16) + length_bytes*idx)
                    strtowrite = ":" + cmd + address_new + chunk + "\n"
                    #tx to cpu module
                    for char in strtowrite:
                        self.connection.write(char.encode())
                        self.connection.flush()
                    time.sleep(0.1)
                return
        
        #tx to cpu module
        for char in strtowrite:
            self.connection.write(char.encode())
            self.connection.flush()

        
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
                        
                    # read config
                    print ("MODBUS connected - will read config")
                    try:
                        rq = self.client.read_holding_registers(4000,32,unit=1)
                        self.datalayer.configRegsParse(rq.registers)
                    except Exception as e:
                        print ("Could not read BMS config! Maybe some other program blocks the connection?")
                        self.connected = 0
                        continue
                    print ("Config successfully loaded!")
                    
                    # must exit "connection trying loop" because when it gets here --> successfully connection made
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
                rq = self.client.read_holding_registers(1000+currentMod*100,30,unit=1)
                #if hasattr(rq, 'registers'):
                self.datalayer.modulesRegsParse(currentMod, rq.registers)
                self.datalayer.receivecounter += 1
                currentMod += 1
                if currentMod == self.datalayer.numModules:
                    currentMod = 0
                    
                # configurable delay
                time.sleep(self.config['sleeptime_comm'])
                self.datalayer.status = "connected: "+self.device
            
            except AttributeError:
                self.datalayer.status = 'Read holding registers exception (attr error): '+self.device
                print(self.datalayer.status)
                
            except ModbusException as e:
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
        for index in range(0,12):
            modulesbits |= regs[index]
            self.numCells += bin(regs[index]).count("1")
        
        offset = 12
        for index in range(0,12):
            self.numTemps += bin(regs[index+offset]).count("1")
        
        # create objects for modules and cells
        self.updateNumModules(bin(modulesbits).count("1"))
    
    # "parse" for cell voltages, temperatures, ...
    #
    def modulesRegsParse (self, currentMod, regs):
        
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
