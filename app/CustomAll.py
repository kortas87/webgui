import time
import threading
from time import gmtime, strftime
from app.webguilibs import webguilibs

import config

# each module must contain datalayer class which is then passed to views
class CustomAll_Datalayer:
    
    def __init__(self):
        self.sds_policko = 0
        self.sds_doma    = 0
        self.midnite     = 0
        

class CustomAll:
    
    
    def __init__(self, configuration):
        self.config = configuration
        self.terminate_flag = 0
        self.running_flag = 0
        self.datalayer = CustomAll_Datalayer()
        
    
    def terminate(self):
        self.terminate_flag = 1
        self.thread.join()

    # status for some overview page...
    def status(self):
        return "OK"
        
    # menu items offered by module
    def menu(self):
        return {
        'view_customall': self.config['name'],
        }
  
    def start(self):
        
        if 0 == self.running_flag:
            self.thread = threading.Thread(target=self.run)
            self.terminate_flag = 0
            self.thread.start()
    
    def status(self):
        
        return "Last seen :"+self.lastdata
        
    def run(self):
        self.running_flag = 1
        time.sleep(3)
        
        # assign objects to single datalayer...
        self.datalayer.sds_policko = config.modules['SDSmikro_policko']['obj'].datalayer
        self.datalayer.sds_doma = config.modules['SDSmikro_doma']['obj'].datalayer
        self.datalayer.midnite = config.modules['Midnite']['obj'].datalayer
        
        while not self.terminate_flag:
            #do some more calculation? ...
            time.sleep(5)

    # module can receive GET messages by clients
    # @main.route('/<module>/<key>/<name>/<value>')
    def http_get(self, key, name, value):
        
        return ""
