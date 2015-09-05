# wordify
the modified project
su pw is in comment

<h1> running it </h1>
1. install virtualenv and virtualenvwrapper through pip install command
2. create a virtual environment first by typing mkvirtualenv myvenv
3. if it says command not found, update ~/.bashrc file by including 
	venvwrap="virtualenvwrapper.sh"
    venvwrap=`/usr/bin/which $venvwrap`
    source $venvwrap
   the above lines at the end. (make sure which virtualenvwrapper.sh command returns something)
4. if 2. fires successfully then type pip freeze, it should show wheel only
5. if it shows more than that, comment out the PYTHONPATH variable in the .bashrc file
6. so now virtualenv is setup, clone this repository: git clone https://github.com/murtraja/wordify
7. now look for requirements.txt and fire pip install -r requirements.txt command to install dependencies
8. run the python server python manage.py runserver
9. check it on localhost:8000/words
10. enter deactivate to leave the virtualenv and workon myvenv to get it back!

P.S. there is no need as such for virtual environment but it makes the life much simpler!
