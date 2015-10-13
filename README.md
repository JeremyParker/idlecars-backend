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
* redis
  * `brew install redis` on OSX
  * `redis-server &` to boot it up
* direnv
  * `brew install direnv` on OSX
  * get the latest `.envrc` from another dev and put it in the project root
  * `direnv allow` to enable direnv

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

### Running e2e tests
There is a special setup for running e2e (integration) test from the angular web app client.
Before you start the server, make sure you have created the test database in psql: `create database idlecars_test;`.
Run the migrations to make sure the database is prepared:
`python manage.py migrate --settings='idlecars.e2e_test_settings'`
Then start the e2e test server:
`python manage.py runserver 9999 --settings='idlecars.e2e_test_settings'`

### Running integration tests
Integration test support is pretty iffy at the time of this writing. To test the Braintree integration against the
sandbox, follow the instructions above to `create database idlecars_integration_test;`
Then run
`./manage.py test_braintree_sandbox --settings='idlecars.integration_test_settings'`

### Deployment
We have two apps on Heroku that we deploy to.
Staging
* name: staging-idlecars
* url: staging-idlecars.heroku.com

Production
* name: idlecars
* url: idlecars.com

To deploy to staging:
```
git push staging master
heroku run python manage.py migrate --app staging-idlecars
```

To deploy to production:
```
git push heroku master
heroku run python manage.py migrate --app idlecars
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

### Upgrading up the database
Here is an example of the command run to upgrade the database on May the Fourth, 2015.
However, future upgrades can be performed by creating a follower then promoting the follower.
```
heroku maintenance:on -a idlecars
heroku ps:scale worker=0 -a idlecars
heroku pg:copy HEROKU_POSTGRESQL_CRIMSON_URL HEROKU_POSTGRESQL_GREEN_URL -a idlecars
heroku ps:scale worker=1 -a idlecars
heroku maintenance:off -a idlecars
heroku promote HEROKU_POSTGRESQL_GREEN -a idlecars
```

### Restoring db from backup
```
heroku pg:reset DATABASE_URL --app staging-idlecars
heroku pg:backups restore 'quoted_url_from_backup_service.dump' DATABASE_URL --app staging-idlecars
heroku run python manage.py migrate
heroku run python manage.py shell
>> run any backfills that need running
```

