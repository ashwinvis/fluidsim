from __future__ import print_function

import unittest
from shutil import rmtree

import matplotlib.pyplot as plt

import fluiddyn.util.mpi as mpi
from fluiddyn.io import stdout_redirected
from fluidsim.solvers.test.test_solvers import run_mini_simul


class BaseTestCase(unittest.TestCase):
    """ TestCase classes that want to be parametrized should
        inherit from this class.
    """
    solver = 'sw1l'
    _tag = ''

    @classmethod
    def setUpClass(cls):
        cls.sim = run_mini_simul(cls.solver, HAS_TO_SAVE=True)
        cls.output = cls.sim.output
        cls.module = module = getattr(cls.output, cls._tag)
        try:
            cls.dico = module.compute()
        except AttributeError:
            cls.dico = module.load()

    @classmethod
    def tearDownClass(cls):
        if mpi.rank == 0:
            rmtree(cls.sim.output.path_run)

    def _plot(self):
        """ Test if plot methods work. """
        module = self.module

        tmax = self.sim.params.time_stepping.t_end
        with stdout_redirected():
            try:
                if hasattr(self.sim.params.output.periods_save, self._tag):
                    delta_t = getattr(
                        self.sim.params.output.periods_save, self._tag)
                else:
                    raise TypeError
                module.plot(tmin=0, tmax=tmax, delta_t=delta_t)
            except TypeError:
                module.plot()

            plt.clf()
            plt.close('all')

    def _online_plot(self, *args):
        module = self.module
        if mpi.rank == 0:
            module.init_online_plot()
            module._online_plot(*args)
            plt.clf()
            plt.close('all')
