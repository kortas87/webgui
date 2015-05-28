
import sqlite3
import os

class BmsLionSQL:
    
    def __init__(self, configuration):
        self.configuration = configuration
        
        #self.conn = pymysql.connect(host="localhost", user="root",passwd="asdf", db="lion")
        #self.cur = self.conn.cursor(pymysql.cursors.DictCursor)
        #self.cur = self.conn.cursor()
        #self.conn.autocommit(True)
        
    def terminate(self):
        print ("finishing")

    def start(self):
        
        conn = sqlite3.connect(self.configuration['db_filename'])

        if not os.path.exists(self.configuration['db_filename']):
            print ('Need to create schema')
        else:
            print ('Database exists, assume schema does, too.')
    
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
