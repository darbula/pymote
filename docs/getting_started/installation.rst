Installation
############


This document assumes you are familiar with Python and using command prompt or 
shell. It should outline the steps necessary for you to follow the 
:doc:`tutorial`.

Requirements
************
    
* `Python`_ higher release of 2.x
* `NumPy`_
* `SciPy`_
* `NetworkX`_
* `IPython`_
* `PyPNG`_ 
* `matplotlib`_
* `PyQT4`_ or `PySide`_ (only for gui)

.. note:: Since all required packages except PyQT4/PySide are mandatory, when 
          installing Pymote using ``pip``, ``pip`` should try to install them if 
          the're not already installed.

.. _Python: http://www.python.org
.. _NumPy: http://numpy.scipy.org
.. _SciPy: http://www.scipy.org
.. _NetworkX: http://networkx.lanl.gov/
.. _IPython: http://ipython.org/
.. _PyPNG: https://github.com/drj11/pypng
.. _matplotlib: http://matplotlib.org/
.. _PyQT4: http://www.riverbankcomputing.co.uk/software/pyqt/download
.. _PySide: http://qt-project.org/wiki/PySide


Windows
=======

Install latest version Python 2 using appropriate installers that can be found 
`here <http://www.python.org/download/>`_. General setup instructions can be 
found on this `link <http://docs.python.org/2/using/windows.html/>`_.


.. note::

    Instead of installing packages globally in this instructions we use 
    `virtualenv`_ to create isolated Python environment and then install 
    packages into this environment.

Virtualenv
----------
    
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

Now you can make an virtual environment in which all other packages get 
installed. First navigate to a directory in which you want to set up environment
and then run these commands:

.. code-block:: bash

    > virtualenv pymote_env
    > pymote_env\Scripts\activate.bat
    (pymote_env)>
    
Note the ``(pymote_env)`` prefix to prompt in the last line. This indicates 
that we have activated newly created environment located in directory 
``pymote_env``. Further installations using pip go into this new environment.


Packages
--------

Next we should install numpy, scipy and matplotlib packages in this environment. Since these
packages require compiling we use precompiled binaries to install them into 
virtual environment using a this 
`solution <http://stackoverflow.com/a/6753898/1247955>`_:

#. Download `numpy binary <http://sourceforge.net/projects/numpy/files/NumPy/>`_ and `scipy binary <http://sourceforge.net/projects/scipy/files/scipy/>`_ superpack binaries
#. Extract downloaded exe files with 7-zip
#. Based on your processor support of `SSE <http://en.wikipedia.org/wiki/Streaming_SIMD_Extensions>`_ instructions install appropriate extracted exe files (nosse/sse2/sse3) using:

.. code-block:: bash

    > easy_install numpy-x.y.z-<nosse/sse2/sse3>.exe
    > easy_install scipy-i.j.k-<nosse/sse2/sse3>.exe
    
.. note::

    SSE3 instructions are supported by all `reasonably modern processors <http://en.wikipedia.org/wiki/SSE3#CPUs_with_SSE3>`_ but if you're not sure  
    try `CPU-Z <http://www.softpedia.com/get/System/System-Info/CPU-Z.shtml>`_.


`Matplotlib binary <https://github.com/matplotlib/matplotlib/downloads>`_
package is installed the same way as numpy and scipy. Only 
difference is in the 3rd step where the extracted contents from directory 
`PLATLIB` should be copied to ``pymote_env/Lib/site-packages/`` directory.


For pyreadline package use `easy_install` as pip installs 1.7.1.dev-r0 which
does not work for iPython:

.. code-block:: bash

    > easy_install pyreadline
    

Finally to install Pymote and all other required packages use:

.. code-block:: bash

    > pip install pymote

iPython config
--------------
To set up and tweak IPython default profile first we need to tell it where to look for it. IPython is using environment variable IPYTHONDIR so open editor and load ``pymote_env\Scripts\activate.bat`` file. Add ``set IPYTHONDIR=%VIRTUAL_ENV%\.ipython`` at the top just below the line that sets ``VIRTUAL_ENV`` environment variable.
Next, on enviroment deactivation IPYTHONDIR environment variable should be unset so edit ``pymote_env\Scripts\deactivate.bat`` and at the top just below the line ``@echo off`` insert this line ``set IPYTHONDIR=``.

TODO: auto transfer profile_pymote dir to IPYTHONDIR 


GUI
---

For GUI to work properly you need to install PySide (or PyQt4?) Qt bindings? for
Python. This is achieved by executing 
`following commands <http://stackoverflow.com/a/4673823/1247955>`_:

.. code-block:: bash

    > easy_install PySide
    > python pymote_env\Scripts\pyside_postinstall.py -install



    
TODO: http://cyrille.rossant.net/making-pyqt4-pyside-and-ipython-work-together/

TODO: how to install sip (pyqt) in virtualenv -> pyside is default

TODO: how to install pth so that python_qt_binding is available

.. 
    Ubuntu
    ======
    http://cysec.org/content/installing-matplotlib-and-numpy-virtualenv
    **TODO**.

    Mac OSX
    =======

    **TODO** (Should setup everything up to but not including
    "pip install django-cms" like the above)

.. _virtualenv: http://www.virtualenv.org/
