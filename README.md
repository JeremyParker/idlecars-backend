# idlecars
The repo for the idlecars backend. For a demo of all functionality see https://www.youtube.com/watch?v=dQi7ZiM23jg

'server' is the main api for the owner and driver apps

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
* redis (optional)
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
Occasionally, we add manual backfills. To execute a manual backfill, follow this pattern:
```
terminal_prompt$ ./manage.py shell
Python 2.7.9 (default, Feb 10 2015, 03:28:08) 
[GCC 4.2.1 Compatible Apple LLVM 6.0 (clang-600.0.56)] on darwin
Type "help", "copyright", "credits" or "license" for more information.
(InteractiveConsole)
>>> from credit.backfills import _20151207_backfill_customers
>>> _20151207_backfill_customers.run_backfill_customers()
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

### License
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
