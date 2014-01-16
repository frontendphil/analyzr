analyzr
=======

## Background ##

Master thesis background description

## Installation ##

The following dependencies have to be installed manually as they are a prerequisite or can't be handled by a package manager. I strongly recommend using [virtualenv](http://www.virtualenv.org/en/latest/) because you are going to install a bunch of python packages and you probably don't want all of them system wide all the time. Also, now that you are using [virtualenv](http://www.virtualenv.org/en/latest/), you might also want to have a look at [virtualenv-wrapper](http://virtualenvwrapper.readthedocs.org/en/latest/).

##### Version control systems #####
* [subversion](http://subversion.apache.org/packages.html)
* [git](http://git-scm.com/download/)
* [mercurial](http://mercurial.selenic.com/)

##### Package control systems #####
* [pip](http://www.pip-installer.org/en/latest/index.html) (Python package manager)
* [npm](https://npmjs.org/) (This is the easiest way to install [complexity-report](https://npmjs.org/package/complexity-report) and [lessc](https://npmjs.org/package/less))

##### Python binding for SVN #####
No, they are not available through pip and make sure you install the svn bindings which match your OS and svn version.

* [pysvn](http://pysvn.tigris.org/docs/pysvn.html)

##### Measurement tools #####
* [complexity-report](https://npmjs.org/package/complexity-report)

##### Miscellanious #####
* Something to compile the less file (e.g. [LessApp](http://incident57.com/less/))
    * a bash script is also available but requires a [lessc](https://npmjs.org/package/less) command to be present on your system

All other dependencies can be installed using:

```bash
pip install -r requirements.txt
```

* [Django](https://www.djangoproject.com/download/)
    * [django-annoying](https://github.com/skorokithakis/django-annoying)
    * [django-timezone-field](https://github.com/mfogel/django-timezone-field)
    * [django-compressor](http://django-compressor.readthedocs.org/en/latest/)
* [GitPython](http://pythonhosted.org/GitPython/0.3.1/) (Python bindings for git)
* [Jinja2](http://jinja.pocoo.org/docs/) (Template engine)
* [Pygments](http://pygments.org/) (Syntax highlighting)
* [south](http://south.readthedocs.org/en/latest/) (Database migrations)
* [lizard](https://github.com/terryyin/lizard) (C Metrics)
* [python-dateutil](http://labix.org/python-dateutil)

### Django Setup ###

There is not much to be done. Only setting up the database and running all migrations.

```bash
python manage.py syncdb
python manage.py migrate parsr
```
