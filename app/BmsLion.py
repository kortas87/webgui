import threading
import serial
import time
import os.path
import re
import platform
import html

# separated process for reading serial port and parsing data
class BmsLion:
    
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
    
    def http_get(self, key, name, value):
        #module can receive GET messages
        return
        
    #menu items offered by module
    def menu(self):
        return {'overview':'modules', 'gauges': 'gauge', 'status':'status', 'settings':'settings'}
    
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
        
        print ("BmsLion module started")
    
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
        while not self.terminate_flag:

            if not self.connected:
                for self.dev in self.devices:
                    try:
                        if os.path.isfile(self.dev):
                            self.connected = 1
                            self.connection = open(self.dev)
                            self.datalayer.status = 'connected to file '+self.dev
                            self.filemode = True
                            break
                        self.datalayer.status = 'opening '+self.dev
                        self.connection = serial.Serial(port=self.dev, baudrate=115200, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE,timeout=10,xonxoff=False, rtscts=False, dsrdtr=False)
                        self.connected = 1
                        #print(self.connection.getSettingsDict())
                        self.datalayer.receivecounter = 0
                        self.datalayer.status = 'connected to '+self.dev
                        self.send(":l5")
                        time.sleep(0.3)
                        self.send(":l5")
                        #debug write files
                        self.logfile = open('dataout.txt', 'w')
                        #self.logfileH = open('dataout.bin', 'bw')
                        #time.sleep (1)
                        break
                    except serial.SerialException as e:
                        self.datalayer.status = 'retry in 1s, no connection '+self.dev
                        self.connected = 0
                        time.sleep(0.5)
            if not self.connected:
                time.sleep(0.5)
                continue
                
            try:
                line = self.connection.readline()
                
                if self.filemode:
                    time.sleep(0.1)
                    #line += "\n"
                else:
                    line = line.decode('ascii')
                    
                #line = received.decode('ascii')
                    
                
                #debug
                self.logfile.write(line)
                #self.logfileH.write(received)
                self.logfile.flush()
                #self.logfileH.flush()
                
                self.datalayer.receivecounter += 1
                self.parse(line)
                
            except Exception as e:
                self.datalayer.status = 'I/O problem (readline) '+self.dev
                #debug
                self.logfile.close()
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
        
    # parses 
    # input: text line
    # output: datalayer
    def parse(self, line):
        
        #temp
        #LionMail.schedule()
    
        if len(line)>0:
            if 'E' == line[:1]:
                self.datalayer.message = 'error: PEC...'
                return
            
            line = line.strip('\r\n')
            cmd = line[0]
            line = line[1:]
        else:
            #self.datalayer.message = 'zero length data received'
            return
            
        # info output
        if cmd == '>':
          self.datalayer.consoleHTML += cmd + html.escape(line) +'<br />' 
        
        # receiving file
        if cmd == '@':
          if self.clearFileFlag:
              self.datalayer.allfile = ""
              self.clearFileFlag = False
              
          self.datalayer.allfile += line+"\n"
          # debug:
          #self.datalayer.consoleHTML += cmd + html.escape(line) +'<br />' 
        
        
        #check if correct cmd received
        elif any(cmd == s for s in self.commands):
            
            #module    
            if len(line)>0:
                try:
                    mod = int(line[0], 16)
                    line = line[1:]
                    #if mod >= self.datalayer.MAX_MODULES:
                    #    print("Configured less modules than received!!")
                except Exception as e:
                    self.datalayer.message = 'cound not convert line '+ str(line).replace('\n',' ')+', '+str(e).replace('\n',' ')
                    return
            else:
                self.datalayer.message = 'wrong data received.'
                return
            
            #data
            if not len(line)>0:        
                self.datalayer.message = 'wrong data received.'
                return
                
            #eeprom
            if cmd == 'e':
                #bits 0-25
                if mod == 0:
                    self.datalayer.eepromOUT = str(line)
                    print('EEPROM:'+line)
                #bit 25-50
                #if mod == 1:
                #   self.datalayer.eepromOUT += str(line)
                #    print('EEPROM(2/3)'+line)
                    
                #write mode output
                if mod == 9:
                    self.datalayer.eepromOUT = str(line)
                    print('EEPROM'+line)
            
            #divide received string by n = 4
            n = 4
            val_length = len(line)
            values = [line[i:i+n] for i in range(0, len(line), n)]
            
            for index, value in enumerate(values):
                try:
                    #voltage
                    if cmd == 'v':
                        if (mod + 1) > self.datalayer.size:
                            self.datalayer.size = mod + 1
                        #if we have not received full line then do not convert values
                        #check at least divisibility
                        if val_length % 2 == 0:
                            self.datalayer.Modules[mod].Cells[index].volt = int(value, 16)
                        else:
                            print ("wrong data length"+val_length)
                    #temperature
                    elif cmd == 't':
                        #if we have not received full line then do not convert values
                        #check at least divisibility
                        if val_length % 2 == 0:
                            self.datalayer.Modules[mod].Cells[index].temp = int(value, 16)
                        else:
                            print ("wrong data length")
                    #cpu module information
                    elif cmd == 'c':
                        if index == 0:
                            self.datalayer.cputemp = int(value, 16)
                        if index == 1:
                            self.datalayer.cpuVsupply = int(value, 16)
                        if index == 2:
                            self.datalayer.cpuV33 = int(value, 16)
                        if index == 3:
                            self.datalayer.cpuPEC = int(value, 16)
                        if index == 4:
                            self.datalayer.cputimeA = value
                        if index == 5:
                            self.datalayer.cputime = int(self.datalayer.cputimeA+value,16)
                        if index == 6:
                            self.datalayer.eepromNewest = value
                        if index == 7:
                            self.datalayer.cpuPECpercent = int(value, 16) 
                        if index == 8:
                            self.datalayer.cpuAI[0] = int(value, 16)
                        if index == 9:
                            self.datalayer.cpuAI[1] = int(value, 16)
                        if index == 10:
                            self.datalayer.cpuAI[2] = int(value, 16)
                        if index == 11:
                            self.datalayer.cpuAI[3] = int(value, 16)
                        if index == 12:
                            self.datalayer.cpuAI[5] = int(value, 16)
                    #stack information
                    elif cmd == 's':
                        if index == 0:
                            self.datalayer.stackmaxtemp = int(value, 16)
                        if index == 1:
                            self.datalayer.stackmintemp = int(value, 16)
                        if index == 2:
                            self.datalayer.stackvolt = int(value, 16)
                        if index == 3:
                            self.datalayer.stackmincell = int(value, 16)
                        if index == 4:
                            self.datalayer.stackmaxcell = int(value, 16)
                        if index == 5:
                            self.datalayer.stacksoc = int(value, 16)
                        if index == 6:
                            self.datalayer.stackIA = value
                        if index == 7:
                            self.datalayer.stackI = int(self.datalayer.stackIA+value,16)
                            if self.datalayer.stackI > 0x7FFFFFFF:
                                self.datalayer.stackI -= 0x100000000
                            self.datalayer.stackpower = self.datalayer.stackvolt/100 * self.datalayer.stackI/10000
                        if index == 8:
                            self.datalayer.cpuAIcalc[0] = int(value, 16)
                        if index == 9:
                            self.datalayer.cpuAIcalc[1] = int(value, 16)
                        if index == 10:
                            self.datalayer.cpuAIcalc[2] = int(value, 16)
                        if index == 11:
                            self.datalayer.cpuAIcalc[3] = int(value, 16)
                        if index == 12:
                            self.datalayer.cpuAIcalc[5] = int(value, 16)

                    elif cmd == 'b':
                        #decode balancing bits
                        if index == 0:
                            for i in range(12):
                              self.datalayer.Modules[mod].Cells[i].bal = (int(value, 16) >> i) & 1;
                        #reference voltage
                        elif index == 1:
                            self.datalayer.Modules[mod].vref = int(value, 16);
                        #V module2 by mux
                        elif index == 2:
                            self.datalayer.Modules[mod].vmod2 = int(value, 16);
                        #T pcb
                        elif index == 3:
                            self.datalayer.Modules[mod].tpcb = int(value, 16);
                                        
                except Exception as e:
                    self.datalayer.message = 'Could not convert hex to int '+ str(value).replace('\n',' ')+', '+str(e).replace('\n',' ')
                    #print(self.datalayer.message)
                    print ('line: '+line);
                    print ('exception '+str(e)+'mod:'+str(mod)+' index: '+str(index))
                    return
            
            self.datalayer.message = 'data ok'

        else:
            self.datalayer.message = 'uknown command received' #+line
            #print (self.datalayer.message)
            print (line)
        
        return


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
    
    def getConsoleHTML(self):
        text = self.consoleHTML
        self.consoleHTML = ""
        return text
    
    def __init__(self):
        self.size = 1
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
        self.cpuAI = [-1,-1,-1,-1,-1,-1]
        self.cpuAIcalc = [-1,-1,-1,-1,-1,-1]
        self.status = 'not connected'
        self.eepromOUT = 'no data received yet'
        self.settingsOUT = 'no data received yet'
        self.linux = platform.platform()
        self.console     = ""
        self.consoleHTML = ""
        self.filelink = ""
        self.allfile = ""
