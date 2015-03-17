# idlecars
The repo for Idle Cars.

'server' is the webapp.

## Local environment setup

Have a Heroku account and get added to the idlecars app

Make sure you have installed: (see http://docs.python-guide.org/en/latest/starting/install/osx/)

* Python 2.7.9
* setuptools
* pip
* virtualenv

Also install:

* virtualenvwrapper
* Heroku toolbelt: https://toolbelt.heroku.com/
* Postgres: http://postgresapp.com/

Create a virtual env for this project with the command
```
mkvirtualenv -p [path_to_python(something like /usr/local/bin/python)] idlecars
```

Then choose to use that virtual env with the command
```
workon idlecars
```
(...and use this command to switch virtualenv every time you restart a shell?)


Install all the dependencies
```
pip install -r requirements.txt
```

set environment variable in your .bashrc (or wherever you like to set environment variables.)
```
export DJANGO_SETTINGS_MODULE="idlecars.local_settings"
```

Create a database in postgres called 'idlecars'. Launch psql, and enter:
```
CREATE DATABASE idlecars;
```

Set up the local database tables:
```
python manage.py syncdb --settings=idlecars.local_settings
```
You will be prompted to create a superuser. Create user 'admin' with password 'idlecars'. (Not sure if this will be necessary, but we might need a common user for unit tests.)

### Running the server
Foreman is a ruby gem that is installed with the heroku toolbelt. It will run your local server.
```
foreman start
```

### Running the tests
run
```
python manage.py test server
```
to run the unit test suite. All the tests should pass. To run the tests with debug enabled, run
```
python manage.py test server --nocapture
```

### Merge tool
Personally, I like to use P4Merge as a visual merge tool:

```
git config --global merge.tool p4mergetool
git config --global mergetool.p4mergetool.cmd \
"/Applications/p4merge.app/Contents/Resources/launchp4merge \$PWD/\$BASE \$PWD/\$REMOTE \$PWD/\$LOCAL \$PWD/\$MERGED"
git config --global mergetool.p4mergetool.trustExitCode false
git config --global mergetool.keepBackup false
```
... and as a visual diff tool:
```
git config --global diff.tool p4mergetool
git config --global difftool.p4mergetool.cmd \
"/Applications/p4merge.app/Contents/Resources/launchp4merge \$LOCAL \$REMOTE"
```

Then to see diffs:
```
git difftool
```
