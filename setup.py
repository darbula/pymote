from distutils.core import setup
import os

# Compile the list of packages available, because distutils doesn't have
# an easy way to do this.
packages, data_files = [], []
root_dir = os.path.dirname(__file__)
if root_dir != '':
    os.chdir(root_dir)
pymote_dir = 'pymote'

def fullsplit(path, result=None):
    """
    Split a pathname into components (the opposite of os.path.join) in a
    platform-neutral way.
    """
    if result is None:
        result = []
    head, tail = os.path.split(path)
    if head == '':
        return [tail] + result
    if head == path:
        return result
    return fullsplit(head, [tail] + result)
    
for dirpath, dirnames, filenames in os.walk(pymote_dir):
    # Ignore PEP 3147 cache dirs and those whose names start with '.'
    for i, dirname in enumerate(dirnames):
        if dirname.startswith('.') or dirname == '__pycache__':
            del dirnames[i]
    if '__init__.py' in filenames:
        packages.append('.'.join(fullsplit(dirpath)))
    elif filenames:
        data_files.append([dirpath, [os.path.join(dirpath, f) for f in filenames]])

setup(
    name = "Pymote",
    version = '0.1',
    url = 'https://github.com/darbula/pymote',
    author = 'Damir Arbula',
    author_email = 'damir.arbula@gmail.com',
    description = 'A high-level Python library for simulation of distributed algorithms.',
    download_url = '',
    packages = packages,
    data_files = data_files,
#    install_requires=[
#        'networkx',
#        'numpy',
#        'scipy',
#        'pypng',
#        'ipython',
#        'matplotlib',
#    ],
#    scripts = ['pymote/bin/pymote.bat'],
#    long_description=open(os.path.join(os.path.dirname(__file__), 'README.rst')).read(),
#    license='BSD License',
#    platforms=['OS Independent'],
#    classifiers=CLASSIFIERS,
#    tests_require=[],
#    include_package_data=True,
#    zip_safe = False,
#    test_suite = 'runtests.main',
)