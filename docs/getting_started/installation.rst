Installation
############


This document assumes you are familiar with Python and using command prompt or 
shell. It should outline the steps necessary for you to follow the 
:doc:`tutorial`.

Requirements
************
    
* `Python`_ 2.7
* `NumPy`_
* `SciPy`_
* `Matplotlib`_
* `PySide`_ (for gui)
* `IPython`_
* `NetworkX`_
* `PyPNG`_ 

.. _Python: http://www.python.org
.. _NumPy: http://numpy.scipy.org
.. _SciPy: http://www.scipy.org
.. _Matplotlib: http://matplotlib.org/
.. _PySide: http://qt-project.org/wiki/PySide
.. _IPython: http://ipython.org/
.. _NetworkX: http://networkx.lanl.gov/
.. _PyPNG: https://github.com/drj11/pypng

If you have installed all required packages simply install Pymote using::

    > pip install pymote

If you dont' have all required packages and/or want them and Pymote installed
in an isolated environemnt please follow steps below.


Windows
*******

Install latest version Python 2 using appropriate installers that can be found 
`here <http://www.python.org/download/>`_. General setup instructions can be 
found on this `link <http://docs.python.org/2/using/windows.html/>`_.


.. note::

    Instead of installing packages globally in this document we use 
    `virtualenv`_ to create isolated Python environment and then install 
    packages into this environment.

Virtualenv
==========
    
To install virtualenv first install
`distribute <http://pypi.python.org/pypi/distribute>`_ and
`pip <http://www.pip-installer.org/en/latest/>`_ by downloading 
`distribute_setup.py <http://python-distribute.org/distribute_setup.py>`_ and 
`get-pip.py <https://raw.github.com/pypa/pip/master/contrib/get-pip.py>`_ 
and then running following commands:
    
.. code-block:: bash
    
    > python distribute_setup.py
    > python get-pip.py

.. warning::

    For everything to run smooth you have to put in PATH environment variable 
    paths to ``python.exe`` (i.e. ``C:\Python27``) and path to Scripts folder
    (i.e. ``C:\Python27\Scripts``) and restart command prompt.

Install virtualenv::

    > pip install virtualenv

Now you can make a virtual environment in which all other packages are going to
be installed. First navigate to a directory in which you want to set up
environment and then run these commands:

.. code-block:: bash

    > virtualenv pymote_env
    > pymote_env\Scripts\activate.bat
    (pymote_env)>
    
Note the ``(pymote_env)`` prefix to prompt in the last line. This indicates 
that newly created environment located in directory ``pymote_env``is activated
and further installations using ``pip`` go into this new environment.


Required packages
=================

Next we should install required packages in this environment.

NumPy SciPy
-----------
These packages require compiling we use precompiled binaries to install
them into virtual environment using a this `solution <http://stackoverflow.com/a/6753898/1247955>`_:

#. Download `numpy binary <http://sourceforge.net/projects/numpy/files/NumPy/>`_ and `scipy binary <http://sourceforge.net/projects/scipy/files/scipy/>`_ superpack binaries
#. Extract downloaded exe files with 7-zip
#. Based on your processor support of `SSE <http://en.wikipedia.org/wiki/Streaming_SIMD_Extensions>`_ instructions install appropriate extracted exe files (nosse/sse2/sse3) using:

.. code-block:: bash

    (pymote_env)> easy_install numpy-x.y.z-<nosse/sse2/sse3>.exe
    (pymote_env)> easy_install scipy-i.j.k-<nosse/sse2/sse3>.exe
    
.. note::

    SSE3 instructions are supported by all `reasonably modern processors <http://en.wikipedia.org/wiki/SSE3#CPUs_with_SSE3>`_ but if you're not sure  
    try `CPU-Z <http://www.softpedia.com/get/System/System-Info/CPU-Z.shtml>`_.

Matplotlib
----------
`Matplotlib binary <https://github.com/matplotlib/matplotlib/downloads>`_
package is installed the same way as NumPy and SciPy in previous section.
Only difference is in the 3rd step where the extracted contents from directory 
`PLATLIB` should be copied to ``pymote_env/Lib/site-packages/`` directory.


Pyreadline
----------
For Pyreadline package use `easy_install` as ``pip`` currently installs version
1.7.1.dev-r0 which does not work with IPython:

.. code-block:: bash

    (pymote_env)> easy_install pyreadline


PySide
------
For GUI to work properly you need to install PySide Qt bindings for
Python. This is achieved by executing 
`following commands <http://stackoverflow.com/a/4673823/1247955>`_:

.. code-block:: bash

    (pymote_env)> easy_install PySide
    (pymote_env)> python pymote_env\Scripts\pyside_postinstall.py -install
    
Pymote
======

Finally to install Pymote and all other required packages use:

.. code-block:: bash

    (pymote_env)> pip install pymote

IPython config
==============
To set up and tweak IPython default profile first we need to tell it where to
look for it. IPython is using environment variable IPYTHONDIR to find out the
config files location. Open editor and load ``pymote_env\Scripts\activate.bat``
file. Add ``set IPYTHONDIR=%VIRTUAL_ENV%\.ipython`` at the top just below the
line that sets ``VIRTUAL_ENV`` environment variable. Next, on enviroment
deactivation IPYTHONDIR environment variable should be unset so edit
``pymote_env\Scripts\deactivate.bat`` and at the top just below the line
``@echo off`` insert this line ``set IPYTHONDIR=``.

Start IPython to create IPYTHONDIR directory or create it manually.

Copy pymote/conf/profile_pymote.py dir to IPYTHONDIR.

Start IPython using new profile and in pylab mode with qt4 backend::

    (pymote_env)> ipython --pylab=qt --profile=pymote


Quickstart console
==================
For quickstart IPython console with imported pymote and proper config and 
backend there is a batch script provided in ``pymote_env\bin\pymote.bat``.
It can be pinned to taskbar as a shortcut using instructions given in that file.

If Pymote and required packages are installed in dedicated virtual environment 
you should set PYMOTE_ENV environment variable to a path to the Pymote virtual 
environment directory.


.. 
    Ubuntu
    ******
    http://cysec.org/content/installing-matplotlib-and-numpy-virtualenv
    **TODO**.
    
    curl -O http://python-distribute.org/distribute_setup.py
    python distribute_setup.py
    easy_install pip

    Mac OSX
    *******

    **TODO** 

.. _virtualenv: http://www.virtualenv.org/
