"""Simple text output (:mod:`fluidsim.solvers.ns2d.strat.output.print_stdout`)
==============================================================================

.. autoclass:: PrintStdOutNS2DStrat
   :members:
   :private-members:

"""

from __future__ import print_function, division

import numpy as np

from fluidsim.base.output.print_stdout import PrintStdOutBase

from fluiddyn.util import mpi


class PrintStdOutNS2DStrat(PrintStdOutBase):
    """Simple text output.

    Used to print in both the stdout and the stdout.txt file, and also
    to print simple info on the current state of the simulation.

    """

    def _make_str_info(self):
        to_print = super(PrintStdOutNS2DStrat, self)._make_str_info()

        energyK, energyA, energyK_ux = self.output.compute_energies()
        energy = energyK + energyA
        if mpi.rank == 0:
            to_print += (
                '              energyK = {:9.3e}\n'
                '              energyA = {:9.3e}\n'
                '              energy  = {:9.3e} ; Delta energy = {:+9.3e}\n'
                ''.format(energyK, energyA, energy, energy-self.energy_temp))

            duration_left = self._evaluate_duration_left()
            if duration_left is not None:
                to_print += (
                    '              estimated remaining duration = {:9.3g} s'
                    ''.format(duration_left))

        self.energy_temp = energy
        return to_print

    def load(self):
        dico_results = {'name_solver': self.output.name_solver}
        file_means = open(self.output.path_run+'/stdout.txt')
        lines = file_means.readlines()

        lines_t = []
        lines_E = []
        lines_EK = []
        lines_EA = []
        for il, line in enumerate(lines):
            if line.startswith('it ='):
                lines_t.append(line)
            if line.startswith('              energy  ='):
                lines_E.append(line)
            if line.startswith('              energyK ='):
                lines_EK.append(line)
            if line.startswith('              energyA ='):
                lines_EA.append(line)

        nt = len(lines_t)
        if nt > 1:
            nt -= 1

        it = np.zeros(nt, dtype=np.int)
        t = np.zeros(nt)
        deltat = np.zeros(nt)

        E = np.zeros(nt)
        deltaE = np.zeros(nt)
        EK = np.zeros(nt)
        EA = np.zeros(nt)

        for il in xrange(nt):
            line = lines_t[il]
            words = line.split()
            it[il] = int(words[2])
            t[il] = float(words[6])
            deltat[il] = float(words[10])

            line = lines_E[il]
            words = line.split()
            E[il] = float(words[2])
            deltaE[il] = float(words[7])

            line = lines_EK[il]
            words = line.split()
            EK[il] = float(words[2])

            line = lines_EA[il]
            words = line.split()
            EA[il] = float(words[2])

        dico_results['it'] = it
        dico_results['t'] = t
        dico_results['deltat'] = deltat
        dico_results['E'] = E
        dico_results['deltaE'] = deltaE
        dico_results['EK'] = EK
        dico_results['EA'] = EA

        return dico_results

    def plot(self):
        dico_results = self.load()

        t = dico_results['t']
        deltat = dico_results['deltat']
        E = dico_results['E']
        #  deltaE = dico_results['deltaE']
        EK = dico_results['EK']
        EA = dico_results['EA']

        x_left_axe = 0.12
        z_bottom_axe = 0.55
        width_axe = 0.85
        height_axe = 0.4
        size_axe = [x_left_axe, z_bottom_axe,
                    width_axe, height_axe]
        fig, ax1 = self.output.figure_axe(size_axe=size_axe)
        ax1.set_xlabel('t')
        ax1.set_ylabel('deltat(t)')

        ax1.set_title('info stdout, solver '+self.output.name_solver +
                      ', nh = {0:5d}'.format(self.nx))
        ax1.plot(t, deltat, 'k', linewidth=2)

        size_axe[1] = 0.08
        ax2 = fig.add_axes(size_axe)
        ax2.set_xlabel('t')
        ax2.set_ylabel('E(t), deltaE(t)')
        ax2.plot(t, E, 'k', linewidth=2, label='$E$')
        # ax2.plot(t, deltaE, 'b', linewidth=2)
        ax2.plot(t, EK, 'r', linewidth=2, label='$E_K$')
        ax2.plot(t, EA, 'g', linewidth=2, label='$E_A$')
        ax2.legend()
        ax2.grid(True)
