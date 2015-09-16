import threading
import serial
import time
import os.path
import re
import platform
import html

from struct import *
from pymodbus.client.sync import ModbusSerialClient

# separated process for reading serial port and parsing data
class BmsLionModbus:
    
    #init
    def __init__(self, configuration):
        self.devices = configuration
        self.datalayer = 0
        self.thread = 0
        self.connection = 0
        self.connected = 0
        self.terminate_flag = 0
        self.running_flag = 0
        self.commands = ['v','t','b','c','e','s']
        self.dev = ''
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
        # we do not check secret key
        # we do not care about variable name
        # we receive only string at the moment and pass it over serial (=value)
        
        if (name == "download"):
            return "not implemented yet!"
            #self.datalayer.allfile
        
        self.send(value)
        return ''
        
    def status(self):
        
        return "OK, PEC: "+str(self.datalayer.cpuPEC)+"%"
        
    # menu items offered by module
    # each menu item is connected with a view
    def menu(self):
        return {
        'view_modulesm' :'overview',
        'view_settings':'settings',
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
        
        self.client = ModbusSerialClient(method = "rtu", port="/dev/ttyUSB1", baudrate=9600, stopbits=1, bytesize=8, timeout=0.1)
        self.client.connect()
        print ("MODBUS connected")
        print (self.client)
        rq = self.client.read_holding_registers(1000,5,unit=1)
        print(rq.registers)
        return;
        while not self.terminate_flag:

            if not self.connected:
                for self.dev in self.devices:
                    try:
                        self.datalayer.status = 'opening '+self.dev
                        self.client = ModbusSerialClient(method = "rtu", port=self.dev, baudrate=9600, stopbits=1, bytesize=8, timeout=0.1)
                        #client = ModbusSerialClient(method = "rtu", port="/dev/ttyUSB1", baudrate=9600, stopbits=1, bytesize=8, timeout=0.1)
                        time.sleep(1)
                        self.client.connect()
                        self.connected = 1
                        self.datalayer.receivecounter = 0
                        self.datalayer.status = 'modbus connected to '+self.dev
                    except Exception as e:
                        self.datalayer.status = 'retry in 2s, no connection '+self.dev
                        print(str(e))
                        self.connected = 0
                        time.sleep(2)
                        continue
                        
                    # read config
                    time.sleep(2)
                    print ("MODBUS connected")
                    print (self.client)
                    rq = self.client.read_holding_registers(1000,5,unit=1)
                    print(rq.registers)
                    #self.datalayer.configRegsParse(rq.registers)
                    #try:
                        # read config
                    #    rq = self.client.read_holding_registers(4000,78)
                    #    self.datalayer.configRegsParse(rq.registers)
                    #    break
                    #except Exception as e:
                    #    self.datalayer.status = 'config not loaded '+self.dev
                    #    self.connected = 0
                    #    time.sleep(2)
                        
            if not self.connected:
                time.sleep(1)
                continue
                
            try:
                rq = self.client.read_holding_registers(base,40)
                rq.registers[0]

                
                if self.filemode:
                    time.sleep(0.1)
                    #line += "\n"
                else:
                    line = line.decode('ascii')
                    
                #line = received.decode('ascii')
                    
                
                #debug
                #self.logfile.write(line)
                #self.logfileH.write(received)
                #self.logfile.flush()
                #self.logfileH.flush()
                
                self.datalayer.receivecounter += 1
                self.parse(line)
                
            except Exception as e:
                self.datalayer.status = 'I/O problem (readline) '+self.dev
                #debug
                #self.logfile.close()
                #self.logfileH.close()
                print('I/O problem '+self.dev)
                print(str(e))
                self.connected = 0
                
                self.connection.close()
                
                time.sleep(1)
        
        #cleanup only if connection was established...
        if self.connected:
            self.connection.close()
            #debug
            #self.logfile.close()
            #self.logfileH.close()            
            self.connected = 0
            self.datalayer.message = "reading process terminated"
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
    
    # module registers
    struct1000 = bytes(1600)
    # cpu registers
    struct3000 = bytes(50)
    # config registers
    configRegs = bytes(160)
    
    MAX_MODULES = 0
    
    # must calculate cell config, number of modules
    #
    def configRegsParse (self, regs):
        self.MAX_MODULES = str(regs[0])+":"+str(regs[1])+":"+str(regs[2])+":"+str(regs[3])
        
    
    def getConsoleHTML(self):
        text = self.consoleHTML
        self.consoleHTML = ""
        return text
    
    def __init__(self):
        self.size = 1
        self.sqllog = 0
        self.message = ""
        self.alert = ""
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
