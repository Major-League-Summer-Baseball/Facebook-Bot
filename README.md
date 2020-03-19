# Facebook Captains Bot
Allows captains to submit their scores and deal with getting information to people.

See the the Wiki Pages for [help](https://github.com/fras2560/mlsb-platform/wiki)

**Assumed Dependencies**:
* python 3
* pip

# Getting Started
If just making a small change then it recommended to just run the unittests. 

**TLDR**
```
pip install -r requirements.txt
# to run unittests
python -m unittest discover -s api/test
# want to run one suite
python -m unittest discover -s api/test -p <TEST_SUITE>.py
```

## Environment Variables
The following variables are used by MLSB Facebook bot (default in brackets):
* ADMIN: the admin's user name for the platform API ("admin") 
* PASSWORD: the admin password for the platform API ("password")
* PLATOFRM: the MLSB platform URL (http://localhost:5000)
* MONGODEB_URI: the Mongo DB URI (mongodb://localhost:27017/mlsb)
* PAGE_ACCESS_TOKEN: a token for Facebook page (None)
* VERIFY_TOKEN: a token used to verify that requests comes from Facebook (None)
The app does expect the the postgres database has had the tables initiated. To intiated the datbase can use

## Using Virtual Environment (recommended)
Virtual environment are used to separate packages for various packages. Another options is PipEnv. It allows a developer to switch between python packages and ensure they have the right packages and the appropriate versions for the given project.

To use first you create the virutal environment using something like
```
# second venv is the folder to create that stores virtual environment
python -m venv venv
```

Now you can activate the virtual environment using:
```
# on windows and assuming used venv folder
venv\scripts\activate.bat
# on linux and assuming used venv folder
source venv/bing/activate
```

Now any installed packages using `pip` will be isolated to the virtual environment. To deactivate
the virtual environment you can use:
```
deactivate
```

## Dependencies
Due to the facebook-bot being dependent on external services it is strongly recommended to use a docker setup. However, one can setup the MLSB platform and just set the appropriate environment variables to develop not using Docker.

### Docker Setup
---------------------------------------------------------------------
See getting started with [docker](https://docs.docker.com/get-started/)
Using the terminal navigate to the root the Facebook-Bot repository and run:
```
# build the docker image
docker-compose build
# bring the container up
docker-compose up -d
# wait a few seconds and then init the database
docker-compose exec mlsb python initDB.py -createDB -mock

# to bring down the stack
docker-compose down
```
The local verion of the website should be available at [locally](http://localhost:5000). The Facebook Bot should be available as [well](http://localhost:5001).

**Running unit tests in docker**
To run the whole suite of tests use:
```
docker-compose exec mlsb-bot python -m unittest discover -s api/test -p test*.py
```
To run a particular test suite use:
```
docker-compose exec mlsb-bot python -m unittest discover -s api/test -p <TEST_SUITE>.py
```

### Manual Setup
---------------------------------------------------------------------
This is a slightly more complex setup but it is possible. One would need to setup MLSB running on their local website and setup a mongo database.

##### MLSB
Grab the source code from [here](https://github.com/fras2560/mlsb-platform) and see the readme for how to get it setup.

**TLDR**
```
pip install -r requirements.txt
# root of mlsb platform repository
python runserver.py
```

##### Mongo
See the following tutorials for setting it up:
* [Windows](https://docs.mongodb.com/manual/tutorial/install-mongodb-on-windows/)
* [Linux](https://docs.mongodb.com/manual/administration/install-on-linux/)
* [Mac](https://treehouse.github.io/installation-guides/mac/mongo-mac.html)

Grab the source code from [here](https://github.com/fras2560/mlsb-platform) and see the readme for how to get it setup.

Once mongo is setup create a database called mlsb with a collection called users. Ensure that mongo database is availble on some port and set environment variable tto he DATABASE_URL mongodb://<USER>:<DBPASSWORD>@localhost:<PORT> (e.g. mongodb://admin:password@localhost:27018)

#### Set Environment Variables
When using the manual setup and setting most environment to reasonable defaults the following setup should work:
* PLATOFRM: http://localhost:5000 (unless it started on a different port)
* MONGODEB_URI: mongodb://localhost:27017/mlsb
* PAGE_ACCESS_TOKEN: set this based upon Facebbok token (see below)
* VERIFY_TOKEN: set it to some random string (remember for below)
---------------------------------------------------------------------

### Finally Hooking up Bot with Facebook
Most of these was taken from [here] and if need more clarification or guidance it is a good resource.

**Facebook Bot**
Follow the steps under["Set up facebook messenger"](https://dev.to/apcelent/how-to-create-a-facebook-messenger-bot-with-python-flask-50j2). Once you have the page access token set the PAGE_ACCESS_TOKEN environment variable and restart the bot server.

**Ngrok**
[Install ngrok](https://ngrok.com/download)
Launch it from the command line to point to the Facebook bot.
```
# port may change depending on what port the bot is running on
./ngrok http -bind-tls=true 5001
# should see output something like
ngrok by @inconshreveable                                                                                               (Ctrl+C to quit)
Session Status                online
Session Expires               7 hours, 59 minutes
Version                       2.3.35
Region                        United States (us)
Web Interface                 http://127.0.0.1:4040 
Forwarding                    https://e6f06512.ngrok.io -> http://localhost:5001
```
Set the Facebook Bot Callback URL to the forwarding ngrok.io the output by ngrok.

# Style
As for style it is recommended that one uses flake8 for checking style. The
following commands can help get feedback about any incorrect styling issues.

```
pip install flake8
flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics --exclude=api/__init__.py,api/website/views.py
```

# Github Actions
Working on Github actions. For now it will run unittests and styling issues
on PRs to Development and Master.

Docker images are push for commits to master and development

# Additional Sources
TODO
