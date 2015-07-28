from flask import render_template, session, redirect, url_for, current_app
from . import main
import time

import config

# get the main page /
@main.route('/', methods=['GET','POST'])
def index():
    
    return render_template('default.html', datalayer = config.modules[config.default_variables['first_view_mod']]['obj'].datalayer, defaults = config.default_variables, menu = config.menu_items)

# get any view (load module view once)
@main.route('/view/<view>')
def GET_view(view):
    if not (view in config.menu_items):
        return render_template('error.html', msg='Given view does not exist.')
    
    # we are using the same templates for different instances of the same class
    parts = view.split("_")
    if (len(parts) == 3):
        realview   = parts[0]+"_"+parts[1]
    else:
        realview = view

    module_name = config.menu_items[view].module
    
    if (config.modules[module_name]['enabled']):
        return render_template(realview+'.html', datalayer = config.modules[module_name]['obj'].datalayer)

# get data update for templates (periodic updates)
@main.route('/data/<randomkey>/<view>')
def GET_data(randomkey,view):
    general = {}
    general['uptime'] =  human_uptime() #time.time()
    general['time']   = int(time.time())
    
    if not (view in config.menu_items):
        return render_template('error.html', msg='Given module does not exist.')
    
    # we are using the same templates for different instances of the same class
    parts = view.split("_")
    if (len(parts) == 3):
        realview   = parts[0]+"_"+parts[1]
    else:
        realview = view
    
    module_name = config.menu_items[view].module
    return render_template(realview+'_data.html', datalayer = config.modules[module_name]['obj'].datalayer, general = general)


# send anything to module and get response or empty page
@main.route('/<module>/<secretkey>/<name>/<value>/<randomkey>')
def GET_module(module='',secretkey='',name='',value='',randomkey=None):
    
    if not (module in config.modules) or not config.modules[module]['enabled']:
        return render_template('error.html', msg='Given module does not exist.')
    
    out = config.modules[module]['obj'].http_get(secretkey, name, value);
    
    code = 200
    if (out == ''):
        code = 204
    
    return (out, code)



from matplotlib import pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.dates import AutoDateFormatter, AutoDateLocator, date2num
# this will be moved to BmsLion module - in case we are drawing any charts...
# all data will be requested via:
#                                   def GET_module
@main.route('/fig/<param1>/<param2>')
def GET_plot(param1="1", param2="2"):
    
    plt.plot(date2num(time),values)
    plt.title("Quant SOC reset")
    plt.xlabel("time")
    plt.ylabel("voltage")
    # the the x limits to the 'hours' limit
    #plt.xlim(0, 23)
    # set the X ticks every 2 hours
    #plt.xticks(range(0, 23, 2))
    xtick_locator = AutoDateLocator(minticks=5, maxticks=5)
    xtick_formatter = AutoDateFormatter(xtick_locator)
    ax = plt.axes()
    ax.xaxis.set_major_locator(xtick_locator)
    ax.xaxis.set_major_formatter(xtick_formatter)
    plt.grid()
    
    buf = io.BytesIO()
    plt.savefig(buf, format = 'png')
    buf.seek(0)
    #plt.show()
    return send_file(buf, mimetype='image/png')


# Gives a human-readable uptime string
def human_uptime():
     try:
         f = open( "/proc/uptime" )
         contents = f.read().split()
         f.close()
     except:
        return "Cannot open uptime file: /proc/uptime"
 
     total_seconds = float(contents[0])
 
     # Helper vars:
     MINUTE  = 60
     HOUR    = MINUTE * 60
     DAY     = HOUR * 24
 
     # Get the days, hours, etc:
     days    = int( total_seconds / DAY )
     hours   = int( ( total_seconds % DAY ) / HOUR )
     minutes = int( ( total_seconds % HOUR ) / MINUTE )
     seconds = int( total_seconds % MINUTE )
 
     # Build up the pretty string (like this: "N days, N hours, N minutes, N seconds")
     string = ""
     if days > 0:
         string += str(days) + "" + (days == 1 and "d" or "d" ) + ""
     if len(string) > 0 or hours > 0:
         string += str(hours) + "" + (hours == 1 and "h" or "h" ) + ""
     
     string += str(minutes*60+seconds)+"s"
     return string;
