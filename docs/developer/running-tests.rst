Running tests
=============
To execute tests install nose ``pip install nose`` and run it inside pymote 
directory. All tests should be found recursively scanning directories.
To run all tests run this from root pymote directory::

    $ nosetests -v

To run selected test module::

    $ nosetests -v pymote.tests.test_algorithm