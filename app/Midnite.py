import time
import threading
from time import gmtime, strftime
from app.webguilibs import webguilibs
from pymodbus.client.sync import ModbusTcpClient

# each module must contain datalayer class which is then passed to views
class Midnite_Datalayer:
    
    def __init__(self):
        self.power = 0
        self.lastupdate = 0
        self.ibatlimNew = 88
        self.ibatlim = 88
        

class Midnite:
    
    
    def __init__(self, configuration):
        self.config = configuration
        self.terminate_flag = 0
        self.running_flag = 0
        self.datalayer = Midnite_Datalayer()
        
    
    def terminate(self):
        self.terminate_flag = 1
        self.thread.join()

    # status for some overview page...
    def status(self):
        return "OK, 3.65V, <20A"
        
    # menu items offered by module
    def menu(self):
        return {
        'view_midnite': self.config['name'],
        }
  
    def start(self):
        
        if 0 == self.running_flag:
            self.thread = threading.Thread(target=self.run)
            self.terminate_flag = 0
            self.thread.start()
    
    def status(self):
        
        return "Last seen :"+self.lastdata
        
    def run(self):
        self.setCurrentRetries = 3
        self.running_flag = 1
        while not self.terminate_flag:
            try:
                
                client = ModbusTcpClient(self.config['address'],port=502)
                client.connect()
                
                if (self.datalayer.ibatlimNew != self.datalayer.ibatlim) and self.setCurrentRetries > 0:
                    print("new current limit: "+str(self.datalayer.ibatlimNew)+" A, writing: "+str(self.datalayer.ibatlimNew*10))
                    self.setCurrentRetries -= 1
                    # unlock first
                    # client.write_registers(20492, [65535,17399])
                    # client.write_registers(28673, [0,17399])
                    # write value
                    
                    rq = client.write_register(4147, self.datalayer.ibatlimNew*10)
                    time.sleep(1)
                
                base = 4114
                rq = client.read_holding_registers(base,40)

                self.datalayer.vbat = rq.registers[0]/10
                self.datalayer.vpv = rq.registers[1]/10
                self.datalayer.voc  = rq.registers[7]/10

                self.datalayer.ibat = rq.registers[2]/10
                self.datalayer.ipv  = rq.registers[6]/10

                self.datalayer.power = rq.registers[4]
                self.datalayer.kwh = rq.registers[3]/10
                self.datalayer.amph = rq.registers[10]
                
                self.datalayer.lifekwh = (rq.registers[11] + (rq.registers[12] << 16))/10
                
                self.datalayer.tfet = rq.registers[18]/10
                self.datalayer.tpcb = rq.registers[19]/10
                
                self.datalayer.ibatlim = rq.registers[4148-base-1]/10

                client.close()
                self.datalayer.lastupdate = int(time.time())
                
            except Exception as e:
                print ("error reading Midnite MODBUS data: "+str(self.config['address']))
                print (str(e))
            finally:
                client.close()
            
            time.sleep(5)

    # module can receive GET messages by clients
    # @main.route('/<module>/<key>/<name>/<value>')
    def http_get(self, key, name, value):
        if name == "ibatlim":
            try:
                self.datalayer.ibatlimNew = int(float(value))
                self.setCurrentRetries = 3
            except ValueError:
                print("value error - get param midnite")
            
