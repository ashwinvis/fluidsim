========
FluidSim
========

|release| |docs| |coverage| |travis|

.. |release| image:: https://img.shields.io/pypi/v/fluidsim.svg
   :target: https://pypi.python.org/pypi/fluidsim/
   :alt: Latest version

.. |docs| image:: https://readthedocs.org/projects/fluidsim/badge/?version=latest
   :target: http://fluidsim.readthedocs.org
   :alt: Documentation status

.. |coverage| image:: https://codecov.io/bb/fluiddyn/fluidsim/branch/default/graph/badge.svg
   :target: https://codecov.io/bb/fluiddyn/fluidsim/branch/default/
   :alt: Code coverage

.. |travis| image:: https://travis-ci.org/fluiddyn/fluidsim.svg?branch=master
    :target: https://travis-ci.org/fluiddyn/fluidsim

FluidSim is the numerically oriented package of the `FluidDyn project
<http://fluiddyn.readthedocs.org>`__.  The project is still in a
testing stage so it is still pretty unstable and many of its planned
features have not yet been implemented.

It has first been developed by `Pierre Augier
<http://www.legi.grenoble-inp.fr/people/Pierre.Augier/>`_ (CNRS
researcher at `LEGI <http://www.legi.grenoble-inp.fr>`_, Grenoble) at
KTH (Stockholm) as a numerical code to solve fluid equations in a
periodic two-dimensional space with pseudo-spectral methods.

*Key words and ambitions*: fluid dynamics research with Python (2.7 or
>= 3.3); modular, object-oriented, collaborative, tested and
documented, free and open-source software.

License
-------

FluidDyn is distributed under the CeCILL_ License, a GPL compatible
french license.

.. _CeCILL: http://www.cecill.info/index.en.html

Installation
------------

You can get the source code from `Bitbucket
<https://bitbucket.org/fluiddyn/fluidsim>`__ or from `the Python
Package Index <https://pypi.python.org/pypi/fluidsim/>`__.

The development mode is often useful. From the root directory::

  python setup.py develop

Tests
-----

From the root directory::

  make tests
  make tests_mpi

Or, from the root directory or from any of the "test" directories::

  python -m unittest discover
