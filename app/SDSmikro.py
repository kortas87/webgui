import time
import threading
import xml.etree.ElementTree as ET
from urllib.request import urlopen
from time import gmtime, strftime
from app.webguilibs import webguilibs

# each module must contain datalayer class which is then passed to views
class SDSmikro_Datalayer:
    
    def __init__(self):
        self.p1 = 0
        self.p2 = 0
        self.p3 = 0
        self.p1_raw = 0
        self.p2_raw = 0
        self.p3_raw = 0
        self.p1imp = 0
        self.p1mul = 1
        self.p2imp = 0
        self.p2mul = 1
        self.p3imp = 0
        self.p3mul = 1
        self.lastupdate = 0
        self.uptime = 0
        self.uptime_raw = 0
        self.r1 = 0
        self.r2 = 0
        self.ad1 = 0
        self.ad1_raw = 0
        self.ad2 = 0
        self.ad2_raw = 0
        self.ad3 = 0
        self.ad3_raw = 0
        self.ad4 = 0
        self.ad4_raw = 0
        self.t = {}
        

class SDSmikro:
    
    
    def __init__(self, configuration):
        self.config = configuration
        self.terminate_flag = 0
        self.running_flag = 0
        self.datalayer = SDSmikro_Datalayer()
        
    
    def terminate(self):
        self.terminate_flag = 1
        self.thread.join()

    # status for some overview page...
    def status(self):
        return "OK, 3.65V, <20A"
        
    # menu items offered by module
    # each menu item is connected with a view
    # view_xxx must be unique name between all modules! it is also filename...
    def menu(self):
        return {
        'view_sdsmikro': self.config['name'],
        }
  
    def start(self):
        
        if 0 == self.running_flag:
            self.thread = threading.Thread(target=self.run)
            self.terminate_flag = 0
            self.thread.start()
            self.datalayer.message = "started new reading process"
        else:
            self.datalayer.message = "one process already running"
        
        print ("BmsLion module started")
    
    def status(self):
        
        return "Last seen :"+self.lastdata
        
    def run(self):
        self.running_flag = 1
        while not self.terminate_flag:
            try:
                addr = 'http://'+self.config['address']
                
                # get temps
                lines = urlopen(addr+"/temp.txt", timeout = 5).read().decode("utf-8").split("\n")
                for idx,line in enumerate(lines):
                    self.datalayer.t[idx] = "#"
                    if len(line) > 20:
                        self.datalayer.t[idx] = float(lines[0].split(":")[1].strip()[:-2])
                time.sleep(1)
                
                # get XML
                root = ET.parse(urlopen(addr+"/xml.xml")).getroot()
                self.datalayer.loc = root.find("./sysLoc").text
                self.datalayer.p1_raw = root.find(".//s0_1/act").text
                self.datalayer.p1     = self.datalayer.p1_raw.split()[0]
                self.datalayer.p2_raw = root.find(".//s0_2/act").text
                self.datalayer.p2     = self.datalayer.p2_raw.split()[0]
                self.datalayer.p3_raw = root.find(".//s0_3/act").text
                self.datalayer.p3     = self.datalayer.p3_raw.split()[0]
                self.datalayer.p1imp = int(root.find(".//s0_1/impT0").text)
                self.datalayer.p1mul = int(root.find(".//s0_1/mul").text)
                self.datalayer.p2imp = int(root.find(".//s0_2/impT0").text)
                self.datalayer.p2mul = int(root.find(".//s0_2/mul").text)
                self.datalayer.p3imp = int(root.find(".//s0_3/impT0").text)
                self.datalayer.p3mul = int(root.find(".//s0_3/mul").text)
                self.datalayer.uptime_raw = int(int(root.find(".//snmp/uptime").text)/100)
                self.datalayer.uptime = webguilibs.niceUptime(self.datalayer.uptime_raw)
                self.datalayer.ad1_raw = root.find(".//snmp/ad1_si").text
                self.datalayer.ad1     = float(self.datalayer.ad1_raw.split()[0])
                self.datalayer.ad2_raw = root.find(".//snmp/ad2_si").text
                self.datalayer.ad2     = float(self.datalayer.ad2_raw.split()[0])
                self.datalayer.ad3_raw = root.find(".//snmp/ad3_si").text
                self.datalayer.ad3     = float(self.datalayer.ad3_raw.split()[0])
                self.datalayer.ad4_raw = root.find(".//snmp/ad4_si").text
                self.datalayer.ad4     = float(self.datalayer.ad4_raw.split()[0])
                self.datalayer.r1 = int(root.find(".//snmp/relay_1").text)
                self.datalayer.r2 = int(root.find(".//snmp/relay_2").text)
                self.datalayer.lastupdate = int(time.time())
                
            #xml.etree.ElementTree.ParseError 
            except Exception as e:
                print ("error reading SDS data: "+str(addr))
            
            time.sleep(4)

    # module can receive GET messages by clients
    # @main.route('/<module>/<key>/<name>/<value>')
    def http_get(self, key, name, value):
        
        return ""
