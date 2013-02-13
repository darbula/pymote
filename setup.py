import os, sys
import distribute_setup
distribute_setup.use_setuptools()
from setuptools import setup, find_packages

# transfer profile_pymote for ipython into IPYTHONDIR
import sys
if 'install' in sys.argv:
    import shutil
    try:
        import IPython
        ipythondir = IPython.utils.path.get_ipython_dir()
    except ImportError, AttributeError:
        print("Pymote IPython configuration not installed. Install latest IPython and then copy the conf/ipython/profile_pymote/ipython_config.py manually to IPython config dir.")
    else:
        profiledir = os.path.join(ipythondir, 'profile_pymote')
        if not os.path.exists(ipythondir):
            os.makedirs(ipythondir)
        if not os.path.exists(profiledir):
            os.makedirs(profiledir)
        print ("copying ipython_config.py to "+profiledir)
        shutil.copy(os.path.join('pymote','conf','ipython','ipython_config.py'),profiledir)
    

setup(
    name = "Pymote",
    version = '0.1.1',
    url = 'https://github.com/darbula/pymote',
    author = 'Damir Arbula',
    author_email = 'damir.arbula@gmail.com',
    description = 'A high-level Python library for simulation of distributed algorithms.',
    download_url = '',
    packages = find_packages(),
    #package_data = {
    #    '': ['*.bat'],
    #},
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
        'console_scripts': [
            'ipymote = pymote.bin.ipymote:start_ipymote',
        ],
        'gui_scripts': [
            'pymote-simgui = pymote.gui.simulationgui:main',
        ]
    },

#    license='BSD License',
#    platforms=['OS Independent'],
#    classifiers=CLASSIFIERS,
#    tests_require=[],
#    include_package_data=True,
#    zip_safe = False,
#    test_suite = 'runtests.main',
)