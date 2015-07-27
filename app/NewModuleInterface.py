

# each module must contain datalayer class which is then passed to views
class NewModuleInterface_Datalayer:
    MAX_MODULES = 16
    
    def __init__(self):
        #self.alert = ""
        #self.modules = [Module() for x in range(self.MAX_MODULES)]

class NewModuleInterface:
    
    
    def __init__(self, configuration):
        #configuration is given in config.py
        
        #important!
        self.datalayer = NewModuleInterface_Datalayer()
    
    def terminate(self):
        #for example finish modules thread
        #self.thread.join()

    # status for some overview page...
    def status(self):
        return "OK, 3.65V, <20A"
        
    # menu items offered by module
    # each menu item is connected with a view
    # view_xxx must be unique name between all modules! it is also filename...
    def menu(self):
        return {
        'menu1': 'view_menu1',
        'menu2': 'view_menu2',
        }

    # start
    def start(self):
        
        # can start new thread to run continuously...
        # self.thread = threading.Thread(target=self.run)
        # self.thread.start()

        print ("New module started")
    
  
        
    def run(self):
        print ("run code");
        #while not self.terminate_flag:
        #    keep doing something...

    # module can receive GET messages by clients
    # @main.route('/<module>/<key>/<name>/<value>')
    def http_get(self, key, name, value):
        
        return   
