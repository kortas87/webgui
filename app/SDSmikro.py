import time
import threading
import xml.etree.ElementTree as ET
from urllib.request import urlopen
from time import gmtime, strftime

# each module must contain datalayer class which is then passed to views
class SDSmikro_Datalayer:
    
    def __init__(self):
        self.p1 = 0
        self.p2 = 0
        

class SDSmikro:
    
    
    def __init__(self, configuration):
        self.config = configuration
        self.terminate_flag = 0
        self.running_flag = 0
        self.lastdata = ""
        
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
        'view_sdsmikro': 'SDSmikro',
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
            root = ET.parse(urlopen('http://'+self.config['address']+"/xml.xml")).getroot()
            self.datalayer.p1 = root.find(".//s0_1/act").text
            self.datalayer.p2 = root.find(".//s0_3/act").text
            self.lastdata = strftime("%d.%m.%Y %H:%M:%S", gmtime())
            time.sleep(5)

    # module can receive GET messages by clients
    # @main.route('/<module>/<key>/<name>/<value>')
    def http_get(self, key, name, value):
        
        return   
