from __future__ import division

import unittest
from shutil import rmtree

import numpy as np

import fluidsim
import fluiddyn.util.mpi as mpi
from fluiddyn.io import stdout_redirected


def run_mini_simul(key_solver, HAS_TO_SAVE=False, FORCING=False):

    Simul = fluidsim.import_simul_class_from_key(key_solver)

    params = Simul.create_default_params()

    params.short_name_type_run = 'test'

    nh = 16
    params.oper.nx = nh
    params.oper.ny = nh
    Lh = 6.
    params.oper.Lx = Lh
    params.oper.Ly = Lh

    params.oper.coef_dealiasing = 1.  # 2. / 3
    params.nu_8 = 2.

    try:
        params.f = 1.
        params.c2 = 200.
    except AttributeError:
        pass

    params.time_stepping.t_end = 0.5

    params.init_fields.type = 'dipole'

    if HAS_TO_SAVE:
        params.output.periods_save.spectra = 0.25
        params.output.periods_save.spatial_means = 0.25
        params.output.periods_save.spect_energy_budg = 0.25

    if FORCING:
        params.FORCING = True
        params.forcing.type = 'waves'
        params.forcing.nkmin_forcing = 2
        params.forcing.nkmax_forcing = 4

    params.output.HAS_TO_SAVE = HAS_TO_SAVE

    with stdout_redirected():
        sim = Simul(params)
        sim.time_stepping.start()

    if HAS_TO_SAVE:
        sim.output.spatial_means.load()

    return sim


class TestSolver(unittest.TestCase):
    solver = 'NS2D'
    options = {'HAS_TO_SAVE': False, 'FORCING': False}
    zero = 1e-15

    @classmethod
    def setUpClass(cls):
        cls.sim = run_mini_simul(cls.solver, **cls.options)

    @classmethod
    def tearDownClass(cls):
        if mpi.rank == 0:
            rmtree(cls.sim.output.path_run)

    def assertZero(self, value, places=None):
        if places is None:
            places = -int(np.log10(self.zero))

        self.assertAlmostEqual(value, 0, places=places)
        if places < 7 and mpi.rank == 0:
            from warnings import warn
            warn('Machine zero level too high. Value to be asserted as zero' +
                 '= {} : {}'.format(value, self.id()), UserWarning)

    def test_energy_conservation(self):
        """Verify that the energy growth rate due to nonlinear tendencies
        (advection term) must be zero.

        """
        self.sim.params.FORCING = False
        tendencies_fft = self.sim.tendencies_nonlin()
        state_fft = self.sim.state.state_fft
        Frot_fft = tendencies_fft.get_var('rot_fft')
        rot_fft = state_fft.get_var('rot_fft')

        oper = self.sim.oper
        Frot_fft = tendencies_fft.get_var('rot_fft')
        T_rot = (Frot_fft.conj() * rot_fft +
                 Frot_fft * rot_fft.conj()).real / 2.
        sum_T = oper.sum_wavenumbers(T_rot)
        sum_Tabs = oper.sum_wavenumbers(abs(T_rot))
        self.assertZero(sum_T)
        self.assertZero(sum_Tabs)


class TestSW1L(TestSolver):
    solver = 'SW1L'
    options = {'HAS_TO_SAVE': True, 'FORCING': False}
    zero = 1e-7

    def _get_tendencies(self):
        self.sim.params.FORCING = False
        tendencies_fft = self.sim.tendencies_nonlin()

        Fx_fft = tendencies_fft.get_var('ux_fft')
        Fy_fft = tendencies_fft.get_var('uy_fft')
        Feta_fft = tendencies_fft.get_var('eta_fft')

        return Fx_fft, Fy_fft, Feta_fft

    def test_energy_conservation(self):
        """Verify that the energy growth rate due to nonlinear tendencies
        (advection term) must be zero.

        """
        Fx_fft, Fy_fft, Feta_fft = self._get_tendencies()
        state_phys = self.sim.state.state_phys
        ux = state_phys.get_var('ux')
        uy = state_phys.get_var('uy')
        eta = state_phys.get_var('eta')

        oper = self.sim.oper
        Fx = oper.ifft2(Fx_fft)
        Fy = oper.ifft2(Fy_fft)
        Feta = oper.ifft2(Feta_fft)
        A = (Feta * (ux ** 2 + uy ** 2) / 2 +
             (1 + eta) * (ux * Fx + uy * Fy) +
             self.sim.params.c2 * eta * Feta)

        A_fft = oper.fft2(A)
        if mpi.rank == 0:
            self.assertZero(A_fft[0, 0])


class TestSW1LExactLin(TestSW1L):
    solver = 'SW1L.exactlin'
    options = {'HAS_TO_SAVE': True, 'FORCING': False}

    def _get_tendencies(self):
        self.sim.params.FORCING = False
        tendencies_fft = self.sim.tendencies_nonlin()

        Fap_fft = tendencies_fft.get_var('ap_fft')
        Fam_fft = tendencies_fft.get_var('am_fft')
        try:
            Fq_fft = tendencies_fft.get_var('q_fft')
        except ValueError:
            Fq_fft = self.sim.oper.constant_arrayK(value=0.j)

        return self.sim.oper.uxuyetafft_from_qapamfft(Fq_fft, Fap_fft, Fam_fft)


class TestSW1LOnlyWaves(TestSW1LExactLin):
    solver = 'SW1L.onlywaves'
    options = {'HAS_TO_SAVE': True, 'FORCING': False}


class TestSW1LModify(TestSW1L):
    solver = 'SW1L.modified'
    options = {'HAS_TO_SAVE': True, 'FORCING': False}
    zero = 1e-7

    def test_energy_conservation(self):
        """Verify that the energy growth rate due to nonlinear tendencies
        (advection term) must be zero.

        """
        Fx_fft, Fy_fft, Feta_fft = self._get_tendencies()
        state_phys = self.sim.state.state_phys
        ux = state_phys.get_var('ux')
        uy = state_phys.get_var('uy')
        eta = state_phys.get_var('eta')

        oper = self.sim.oper
        Fx = oper.ifft2(Fx_fft)
        Fy = oper.ifft2(Fy_fft)
        Feta = oper.ifft2(Feta_fft)
        A = ((ux * Fx + uy * Fy) + self.sim.params.c2 * eta * Feta)

        A_fft = oper.fft2(A)
        if mpi.rank == 0:
            self.assertZero(A_fft[0, 0])

    def test_energy_conservation_fft(self):
        """Verify that the quadratic energy growth rate due to nonlinear
        tendencies (advection term) must be zero in the spectral plane.

        """
        Fx_fft, Fy_fft, Feta_fft = self._get_tendencies()
        state = self.sim.state
        ux_fft = state('ux_fft')
        uy_fft = state('uy_fft')
        eta_fft = state('eta_fft')

        oper = self.sim.oper
        T_ux = (ux_fft.conj() * Fx_fft).real
        T_uy = (uy_fft.conj() * Fy_fft).real
        T_eta = (eta_fft.conj() * Feta_fft).real
        T_tot = T_ux + T_uy + T_eta
        sum_T = oper.sum_wavenumbers(T_tot)
        sum_Tabs = oper.sum_wavenumbers(abs(T_tot))
        try:
            self.assertZero(sum_T)
        except AssertionError:
            self.assertZero(sum_T, 4)
        try:
            self.assertZero(sum_Tabs)
        except AssertionError:
            self.assertZero(sum_Tabs, 4)


class TestSW1LExmod(TestSW1LModify):
    solver = 'SW1L.exactlin.modified'
    options = {'HAS_TO_SAVE': True, 'FORCING': False}
    zero = 1e-7

    def _get_tendencies(self):
        self.sim.params.FORCING = False
        tendencies_fft = self.sim.tendencies_nonlin()

        Fq_fft = tendencies_fft.get_var('q_fft')
        Fap_fft = tendencies_fft.get_var('ap_fft')
        Fam_fft = tendencies_fft.get_var('am_fft')

        return self.sim.oper.uxuyetafft_from_qapamfft(Fq_fft, Fap_fft, Fam_fft)


if __name__ == '__main__':
    unittest.main()
