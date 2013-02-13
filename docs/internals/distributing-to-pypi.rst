Distributing to PyPI
====================

Windows
-------

Create ``C:\Users\<user>\.pypirc`` file::

    [distutils]
    index-servers =
        pypi

    [pypi]
    repository: http://pypi.python.org/pypi
    username: <username>
    password: <password>

    [server-login]
    repository: http://pypi.python.org/pypi
    username: <username>
    password: <password>

Issue these commands::

    > setx HOME C:\Users\<user>
    > python setup.py sdist upload register
