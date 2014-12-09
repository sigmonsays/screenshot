
development 
=================

linux
--------------------


install python virtualenv 

      apt-get install -y python-virtualenv

setup a virtual environment

      virtualenv venv
      source venv/bin/activate

install dependencies

      python setup.py install

to make code changes in the working directory 

      python setup.py develop

mac osx
--------------------

Not sure this is correct but it seemed to work, Feedback welcome!

      pyenv install 2.7.7
      pyenv global 2.7.7
      export PYENV_VIRTUALENVWRAPPER_PREFER_PYVENV="true"
      eval "$(pyenv init -)"
      pyenv virtualenvwrapper

      python setup.py install
