# webgui

## Prerequests


LINUX EXPERIENCED user - basically follow these steps:

~~~
    python3 -m venv LS_env
    source LS_env/bin/activate
    pip install -r requirements.txt
~~~


Otherwise follow these steps to setup a working Enviroment (more detailed):

~~~
    su
    apt-get update
    apt-get install python3 git
    exit
    cd ~/
    git clone https://github.com/b9i/webgui.git
    cd webgui
    python3 -m venv LS_env --without-pip
    source LS_env/bin/activate
    wget https://bootstrap.pypa.io/get-pip.py
    python get-pip.py
    pip install -r requirements.txt
~~~

## Running the application

~~~
    # su (probably need to run as root to access USB serial devices)
    source LS_env/bin/activate
    
    # debug
    ./manage.py runserver -R -p 8080 -h 0.0.0.0
    
    # production use with gunicorn server (+ apt-get install nginx)
    #gunicorn webgui:app -b 0.0.0.0:5000 --log-file=log.txt
~~~

Start browser and enter http://localhost:8080 in address bar


## Migration the Database

for a new Project:

~~~ 
    ./manage.py db init
    ./manage.py db upgrade
~~~
this will create the folder "migrations" and create the migration from the models.py
if the folder exist ( is checked in the git repo ), only do:

~~~
    ./manage.py db upgrade
~~~

