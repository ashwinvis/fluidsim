"""Lorenz model solver (:mod:`fluidsim.solvers.models0d.lorenz.solver`)
=======================================================================

This module provides classes to solve the Lorenz model.

.. autoclass:: InfoSolverLorenz
   :members:
   :private-members:

.. autoclass:: Simul
   :members:
   :private-members:

.. autoclass:: StateLorenz
   :members:
   :private-members:

"""

from __future__ import division

from math import sqrt

from fluidsim.base.setofvariables import SetOfVariables

from fluidsim.base.solvers.base import InfoSolverBase, SimulBase
from fluidsim.base.state import StateBase


class StateLorenz(StateBase):

    @staticmethod
    def _complete_info_solver(info_solver):
        """Complete the `info_solver` container (static method)."""
        keys = ['X', 'Y', 'Z']
        info_solver.classes.State._set_attribs({
            'keys_state_phys': keys,
            'keys_computable': [],
            'keys_phys_needed': keys,
            'keys_linear_eigenmodes': keys})


class InfoSolverLorenz(InfoSolverBase):
    """Contain the information on the solver predaprey."""
    def _init_root(self):
        super(InfoSolverLorenz, self)._init_root()

        package = 'fluidsim.solvers.models0d.lorenz'
        self.module_name = package + '.solver'
        self.class_name = 'Simul'
        self.short_name = 'lorenz'

        classes = self.classes

        classes.State.module_name = package + '.solver'
        classes.State.class_name = 'StateLorenz'

        classes.Output.module_name = package + '.output'
        classes.Output.class_name = 'Output'


class Simul(SimulBase):
    """Solve the Lotka-Volterra equations.

    """
    InfoSolver = InfoSolverLorenz

    @staticmethod
    def _complete_params_with_default(params):
        """Complete the `params` container (static method)."""
        SimulBase._complete_params_with_default(params)
        attribs = {'sigma': 10., 'beta': 8./3, 'rho': 28.}
        params._set_attribs(attribs)

    def __init__(self, *args, **kargs):
        super(Simul, self).__init__(*args, **kargs)
        p = self.params
        Zs = self.Zs0 = self.Zs1 = p.rho - 1
        self.Xs0 = self.Ys0 = sqrt(p.beta * Zs)
        self.Xs1 = self.Ys1 = -self.Xs0

    def tendencies_nonlin(self, state=None):
        r"""Compute the nonlinear tendencies.

        Parameters
        ----------

        state : :class:`fluidsim.base.setofvariables.SetOfVariables`
            optional

            Array containing the state.  If `state is not None`, the variables
            are computed from it, otherwise, they are taken from the global
            state of the simulation, `self.state`.

            These two possibilities are used during the Runge-Kutta
            time-stepping.

        Returns
        -------

        tendencies : :class:`fluidsim.base.setofvariables.SetOfVariables`
            An array containing the tendencies for the variables.

        Notes
        -----

        The Lotka-Volterra equations can be written

        .. math::
           \dot X = \sigma (Y - X),
           \dot Y = \rho X - Y - XZ.
           \dot Z = X Y - \beta Z.

        """
        p = self.params

        if state is None:
            state = self.state.state_phys

        X = state.get_var('X')
        Y = state.get_var('Y')
        Z = state.get_var('Z')

        tendencies = SetOfVariables(like=self.state.state_phys)
        tendencies.set_var('X', p.sigma * (Y - X))
        tendencies.set_var('Y', p.rho * X - Y - X * Z)
        tendencies.set_var('Z', X*Y - p.beta * Z)

        if self.params.FORCING:
            tendencies += self.forcing.get_forcing()

        return tendencies


if __name__ == "__main__":
    import fluiddyn as fld

    params = Simul.create_default_params()

    params.time_stepping.deltat0 = 0.02
    params.time_stepping.t_end = 20

    params.output.periods_print.print_stdout = 0.01

    sim = Simul(params)

    sim.state.state_phys.set_var('X', sim.Xs0 + 2.)
    sim.state.state_phys.set_var('Y', sim.Ys0)
    sim.state.state_phys.set_var('Z', sim.Zs0)

    # sim.output.phys_fields.plot()
    sim.time_stepping.start()
    fld.show()
