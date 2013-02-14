Installation
############


This document assumes you are familiar with Python and using command prompt or shell. It should 
outline the necessary steps to install software needed for using Pymote i.e. to start with the 
:doc:`tutorial`.

Requirements
************
    
* `Python`_ 2.7
* `Setuptools`_ 
* `NumPy`_
* `SciPy`_
* `Matplotlib`_
* `PySide`_ (for gui)
* `IPython`_ 0.13.1
* `NetworkX`_
* `PyPNG`_ 

.. _Python: http://www.python.org
.. _Setuptools: http://pypi.python.org/pypi/setuptools
.. _NumPy: http://numpy.scipy.org
.. _SciPy: http://www.scipy.org
.. _Matplotlib: http://matplotlib.org/
.. _PySide: http://qt-project.org/wiki/PySide
.. _IPython: http://ipython.org/
.. _NetworkX: http://networkx.lanl.gov/
.. _PyPNG: https://github.com/drj11/pypng

You can install all required packages using their respective instructions for your platform. Once 
you have installed all required packages simply install Pymote using::

    > pip install pymote

If you don't have all required packages and/or want them installed in an isolated environment in 
minimal number of steps please follow the instructions below.


Windows
*******

Install Python 2.7 using appropriate `installers <http://www.python.org/download/>`_. Quick link:
`Python 2.7.3 x86 MSI Installer <http://www.python.org/ftp/python/2.7.3/python-2.7.3.msi>`_

.. warning::

    After instalation append paths to ``python.exe`` (i.e. ``C:\Python27``) and path to directory ``Scripts`` folder (i.e. ``C:\Python27\Scripts``) in the PATH 
    `environment variable <http://superuser.com/a/284351/169714>`_.


Virtualenv
==========

Instead of installing packages globally in these instructions we use `virtualenv`_ to create 
isolated Python environment and then install packages into this environment.
    
To install virtualenv first install `distribute <http://pypi.python.org/pypi/distribute>`_ and
`pip <http://www.pip-installer.org/en/latest/>`_ by downloading 
`distribute_setup.py <http://python-distribute.org/distribute_setup.py>`_ and 
`get-pip.py <https://raw.github.com/pypa/pip/master/contrib/get-pip.py>`_ and then running 
following commands in the command prompt:
    
.. code-block:: bash
    
    > python distribute_setup.py
    > python get-pip.py

After this distribute should be installed so downloaded files can be deleted.

Install virtualenv::

    > pip install virtualenv

To make a virtual environment in which all other packages are going to be installed first navigate
to the directory in which you want to set up environment and then run these commands::

    > virtualenv pymote_env
    New python executable in pymote_env\Scripts\python.exe
    Installing setuptools................done.
    Installing pip...................done.
    > pymote_env\Scripts\activate
    (pymote_env)>
    
Note the ``(pymote_env)`` prefix to prompt in the last line. This indicates that newly created 
environment located in directory ``pymote_env`` is activated so further packages are installed
into this new environment. You can deactivate environment by running command ``deactivate``.

Set ``PYMOTE_ENV`` environment variable as path to ``pymote_env`` directory. This way all
executables not being started from the console should know where to look for the environment and
installed packages.

.. note::

    In Windows Vista and later instead of Control Panel > System GUI you can use command
    ``setx PYMOTE_ENV "C:\path\to\pymote_env"`` to save environment variable permanently.

Open editor and load ``pymote_env\Scripts\activate.bat`` file.
Add ``set IPYTHONDIR=%VIRTUAL_ENV%\.ipython`` at the top below the line that sets ``VIRTUAL_ENV``
environment variable. Next, in ``pymote_env\Scripts\deactivate.bat`` insert line 
``set IPYTHONDIR=`` at the top below the line ``@echo off``.
This way IPython package which is not yet fully compatible with the virtualenv knows where to look
for its conguration files.

.. warning::

    After setting the environment variable and changing activate and deactivate scripts you should
    restart the command prompt and activate ``pymote_env``. If all goes well commands 
    ``echo %PYMOTE_ENV%`` and ``echo %IPYTHONDIR%`` should print appropriate values.

Required packages
=================

All required packages are installed in previously created environment so before continuing ensure 
that the environment is activated This is indicated with prompt prefix i.e. ``(pymote_env)``.

NumPy and SciPy
---------------
Since normal installation of these packages requires compiling we make a shortcut by using 
precompiled binaries and installing them into virtual environment using this 
`solution <http://stackoverflow.com/a/6753898/1247955>`_:

#. Download `numpy binary <http://sourceforge.net/projects/numpy/files/NumPy/>`_ and `scipy binary <http://sourceforge.net/projects/scipy/files/scipy/>`_ superpack binaries
#. Extract downloaded exe files with `7-zip <http://www.7-zip.org/download.html>`_
#. Based on your processor support of `SSE <http://en.wikipedia.org/wiki/Streaming_SIMD_Extensions>`_ instructions install appropriate extracted exe files (nosse/sse2/sse3) using:

.. code-block:: bash

    (pymote_env)> easy_install numpy-x.y.z-<nosse/sse2/sse3>.exe
    (pymote_env)> easy_install scipy-i.j.k-<nosse/sse2/sse3>.exe
    
.. note::

    SSE3 instructions are supported by all 
    `reasonably modern processors <http://en.wikipedia.org/wiki/SSE3#CPUs_with_SSE3>`_. If 
    you're not sure try `CPU-Z <http://www.softpedia.com/get/System/System-Info/CPU-Z.shtml>`_.

Matplotlib
----------
`Matplotlib binary <https://github.com/matplotlib/matplotlib/downloads>`_
package is installed the same way as NumPy and SciPy in previous section.
Only difference is in the 3rd step where the extracted contents from directory 
``PLATLIB`` should be copied to ``pymote_env/Lib/site-packages/`` directory::

    > xcopy /s matplotlib-1.2.0.win32-py2.7\PLATLIB\* pymote_env\Lib\site-packages


Pyreadline
----------
For Pyreadline package use ``easy_install`` as ``pip`` currently installs version
1.7.1.dev-r0 which does not work well with IPython:

.. code-block:: bash

    (pymote_env)> easy_install pyreadline


PySide
------
For Pymote GUI part of the library PySide Qt bindings for Python should be installed. This is 
achieved by executing `following commands <http://stackoverflow.com/a/4673823/1247955>`_:

.. code-block:: bash

    (pymote_env)> easy_install PySide
    (pymote_env)> python pymote_env\Scripts\pyside_postinstall.py -install
    
Pymote
======

Finally in order to download and install Pymote and all other required packages use:

.. code-block:: bash

    (pymote_env)> pip install pymote

To check all packages installed in the environment run ``pip freeze`` and the output should look 
something like this::

    (pymote_env)> pip freeze
    Pymote==0.1.1
    ipython==0.13.1
    matplotlib==1.2.0
    networkx==1.7
    numpy==1.6.2
    pypng==0.0.14
    pyreadline==1.7.1
    pyside==1.1.2
    scipy==0.11.0

IPython config
==============
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
