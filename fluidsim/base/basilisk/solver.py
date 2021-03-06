
from __future__ import print_function

from fluidsim.base.solvers.base import SimulBase
from fluidsim.base.solvers.info_base import InfoSolverBase

import basilisk.stream as basilisk


class InfoSolverBasilisk(InfoSolverBase):

    def _init_root(self):

        super(InfoSolverBasilisk, self)._init_root()

        mod = 'fluidsim.base.basilisk'

        self.module_name = mod + '.solver'
        self.class_name = 'SimulBasilisk'
        self.short_name = 'basil'

        classes = self.classes

        classes.State.module_name = mod + '.state'
        classes.State.class_name = 'StateBasilisk'

        classes.TimeStepping.module_name = mod + '.time_stepping'
        classes.TimeStepping.class_name = 'TimeSteppingBasilisk'

        classes.Operators.module_name = mod + '.operators'
        classes.Operators.class_name = 'OperatorsBasilisk2D'

        classes.Output.module_name = mod + '.output'
        classes.Output.class_name = 'OutputBasilisk'


class SimulBasilisk(SimulBase):
    InfoSolver = InfoSolverBasilisk

    def __init__(self, params):
        bas = self.basilisk = basilisk
        super(SimulBasilisk, self).__init__(params)

        def init(i, t):
            bas.omega.f = bas.noise

        bas.event(init, t=0.)

Simul = SimulBasilisk

if __name__ == "__main__":

    import matplotlib.pyplot as plt

    params = Simul.create_default_params()

    params.short_name_type_run = 'test'

    params.oper.nx = 128

    params.time_stepping.deltat0 = 2.4
    params.output.periods_print.print_stdout = 1e-15

    sim = Simul(params)
    sim.time_stepping.start()

    sim.output.print_stdout.plot_energy()
    plt.show()
