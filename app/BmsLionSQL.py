
import sqlite3
import os

class BmsLionSQL:
    
    def __init__(self, configuration):
        self.c = configuration
        
        #self.conn = pymysql.connect(host="localhost", user="root",passwd="asdf", db="lion")
        #self.cur = self.conn.cursor(pymysql.cursors.DictCursor)
        #self.cur = self.conn.cursor()
        #self.conn.autocommit(True)
        
    def terminate(self):
        print ("finishing")
    
    def status(self):
        return ""

    def start(self):
        db_is_new = os.path.exists(self.c['db_filename'])
        
        with sqlite3.connect(self.c['db_filename']) as conn:
            if not db_is_new:
                print ('Creating schema')
                with open(self.c['db_scheme'], 'rt') as f:
                    schema = f.read()
                print ('Inserting initial data')
                conn.executescript(schema)
            
            else:
                print ('Database exists, assume schema does, too.')
    
    def menu(self):
        return {}
        #return {
        #'overview':'view_modules',
        #'gauges': 'view_gauge',
        #'status':'view_status',
        #'settings':'view_settings'
        #}
    
    
    def writequery(self, valtype, index, value, ):
                 
        query = "INSERT INTO `lion`.`values5` (`vid`, `type`, `index`, `value`, `timestamp`) VALUES (NULL, '{}', '{}', '{}', CURRENT_TIMESTAMP)".format(valtype, index, value)
        #print(query)
        self.cur.execute(query)
    
    def getList(self):
        rows = self.cur.execute("SELECT value, timestamp FROM  `values5` WHERE `type` = 10 and value <> 0 ORDER BY vid DESC LIMIT 700,850")
        data = self.cur.fetchall()
        return zip(*data)
          
    
    def commit(self):
        self.conn.commit()

    def cellV(self, index, value):
        self.writequery(1, index, value)
    
    def cellT(self, index, value):
        self.writequery(3, index, value)
    
    def cellVmin(self, value):
        self.writequery(7, 0, value)    
    
    def cellVmax(self, value):
        self.writequery(8, 0, value)        
    
    def cellTmin(self, value):
        self.writequery(9, 0, value)    
    
    def cellTmax(self, value):
        self.writequery(10, 0, value) 
    
    def stackV(self, value):
        self.writequery(2, 0, value)
    
    def stackI(self, value):
        self.writequery(4, 0, value)
    
    def SOC(self, value):
        self.writequery(5, 0, value)
        
    def PEC(self, value):
        self.writequery(6, 0, value)



#@main.route('/data/<param>/<page>')
#def GET_data(param, page):
#    global sql_i, uptime
#    global uptime
    # sql testing here at the moment...
#    if BmsLion.self.datalayer.sqllog == 1:
#        sql_i.stackV(BmsLion.self.datalayer.stackvolt/100)
#        sql_i.stackI(BmsLion.self.datalayer.stackI/10000)
#        sql_i.cellVmin(BmsLion.self.datalayer.stackmincell/10000)
#        sql_i.cellVmax(BmsLion.self.datalayer.stackmaxcell/10000)
#        sql_i.cellTmin((BmsLion.self.datalayer.stackmaxtemp-27315)/100)
#        sql_i.cellTmax((BmsLion.self.datalayer.stackmintemp-27315)/100)    
#        sql_i.SOC(BmsLion.self.datalayer.stacksoc/100)
#        sql_i.PEC(BmsLion.self.datalayer.cpuPEC)
#        sql_i.commit()
    
    #cellcounter = 0
    #for module in BmsLion.self.datalayer.Modules:
    #    for cell in module.Cells:
    #        if cell.volt > 500:
    #            sql_i.cellV(cellcounter, cell.volt/10000)
    #            sql_i.cellT(cellcounter, (cell.temp-27315)/100 )
    #            cellcounter +=1
   
#    BmsLion.self.datalayer.uptime = int(time.time() - uptime)
#    return render_template(page+'_data.html', datalayer = config.modules['BmsLion']['obj'].datalayer)
    
