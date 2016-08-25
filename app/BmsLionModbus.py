import threading
import serial
import time
import os.path
import re
import platform
import html
import struct
import glob
import sys
#from subprocess import Popen
import subprocess
import csv

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
        self.attrErrCnt = 0
        
           
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
            
        if (name == "configsave"):
            print("Will send following config regs to CPU module:")
            #struct to 16bit register conversion (big endian)
            regs = [ int(value[i:i+4],16) for i in range(0, 200, 4)]
            regs1 = [ int(value[i:i+4],16) for i in range(200, 400, 4)]
            regs2 = [ int(value[i:i+4],16) for i in range(400, 680, 4)]
           # struct to 16bit register conversion (little endian)
           # regs = [ int(value[i:i+2],16)+int(value[i+2:i+4],16)*256 for i in range(0, len(value), 4)]
           # print("Config registers 1/2 "+str(regs)+" length: "+str(len(regs)))
           # print("Config registers 2/2 "+str(regs2)+" length: "+str(len(regs2)))
            numb = 0
           
            for i in range(0,50,1) :
                if (str(regs[i])!= str(globvar[i])):
                    print("Config register "+ str(4000+i) +" changed to "+ str(regs[i]))
                    numb+=1
            if (numb == 0):
                print("Config registers 1/3 were not changed")
                numb=0
                
            for i in range(0,50,1) :
                if (str(regs1[i])!= str(globvar[50+i])):
                    print("Config register "+ str(4050+i) +" changed to "+ str(regs1[i]))
                    numb+=1
            if (numb == 0):
                print("Config registers 2/3 were not changed")
                numb=0   
            for i in range(0,70,1) :
               if (str(regs2[i])!= str(globvar[100+i])):
                    print("Config register "+ str(4100+i) +" changed to "+ str(regs2[i]))
                    numb+=1
                   
            if (numb == 0):
               print("Config registers 3/3 were not changed")
                           
            try:
                    while self.busy > 0:
                        time.sleep(self.config['sleeptime_comm'])
                        print ("Waiting for write to config register......")
                        continue
                    self.busy = 1;
                    time.sleep(1)
                    stop = 1
                    rq = self.client.write_registers(4000,regs,unit=1)
                    print ("OK config registers written (1/3)!")
                    time.sleep(1)
                    
                    stop = 2
                    time.sleep(1)
                    rq = self.client.write_registers(4050,regs1,unit=1)
                    print ("OK config registers written (2/3)!")
                    time.sleep(1)
                    
                    stop = 3
                    time.sleep(1)
                    rq = self.client.write_registers(4100,regs2,unit=1)
                    print ("OK config registers written (3/3)!")
                    time.sleep(1)
                    self.busy = 0
                    
            except Exception as e:
                print ("ERROR writing config registers when writing "+str(stop)+". part.\nException: "+str(e))
        if (name == "ReconnectPort"):
            value = value.replace("_","/")
            self.datalayer.selectedserialport=value
            print(value)
            if (self.connected==1):
                #print("New Connection needed. Closing and reopening")
                #self.datalayer.selectedserialport=int(data[0])
                print(self.datalayer.selectedserialport)
                self.client.close()
                self.connected=0
                self.datalayer.message = "New Connection needed. Closing and reopening"
		
        if (name == 'AutoPortDetectionChanged'):
            print(value)
            if value == 'false':
                print("Shut down automatic port detection")
                self.datalayer.automaticportdetection=0
            if value == 'true':
                print("Start automatic port detection")
                self.datalayer.automaticportdetection=1

        return ''
        
    def status(self):
        
        return "OK, PEC: "+str(self.datalayer.cpuPEC)+"%"
        
    # menu items offered by module
    # each menu item is connected with a view
    def menu(self):
		
        #cmdline="app/CAN_CmdLineTool.py 2 configfile.txt"
        #cmdline="os.getcwd()"
        #os.chdir("app")
        #print(os.getcwd())
        #p = subprocess.Popen([sys.executable, "CAN_CmdLineTool.py", "2", "configfile.txt"],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NEW_CONSOLE)
        #p = subprocess.Popen("print('hallo')",stdout=subprocess.PIPE,stderr=subprocess.STDOUT, shell=True)
        #out = p.communicate()[0]
        #os.chdir("..")
        #print(out)
        return {
			'view_modulesm' :'Overview',
			'view_settingsm':'Settings',			
			}
    
    #items visible on each page  
    def sticky(self):
        return {}
    
    #fork    
    def start(self):
        
        self.datalayer = Datalayer()
        self.ResetModuleData()
        self.datalayer.updateNumModules(1) #to have at least one module so template will not throw exception...
        self.datalayer.sqllog = 0
        
        if 0 == self.running_flag:
            self.thread = threading.Thread(target=self.run)
            self.terminate_flag = 0
            self.thread.start()
            self.datalayer.message = "started new reading process"
        else:
            self.datalayer.message = "one process already running"
    
    def scan_serial_ports(self):
        #print(platform.system())
        if (platform.system()=="Windows"):
            ports = ['COM%s' % (i + 1) for i in range(256)]
        elif platform.system()=="Linux" or platform.system=="Cygwin":
        # this excludes your current terminal "/dev/tty"
            ports = glob.glob('/dev/tty[A-Za-z]*')
        elif platform.system()=="Darwin":
            ports = glob.glob('/dev/tty.*')
        else:
            raise EnvironmentError('Unsupported platform')

        result = []
        if (self.connected or self.datalayer.connectedport!="") and (platform.system()=="Windows"):
            result.append(self.datalayer.connectedport)
            #print("Connected port"+self.datalayer.connectedport)
        for port in ports:
            try:
                s = serial.Serial(port)
                s.close()
                result.append(port)
            except (OSError, serial.SerialException):
                pass
        #print(result)
        return result

    def get_current_serial_Port(self):
        selectedportexists=0
        for port in self.datalayer.serialportlist:
            if port == self.datalayer.selectedserialport:
                selectedportexists=1
        
        if selectedportexists and self.datalayer.selectedserialport !="":
            for port in self.datalayer.serialportlist:
                if port == self.datalayer.selectedserialport:
                    return port
        else:
            self.datalayer.selectedserialport = self.datalayer.serialportlist[0]
            return self.datalayer.serialportlist[0]

    def run(self):
        self.running_flag = 1
        currentMod = 0
        
        self.logfilename = time.strftime("app/__pycache__/lion_%Y-%m-%d_%H-%M-%S", time.gmtime())
        
        while not self.terminate_flag:
		
            self.datalayer.serialportlist = []
            self.datalayer.serialportlist=self.scan_serial_ports()
            if not self.connected:
                self.ResetModuleData()
                try:                   
                   tmpPortList = []
                   if self.datalayer.automaticportdetection==1:
                      tmpPortList = self.datalayer.serialportlist
                   else: 
                      tmpPortList.append(self.get_current_serial_Port())						   
                   print("Current selected port: ")
                   print(tmpPortList)
                except IndexError:
                   print("Tried new connection. Available ports:") 
                   print(self.datalayer.serialportlist)
                   #print("Current index: " + str(self.datalayer.selectedserialport))
                   self.datalayer.status = "retry in 1s, waiting for serial port update"

                for self.device in tmpPortList:
                    try:
                        self.datalayer.status = 'opening '+self.device
                        self.datalayer.connectedport = self.device
                        if self.datalayer.automaticportdetection==1:
                            self.datalayer.selectedserialport = self.device
                        #print('opening '+self.device)
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
            if self.connected:
                error = 0
                try:
                    if self.busy > 0:
                        time.sleep(self.config['sleeptime_comm'])
                        continue
                    self.busy = 2;
                    
                    #if (int(self.datalayer.cpuPECpercent/100) !=100):
                    while (currentMod < self.datalayer.numModules):
                        regNum = 1000+currentMod*100
                        rq = self.client.read_holding_registers(regNum,42,unit=1)
                        self.datalayer.modulesRegsParse(currentMod, rq.registers)
                        self.datalayer.receivecounter += 1
                        currentMod += 1
                    #print ("read: "+str(currentMod)+" register: "+str(regNum)+" self.datalayer.numModules:"+str(self.datalayer.numModules))
                    
                    if currentMod == self.datalayer.numModules:
                        rq = self.client.read_holding_registers(3000,40,unit=1)
                        self.datalayer.cpudateRegsParse(1,rq.registers)
                        rq = self.client.read_holding_registers(3040,40,unit=1)
                        self.datalayer.cpudateRegsParse(2,rq.registers)
                        currentMod = 0

#                        with open(self.logfilename+"_volt", 'a', newline='') as fp:
#                            row = ""
#                            for mod in range (0,len(self.datalayer.Modules)):
#                                for cell in range (0,len(self.datalayer.Modules[mod].Cells)):
#                                   row = row + str(self.datalayer.Modules[mod].Cells[cell].volt)+","
#                            fp.write(row+"\n")
                            
#                        with open(self.logfilename+"_temp", 'a', newline='') as fp:
#                            row = str(self.datalayer.cpuPEC)+","+str(self.datalayer.stacksoc)+","
#                           for mod in range (0,len(self.datalayer.Modules)):
#                                for cell in range (0,len(self.datalayer.Modules[mod].Cells)):
#                                    row = row + str((self.datalayer.Modules[mod].Cells[cell].temp-27315)/100)+","
#                            fp.write(row+"\n")
                            
                    
                    if (int(self.datalayer.cpuPECpercent/100)) == 100:
                        self.ResetModuleData()
                    self.datalayer.status = "connected: "+self.device
                    self.attrErrCnt = 0
            
                except AttributeError:
                    self.ResetModuleData()
                    self.datalayer.status = 'Read holding registers exception (probably CRC error): '+self.device
                    if self.attrErrCnt == 10:
                        self.connected = 0
                    self.attrErrCnt += 1
                    print(self.datalayer.status)
                
                except ModbusException as e:
                    self.ResetModuleData()
                    self.datalayer.status = 'Read holding registers exception: '+self.device
                    print("ModbusException: "+self.datalayer.status)
                    self.connected = 0
                    self.client.close()
                    time.sleep(1)
                except Exception as e:
                    print("Other exception:")
                    print(str(e))
                    self.connected = 0
                    self.client.close()
                    time.sleep(1)
                finally:
                    self.busy = 0
                    
                # configurable delay
                time.sleep(self.config['sleeptime_comm'])
        
        #cleanup only if connection was established...
        if self.connected:
            self.client.close()          
            self.connected = 0
            self.datalayer.message = "closing connection, thread exit"
            self.running_flag = 0

    def ResetModuleData(self):
        #print(int(self.datalayer.cpuPECpercent/100))
        if (self.connected):
            for indexmod in range (0,len(self.datalayer.Modules)):
                for indexcell in range (0,len(self.datalayer.Modules[indexmod].Cells)):
                    self.datalayer.Modules[indexmod].Cells[indexcell].volt = 0
                    self.datalayer.Modules[indexmod].Cells[indexcell].temp = -273.15
                    self.datalayer.Modules[indexmod].Cells[indexcell].bal = 0
                    self.datalayer.Modules[indexmod].Cells[indexcell].OW = 0
                

            
    def readConfig(self):
        # read config
        print ("MODBUS connected - I will read config registers")
        print ("creating log file")
        
        timeout = 10
        while (self.busy > 0) and (timeout > 0):
            print ("Waiting for connection 100ms")
            timeout -= 1
            time.sleep(0.1)
        
        if timeout == 0:
            print("Timeout - no configuration read")
            return False
            
        try:
            global globvar
            self.busy = 1;
            print("Try to read modbus config (1/3)")  		
            rq = self.client.read_holding_registers(4000,50,unit=1)
            #print(rq.registers)
            #time.sleep(1)
            print("Try to read modbus config (2/3)")
            rq1 = self.client.read_holding_registers(4050,50,unit=1)
            print("Try to read modbus config (3/3)")
            rq2 = self.client.read_holding_registers(4100,70,unit=1)
            #print(rq2.registers)
            all_regs = rq.registers + rq1.registers + rq2.registers
            globvar=all_regs
            print ("Total registers read: "+str(len(all_regs)))
            self.datalayer.configRegsParse(all_regs)	
        except Exception as e:
            print ("Could not read BMS config! Maybe some other program blocks the connection?\nException: "+str(e))
            self.connected = 0
            return False
        finally:
            self.busy = 0
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
        self.OW = 0

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
    numTemps = 0

    # must calculate cell config, number of modules
    #
    def configRegsParse (self, regs):
        
        print("Config registers hex: ")
        self.eepromOUT = "".join(format(x, '04x') for x in regs)
        print(self.eepromOUT)
        
        self.numCells = 0
        self.numTemps = 0
        
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
    
    def cpudateRegsParse (self, step, regs):
        
        if step == 1:
        #CPU Register 1-40
            self.stack_warningmask = regs[0]
            self.stack_errormask = regs[1]
            self.cpuerror = regs[2]
            self.cpuPEC = regs[3]
            self.cpuPECpercent = regs[4]
            #print(str(regs[8]))
            # print(str(regs[9]))
            #            print(str(regs[15]))
            self.stackI = regs[8]/10000
            self.stackvolt = regs[10]
            self.stacksoc = regs[13]/100
        elif step == 2:
        #CPU Register 40-80            
            offset = 22
            index = 0
            for index in range(0,6):
                self.cpuAI[index] = regs[offset + index]
            offset = 28
            for index in range(0,6):
                self.cpuAIcalc[index] = regs[offset + index]
                #self.cpuAIcalc[index] = index
                
        
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
            offset = 26
            for index in range(0,Module.MAX_CELLS):
                byte = regs[offset];
                bit = (byte >> index ) & 1
                if (bit == 1):
                    self.Modules[currentMod].Cells[index].bal = 1
                else:
                    self.Modules[currentMod].Cells[index].bal = 0
            
            # pcb temperature
            offset = 27
            self.Modules[currentMod].tpcb[0] = regs[offset]
            self.Modules[currentMod].tpcb[1] = regs[offset+1]
            self.Modules[currentMod].tpcb[2] = regs[offset+2]
            
            #Open wire check
            offset = 39
            for index in range(0,Module.MAX_CELLS):
                byte = regs[offset];
                bit = (byte>> index) & 1
                if (bit == 1):
                    self.Modules[currentMod].Cells[index].OW = 1
                else:
                    self.Modules[currentMod].Cells[index].OW = 0
                
        except Exception:
            print("modulesRegsParse - data out of bounds...")

    
    def getConsoleHTML(self):
        text = self.consoleHTML
        self.consoleHTML = ""
        return text
    
    def updateNumModules(self, num):
        self.numModules = num
        self.size = num
        self.Modules = [Module() for x in range(self.numModules)]
    
    def __init__(self):
        self.size = 0
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
        self.cpuPECpercent = 0.0
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
        self.serialportlist = []
        self.selectedserialport = ""
        self.connectedport=""
        self.automaticportdetection = 1
        self.stack_errormask = 0
        self.stack_warningmask = 0
        self.cpuerror = 0
