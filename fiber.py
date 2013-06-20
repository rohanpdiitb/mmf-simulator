"""
This module defines and implements the models for different fiber types.
"""
import numpy
from numpy import sqrt
import abc
import types
from math import factorial
from scipy.special import gamma

class ModeFamily(object):
    """
    This is an abstract class that represents the modes of the
    fiber. This class is subclassed to obtain various mode patterns.
    """
    __metaclass__ = abc.ABCMeta

    mode_attributes = ['theta', 'offset_x', 'offset_y']
    def __init__(self, w, XX, YY, **kwargs):
        """
        Defines the mode family for a fiber or waveguide. A summary of
        the parameters follows:

        `XX`, `YY`: meshgrid inputs
        `w`: mode radius
        `offset_x`, `offset_y`: Evaluate the parameters off-center
        `theta`: Rotates the mode pattern by this angle
        """
        for i in self.mode_attributes:
            exec("self.%s = 0.0" % i)
            if i in kwargs.keys():
                exec("self.%s = %f" % (i, float(kwargs[i])))

            # Method functions to return paramters
            exec("f = lambda self : self.%s" % i)
            exec("f.__doc__ = \"Returns %s for this mode family\"" % (i))
            exec("self.get_%s = types.MethodType(f, self)" % i)
        self.XX = XX
        self.YY = YY
        self.w = w

    @abc.abstractmethod
    def get_mode_pattern(self, p, q):
        """
        Return the mode pattern for the mesh grid that the class was
        initialized with.
        """
        raise NotImplemented        

class GHModes(ModeFamily):
    """
    This class represents the Hermite-Gauss modes for a fiber. The
    definition of these parameters can be found in *Principal Modes in
    Graded-Index Multimode Fiber in Presence of Spatial- and
    Polarization-Mode Coupling* by Shemirani et al., IEEE/OSA Journal
    of Lightwave Technology, May 2009.

    An examples:
    >>> NA = 0.19
    >>> wavelength = 1.55e-6;
    >>> a = 31.25e-6/2;
    >>> k0 = 2 * numpy.pi / wavelength
    >>> n0 = 1.444;
    >>> Csk0 = 0.0878 * pow(n0, 3)
    >>> delta = 8000;
    >>> n_core = n0;
    >>> DELTA = 0.5 * pow((NA / n0), 2);
    >>> sqrt = numpy.sqrt
    >>> w = sqrt(sqrt(2) * a / (k0 * n0 * sqrt(DELTA)));
    >>> EXTENTS = 30e-6
    >>> STEP = 0.5e-6
    >>> x = numpy.arange(-EXTENTS, EXTENTS, STEP)
    >>> y = numpy.arange(-EXTENTS, EXTENTS, STEP)
    >>> [XX, YY] = numpy.meshgrid(x, y)
    >>> gh_modes = GHModes(w, XX, YY, theta = numpy.pi / 4)
    >>> # gh_modes.plot_mode_pattern(2, 2)
    >>> mode_pattern_1 = gh_modes.get_mode_pattern(0, 0)
    >>> mode_pattern_2 = gh_modes.get_mode_pattern(1, 1)
    >>> print "%.2f" % utils.overlap(mode_pattern_1, mode_pattern_1)
    1.00
    >>> print "%.2f" % utils.overlap(mode_pattern_2, mode_pattern_2)
    1.00
    >>> print "%.2f" % utils.overlap(mode_pattern_1, mode_pattern_2)
    0.00
    """
    def get_mode_pattern(self, p, q):
        """
        Return the Hermite-Gauss mode pattern for the mesh grid that
        the class was initialized with.
        """
        # Initialize the hermite polynomials
        Hp = numpy.polynomial.hermite.Hermite.basis(p)
        Hq = numpy.polynomial.hermite.Hermite.basis(q)

        # Convenience assignments
        XX = self.XX
        YY = self.YY
        theta = self.theta
        pi = numpy.pi
        exp = numpy.exp
        w = self.w
        cos = numpy.cos
        sin = numpy.sin

        # Radial distances, with offsets
        R2 = numpy.square(XX - self.offset_x) + numpy.square(YY - self.offset_y)

        # Split the multiplication into steps
        P1 = sqrt(2 / pi) / w / sqrt(pow(2.0, p + q) * float(factorial(p)) * float(factorial(q)))
        P1 = 1.0
        P2 = P1 * Hp(sqrt(2.0) * (XX * cos(theta) + YY * sin(theta)) / w)
        P3 = numpy.multiply(P2, Hq(sqrt(2.0) * (XX * -sin(theta) + YY * cos(theta)) / w))
        P4 = numpy.multiply(P3, exp(-R2 / w / w))
        P5 = P4 / sqrt(numpy.sum(numpy.square(P4)))
        return P5

    def plot_mode_pattern(self, p, q):
        """
        Plot the `p`, `q` mode pattern.
        """
        try:
            import matplotlib
        except ImportError:
            print "Can't plot, because matplotlib seems missing"
            return
        import matplotlib.patches as patches
        import matplotlib.pyplot as pyplot

        pattern = self.get_mode_pattern(p, q)
        pattern = pattern / numpy.max(pattern)
        pyplot.imshow(numpy.abs(pattern), interpolation = 'bilinear', cmap = matplotlib.cm.spectral)
        pyplot.grid(True)
        pyplot.show()

class Fiber(object):
    """
    This object represents an abstract notion of a fiber. It is intended
    to be subclassed to implement a fiber model, based on various
    characteristics.
    """
    __metaclass__ = abc.ABCMeta

    def __init__(self, length = 1000.0, step_length = 0.1, wavelength = 1.55e-6):
        """
        Initialize the fiber with length and step size.
        
        """
        self.length = length
        self.step_length = step_length
        self.current_mode_vector = numpy.matrix([])

        self.transmitter_connected = False
        self.receiver_connected = False

    @abc.abstractmethod
    def connect_transmitter(self):
        """
        Connect a transmit laser array
        """
        raise NotImplemented

    @abc.abstractmethod
    def connect_receiver(self):
        """
        Connect a receiver detector array
        """
        raise NotImplemented

    @abc.abstractmethod
    def populate_modes(self):
        raise NotImplemented

class LargeCoreMMF(Fiber):
    """
    This class represents a conventional (large-core) multimode
    fiber. This uses the model described in *Principal Modes in
    Graded-Index Multimode Fiber in Presence of Spatial- and
    Polarization-Mode Coupling* by Shemirani et al., IEEE/OSA Journal
    of Lightwave Technology, May 2009, and is slightly altered and
    tailored for large-core fibers whose diameters are larger than
    about 30 microns.

    The valid parameters and their default values (in parentheses) are:
    `NA`: numerical aperture (0.19)
    `wavelength`: nominal operating wavelength (1.55e-6)
    `a`: fiber radius (25e-6)
    `n0`: nominal refractive index (1.444)
    `Csk0`: strain optical coefficient (0.0878 * n0^3)
    `delta`: Refractive index gradient parameter (8000)
    `sigma_kappa`: Curvature variance (1.0)
    `sigma_theta`: Angle variance (sqrt(0.36))
    `DELTA`: Index difference between core and cladding (0.5 * (NA / n0)^2)
    `w`: Mode field diameter (sqrt(sqrt(2) * a / (k0 * n0 * sqrt(DELTA))))
    `EXTENTS`: Grid extents (30e-6)
    `STEP`: Grid step  (0.5e-6)

    Example:
    >>> m = LargeCoreMMF()
    >>> len(m.get_admissible_modes())
    55
    """

    fiber_attributes = ["NA", "wavelength", "a", "n0", "Csk0",
        "delta", "DELTA", "sqrt", "w", "EXTENTS", "STEP", "sigma_kappa", "sigma_theta"]

    fiber_internals = ["admissible_modes", "betas"]

    def __init__(self, length = 1000.0, step_length = 0.1, wavelength = 1.55e-6, **kwargs):
        super(LargeCoreMMF, self).__init__(length, step_length, wavelength)

        # Default values
        self.NA = 0.19
        self.wavelength = 1.55e-6;
        self.a = 25e-6;
        self.n0 = 1.444;
        self.Csk0 = 0.0878 * pow(self.n0, 3)
        self.delta = 8000;
        self.n_core = self.n0;
        self.DELTA = 0.5 * pow((self.NA / self.n0), 2);
        self.sigma_kappa = 1.0
        self.sigma_kappa = sqrt(0.36)

        self.k0 = 2 * numpy.pi / wavelength
        self.w = sqrt(sqrt(2) * self.a / (self.k0 * self.n0 * sqrt(self.DELTA)));

        self.EXTENTS = 30e-6
        self.STEP = 0.5e-6

        # Populate values based on kwargs
        for i in self.fiber_attributes:
            if i in kwargs.keys():
                exec("self.%s = %f" % (i, float(kwargs[i])))

            # Method functions to return paramters
            exec("f = lambda self : self.%s" % i)
            exec("f.__doc__ = \"Returns %s for this fiber\"" % (i))
            exec("self.get_%s = types.MethodType(f, self)" % i)

        for i in self.fiber_internals:
            exec("self.%s = None" % (i))

            # Method functions to return paramters
            exec("f = lambda self : self.%s" % i)
            exec("f.__doc__ = \"Returns %s for this fiber\"" % (i))
            exec("self.get_%s = types.MethodType(f, self)" % i)

        self.populate_modes()

    def calculate_beta(self, p, q):
        """
        Calculates the beta values as a function of the wavelength.
        """
        # Refractive index components
        n0x = lambda kappa : (self.delta * self.Csk0 * pow(self.a * kappa, 2) / 2.0 + 2.0 * self.n0) / 2.0
        n0xy = lambda kappa : (n0x(kappa), 2 * self.n0 - n0x(kappa));

        alpha = 2.0
        V = lambda L: 2 * numpy.pi / L * self.a * self.n0 * sqrt(2.0 * self.DELTA)
        b_tilde = lambda L : pow(gamma(1.0 / alpha + 0.5) * (alpha + 2.0) * (p + q + 1) * sqrt(numpy.pi) * pow(V(L), 2.0 / alpha), alpha / (2.0 + alpha))
        return (lambda L, kappa : 1.0 / self.a * sqrt(pow(2 * numpy.pi / L * self.a * n0xy(kappa)[0], 2) - pow(b_tilde(L), 2)),
                lambda L, kappa : 1.0 / self.a * sqrt(pow(2 * numpy.pi / L * self.a * n0xy(kappa)[1], 2) - pow(b_tilde(L), 2)))

    def populate_modes(self):
        # Calculate the admissible mode numbers
        a = self.a
        w = self.w
        MAX = int(numpy.floor((a / w) * (a / w)))
        self.admissible_modes = numpy.concatenate([[(i, j) for i in range(j + 1)] for j in range(MAX + 1)])
        admissible_modes = self.admissible_modes
        M = len(admissible_modes)
        self.betas = [None] * (2*M)

        for i in range(M):
            p, q = admissible_modes[i][0], admissible_modes[i][1]
            (self.betas[i], self.betas[M + i]) = self.calculate_beta(p, q)

    def connect_transmitter(self):
        self.transmitter_connected = True

    def connect_receiver(self):
        self.receiver_connected = True

if __name__ == "__main__":
    import doctest
    import utils
    doctest.testmod()