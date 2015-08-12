import time
import threading
from time import gmtime, strftime
from app.webguilibs import webguilibs
from urllib.request import urlopen
import urllib
import base64

# each module must contain datalayer class which is then passed to views
class Camera_Datalayer:
    
    def __init__(self):
        self.lastupdate = 0
        self.lastshot = ""
    

class Camera:
    
    
    def __init__(self, configuration):
        self.config = configuration
        self.terminate_flag = 0
        self.running_flag = 0
        self.datalayer = Camera_Datalayer()
        
    
    def terminate(self):
        self.terminate_flag = 1
        self.thread.join()

    # status for some overview page...
    def status(self):
        return "OK cam"
        
    # menu items offered by module
    def menu(self):
        return {
        'view_camera': self.config['name'],
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
        while not self.terminate_flag:
            try:
                encodedstring = base64.encodestring(str.encode(self.config['username']+":"+self.config['password']))[:-1]
                auth = "Basic %s" % encodedstring.decode('utf-8')
                page = self.config['address']
                req = urllib.request.Request(page, None, {"Authorization": auth })
                handle = urllib.request.urlopen(req)
                timestamp = strftime("%Y-%m-%d_%H-%M-%S", gmtime())
                self.datalayer.lastshot = '/static/data/'+self.config['snapshotdir']+'/'+timestamp+".jpg"
                savedir = './app'+self.datalayer.lastshot
                with open(savedir,'wb') as f:
                    f.write(handle.read())
                
                self.datalayer.lastupdate = int(time.time())
                
            except Exception as e:
                print ("error getting image: "+str(self.config['address']))
                print (str(e))
            
            time.sleep(60)

    # module can receive GET messages by clients
    # @main.route('/<module>/<key>/<name>/<value>')
    def http_get(self, key, name, value):
        
        return ""
