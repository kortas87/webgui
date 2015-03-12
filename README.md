# webgui

## Prerequests

following steps to setup a working Enviroment:

~~~
    python3 -m venv LS_env

    source LS_env/bin/activate

    pip install -r requirements.txt
~~~

for Ubuntu 14.04:
    
~~~    
    python3 -m venv LS_env --without-pip
    
    source LS_env/bin/activate
    wget https://bootstrap.pypa.io/get-pip.py
    python get-pip.py
    deactivate
    source bin/activate
~~~

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

