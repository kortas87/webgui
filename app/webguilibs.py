

class webguilibs:
    def niceUptime(seconds):
        out = ""
        days = int(seconds/(24*3600))
        if (days >= 1):
            seconds -= days*24*3600
            
        hours = int(seconds/3600)
        if (hours >= 1):
            seconds -= hours*3600
        
        minutes = int(seconds/60)
        if (minutes >= 1):
            seconds -= minutes*60
            
        out = str(days)+"d "+str(hours).zfill(2)+":"+str(minutes).zfill(2)+":"+str(seconds).zfill(2)
        return out
