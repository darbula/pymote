Starting Pymote
***************
Before starting, make sure that virtual environment is activated (:ref:`linux <linux-venvact>`, 
:ref:`windows <windows-venvact>`), unless packages are installed systemwide, which is 
:ref:`discouraged <discourage-systemwide>` and check all :ref:`dependencies <pymote-deps>`.


Interactive console (IPython)
-----------------------------
To use Pymote from the interactive console (IPython) start provided program 
``ipymote`` (in Windows ``ipymote.exe``) with previously activated virtual environment::
    
    (pymote_env)> ipymote

.. note::

    **Windows only**
    
    The recommended way to avoid starting command prompt, activating the virtual environment and
    running ``ipymote`` in it is to make a shortcut to the ``ipymote.exe`` file on the desktop, 
    taskbar or start menu.

    This way console can be additionaly customized by right clicking on the shortcut and selecting
    Properties from the menu. Highly recommended customizations are:

    * in Options tab enable QuickEdit mode
    * in Font tab change font to Consolas and size to 16
    * in Layout tab increase Screen buffer size Height from 300 to at least 3000

    The loading of the correct environment when shortcut is double clicked is possible via
    previously set ``PYMOTE_ENV`` environment variable which points to the environment location.

..
    **For linux**
    
    In ``~/.profile`` or (if exists) ``~/.bash_profile`` file append line::

        export PYMOTE_ENV="/path/to/pymote_env"

    and restart terminal.
    
    Add shortcut...


Pymote can also be started by starting IPython directly and using dedicated ``pymote`` profile::

    (pymote_env)> ipython --profile=pymote

.. note::

    Pymote profile files should be present inside 
    ``pymote_env/.ipython/profile_pymote/ipython_config.py``
    or ``~/.ipython/profile_pymote/ipython_config.py`` file created during Pymote installation.


Simulation GUI
--------------
Pymote features simulation GUI which can be started as standalone application using 
``pymote-simgui`` (in Windows ``pymote-simgui.exe``). 

.. note::

    If pymote is installed in virtual environment then `pymote-simgui` starts inside this 
    environment. When network pickle is opened in simulator all algorithms this network is 
    referencing must be importable from virtual environment. The easy and proper way to 
    ensure that the algorithms are importable is to use bootstrap algorithms package that can be 
    found [here](https://github.com/darbula/pymote-algorithms-bootstrap) and follow the
    instructions found there.

The other, convenient way of starting and working with the GUI is from the interactive console by 
running ``simulationgui.py`` like this::

    In [1]: %run path/to/pymote/gui/simulationgui.py

The gui event loop is separated from the console. Simulation window can be accessed by using 
``simgui`` and network in the simulator window by using ``simgui.net`` so all simulation objects 
(network, nodes, messages...) are fully inspectable and usable via console.

.. figure:: _images/pymote_console_gui.png
   :align: center
   
   Pymote console and GUI