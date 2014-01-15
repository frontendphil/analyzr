analyzr
=======

## Background ##

## Installation ##

### Dependencies ###

The following dependencies have to be installed manually as they are a prerequisite or can't be handled by a package manager.

* [subversion](http://subversion.apache.org/packages.html)
* [git](http://git-scm.com/download/)
* [mercurial](http://mercurial.selenic.com/)
* [pip](http://www.pip-installer.org/en/latest/index.html)
* [pysvn](http://pysvn.tigris.org/docs/pysvn.html)
* Something to compile the less file (e.g. [LessApp](http://incident57.com/less/))
    * a bash script is also available but requires a `lessc` command to be present on your system

All other dependencies can be installed using:

```bash
pip install -r requirements.txt
```

* [Django](https://www.djangoproject.com/download/)
    * [django-annoying](https://github.com/skorokithakis/django-annoying)
    * [django-timezone-field](https://github.com/mfogel/django-timezone-field)
    * [django-compressor](http://django-compressor.readthedocs.org/en/latest/)
* [GitPython](http://pythonhosted.org/GitPython/0.3.1/)
* [Jinja2](http://jinja.pocoo.org/docs/)
* [Pygments](http://pygments.org/)
* [south](http://south.readthedocs.org/en/latest/)
* [lizard](https://github.com/terryyin/lizard)
* [python-dateutil](http://labix.org/python-dateutil)

### Django Setup ###

There is not much to be done. Only setting up the database and running all migrations.

```bash
python manage.py syncdb
python manage.py migrate parsr
```
