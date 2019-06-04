from aguaclara.core.units import unit_registry as u
import aguaclara.core.physchem as pc
import aguaclara.core.constants as con
import aguaclara.core.materials as mat
import aguaclara.core.pipes as pipe
import aguaclara.core.head_loss as hl

import numpy as np
import math

L_MAX = 2.2 * u.m

# Angle of the sloped walls of the entrance tank hoppers
ENT_TANK_SLOPE_ANGLE = 45 * u.deg

# Extra space around the float (increase in effective diameter) to
# ensure that float has free travel
FLOAT_S = 5 * u.cm
HOPPER_PEAK_W = 3 * u.cm
MOD_ND = 0.5 * u.inch

# Distance from the front wall to the pipe stubs in the hopper drains so
# that an operator can easily reach them.
WALL_DRAIN_DIST_MAX = 40 * u.cm
MOD_SPACER_ND = 0.75 * u.inch

# Thickness of the PVC disk used as the float for the chemical dose
# controller lever arm.
FLOAT_THICKNESS = 5 * u.cm
LAMINA_PIPE_EDGE_S = 5 * u.cm

# Nom diam of the pipes that are embedded in the entrance tank slope
# to support the plate settler module
PLATE_SUPPORT_ND = 3 * u.inch


# Increased to get better mixing (10/10/2015 by Monroe)
RAPID_MIX_EDR = 3 * u.W / u.kg

RAPID_MIX_PLATE_RESTRAINER_ND = 0.5 * u.inch

FLOAT_ND = 8*u.inch

# Minimum pipe size to handle grit and to ensure that the pipe can be
# easily unclogged
DRAIN_MIN_ND = 3*u.inch

DRAIN_ND = 3*u.inch  # This is constant for now

REMOVABLE_WALL_THICKNESS = 5*u.cm

# Parameters are arbitrary - need to be calculated
REMOVABLE_WALL_SUPPORT_H = 4 * u.cm

REMOVABLE_WALL_SUPPORT_THICKNESS = 5*u.cm

HOPPER_LEDGE_THICKNESS = 15*u.cm
WALKWAY_W = 1 * u.m
RAPID_MIX_ORIFICE_PLATE_THICKNESS = 2*u.cm
RAPID_MIX_AIR_RELEASE_ND = 1*u.inch

class EntranceTank: 

    def __init__(self, q,
                    lfom_nd = 2 * u.inch, # May be innacurate, check with Monroe -Oliver L., oal22, 4 Jun '19 
                    floc_chan_w=42 * u.inch,
                    floc_end_depth=2. * u.m,
                    plate_s=2.5 * u.cm,
                    plate_thickness=2 * u.mm,
                    plate_angle = 60 * u.deg,
                    plate_capture_vel = 8 * u.mm / u.s,
                    fab_space=5 * u.cm,
                    temp=20. * u.degC,
                    sdr=41.):
        self.q = q
        self.lfom_nd = lfom_nd
        self.floc_chan_w = floc_chan_w
        self.floc_end_depth = floc_end_depth
        self.plate_s = plate_s
        self.plate_thickness = plate_thickness
        self.plate_angle = plate_angle
        self.plate_capture_vel = plate_capture_vel
        self.fab_space = fab_space
        self.temp = temp
        self.sdr = sdr
    
    @property
    def drain_od(self):
        """Return the nominal diameter of the entrance tank drain pipe. Depth at the
        end of the flocculator is used for headloss and length calculation inputs in
        the diam_pipe calculation.
        """
        nu = pc.viscosity_kinematic(self.temp)
        k_minor = \
            hl.PIPE_ENTRANCE_K_MINOR + hl.PIPE_EXIT_K_MINOR + hl.EL90_K_MINOR
        drain_id = pc.diam_pipe(self.q,
                                self.floc_end_depth,
                                self.floc_end_depth,
                                nu,
                                mat.PVC_PIPE_ROUGH,
                                k_minor)
        drain_nd = pipe.ND_SDR_available(drain_id, self.sdr)
        return pipe.OD(drain_nd)
        
    @property
    def plate_n(self):
        """Return the number of plates in the entrance tank.

        This number minimizes the total length of the plate settler unit.
        """
        num_plates_as_float = \
            np.sqrt(
                (self.q / (
                    self.plate_s * self.floc_chan_w * self.plate_capture_vel *
                    np.sin(self.plate_angle.to(u.rad)).item()
                )).to(u.dimensionless)
            )
        num_plates_as_int = np.ceil(num_plates_as_float)
        return num_plates_as_int # This calculates to be too low. -Oliver

    @property
    def plate_l(self):
        """Return the length of the plates in the entrance tank.
        """
        plate_l = \
            (
                self.q / (
                    self.plate_n * self.floc_chan_w * self.plate_capture_vel *
                    np.cos(self.plate_angle.to(u.rad))
                )
            ) - (self.plate_s * np.tan(self.plate_angle.to(u.rad)))
        return plate_l

    @property
    def l(self):
        """Return the length of the entrance tank.
        """
        plate_array_thickness = (self.plate_thickness * self.plate_n) + (self.plate_s * (self.plate_n - 1))
        l = self.drain_od + (self.fab_space * 2) + (plate_array_thickness * np.cos(((90 * u.deg) - self.plate_angle).to(u.rad))) + (self.plate_l * np.cos(self.plate_angle.to(u.rad))) + (self.lfom_nd * 2)
        return l
        
        