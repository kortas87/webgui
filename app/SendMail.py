import smtplib
from smtplib import SMTP_SSL as SMTP       # this invokes the secure SMTP protocol (port 465, uses SSL)
# from smtplib import SMTP                  # use this for standard SMTP protocol   (port 25, no encryption)
#from email.MIMEText import MIMEText
from email.mime.text import MIMEText


class SendMail:
    
    self = ''
    
    #init
    def __init__(self, configuration):
        self.configuration = configuration
        self.SMTPserver = ''
        self.sender = ''
        self.username = ''
        self.password = configuration['password']

    #def schedule():
    #    if not LionMail.mailSent and BmsLion.self.datalayer.stackmaxcell > 36400:
    #        LionMail.mailSent = True
    #        LionMail.send(subject = "Napeti dosahlo 3.64V", destination = ['petrkortanek@gmail.com'], content = str(BmsLion.self.datalayer))
    
    def start(self):
        print ("SendMail module started")
    
    def status(self):
        return ""
    
    def menu(self):
        return {}
        #return {
        #'overview':'view_modules',
        #'gauges': 'view_gauge',
        #'status':'view_status',
        #'settings':'view_settings'
        #}
    
    def terminate(self):
        a = ""
        
    def send(self, subject = "test mail", destination = '', content = "no content"):
        if destination == '':
            destination = self.configuration['destination']
        try:
            text_subtype = 'plain'
            msg = MIMEText(content, text_subtype)
            msg['Subject'] = subject
            msg['From'] = self.configuration['sender'] # some SMTP servers will do this automatically, not all

            conn = SMTP(self.configuration['SMTPserver'])
            conn.set_debuglevel(False)
            conn.login(self.configuration['username'], self.configuration['password'])
            try:
                conn.sendmail(self.configuration['sender'], destination, msg.as_string())
            finally:
                conn.close()
            
        except Exception as exc:
            print( "mail failed; %s" % str(exc) )
