import os, sys
import distribute_setup
distribute_setup.use_setuptools()
from setuptools import setup, find_packages


root_dir = os.path.dirname(__file__)
if root_dir != '':
    os.chdir(root_dir)
pymote_dir = 'pymote'

import shutil
#TODO: install bat on windows
#if sys.platform="win32":
#    shutil.copy(os.path.join('pymote','conf','ipython','ipython_config.py'),os.path.join(ipythondir, 'profile_pymote'))

# transfer profile_pymote for ipython into IPYTHONDIR
try:
    import IPython
    ipythondir = IPython.utils.path.get_ipython_dir()
except ImportError, AttributeError:
    print("Pymote IPython configuration not installed. Install latest IPython and then copy the conf/ipython/profile_pymote/ipython_config.py manually to IPython config dir.")
else:
    shutil.copy(os.path.join('pymote','conf','ipython','ipython_config.py'),os.path.join(ipythondir, 'profile_pymote'))
    


setup(
    name = "Pymote",
    version = '0.1.1',
    url = 'https://github.com/darbula/pymote',
    author = 'Damir Arbula',
    author_email = 'damir.arbula@gmail.com',
    description = 'A high-level Python library for simulation of distributed algorithms.',
    download_url = '',
    packages = find_packages(),
    package_data = {
        '': ['*.bat'],
    },
    exclude_package_data = { '': ['README.rst'] },
    install_requires=[
        'networkx',
        'numpy',
        'scipy',
        'pypng',
        'ipython',
        'matplotlib',
        'PySide',
    ],
    long_description=open(os.path.join(os.path.dirname(__file__), 'README.rst')).read(),

    #TODO: make algorithms extensible http://pythonhosted.org/distribute/setuptools.html#dynamic-discovery-of-services-and-plugins
    entry_points = {
        'pymote.algorithms': [],
        #TODO: make scripts
        #'console_scripts': [
        #    'pymote = pymote.bin:pymote',
        #],
        #'gui_scripts': [
        #    'pymote_simgui = pymote.gui.simulationgui',
        #]
    },

#    scripts = ['pymote/bin/pymote.bat'],
#    license='BSD License',
#    platforms=['OS Independent'],
#    classifiers=CLASSIFIERS,
#    tests_require=[],
#    include_package_data=True,
#    zip_safe = False,
#    test_suite = 'runtests.main',
)