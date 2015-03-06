# idlecars
The Idle Cars webapp

To set up a local dev environment

Have a Heroku account and get added to the idlecars app

Make sure you have installed: (see http://docs.python-guide.org/en/latest/starting/install/osx/)
Python 2.7.9
setuptools
pip
virtualenv

Also install:
virtualenvwrapper
Heroku toolbelt: https://toolbelt.heroku.com/
Postgres: http://postgresapp.com/

Create a virtual env for this project with the command
mkvirtualenv idlecars

Then choose to use that virtual env with the command (and every time you restart a shell?)
workon idlecars

Install all the dependencies
pip install -r requirements.txt

create a database in postgres called 'idlecars'. Launch psql, and enter:
CREATE DATABASE idlecars;

set environment variable
export DJANGO_SETTINGS_MODULE="idlecars.local_settings"

python manage.py syncdb --settings=idlecars.local_settings
You will be prompted to create a superuser. Create user 'admin' with password 'idlecars'

Note - be sure to run
workon idlecars
to make sure your virtualenv is set to the right virtualenv



I like to use P4Merge as a visual merge tool:
$ git config --global merge.tool p4mergetool
$ git config --global mergetool.p4mergetool.cmd \
"/Applications/p4merge.app/Contents/Resources/launchp4merge \$PWD/\$BASE \$PWD/\$REMOTE \$PWD/\$LOCAL \$PWD/\$MERGED"
$ git config --global mergetool.p4mergetool.trustExitCode false
$ git config --global mergetool.keepBackup false

... and as a visual diff tool:
$ git config --global diff.tool p4mergetool
$ git config --global difftool.p4mergetool.cmd \
"/Applications/p4merge.app/Contents/Resources/launchp4merge \$LOCAL \$REMOTE"

Then to see diffs
git difftool

