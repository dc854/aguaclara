import aguaclara.core.constants as con
import aguaclara.core.head_loss as hl
import aguaclara.core.materials as mat
import aguaclara.core.physchem as pc
import aguaclara.core.pipes as pipe
from aguaclara.core.units import u
import aguaclara.core.utility as ut

from aguaclara.design.component import Component
from aguaclara.design.pipeline import Pipe

import numpy as np

class Filter(Component):

    def __init__(self, **kwargs):
        self.backwash_vel = 11 * u.mm/u.s
        self.layer_n = 6
        self.layer_h = 20 * u.cm
        self.sand_density = 2650 * u.kg/u.m**3
        self.filter_hl_max = 80 * u.cm 
        self.siphon_vent_t = 15* u.s
        self.sand_diam = 0.5 * u.mm
        self.porosity = 0.4
        self.branch_s = 10 * u.cm
        self.trunk_max_size = 8 * u.inch
        self.backwash_orifice_hl = 15 * u.cm
        self.trunk_spec = 'sdr26'
        self.branch_spec = 'sdr26'
        self.q_ratio = 0.85
        self.branch_size = 1 * u.inch
        self.branch_size_backwash = 1.5 * u.inch
        self.temp_min = 10.0 * u.degC
        self.temp_max = 30.0 * u.degC
        self.ratio_qp = 0.85
        self.trunk_size = 6*u.inch
        self.trunk_spec = 'sdr26'
        self.trunk_length = 6 * u.m
        self.filter_v = 11*u.mm/u.s/6
        self.sand_d = 0.5 * u.mm 
        self.sand_porosity = 0.4
        self.orifice_filter_hl = 0 * u.cm
        
        self._set_trunk_pipe()
        super().__init__(**kwargs)

    @property
    def vel(self):
        return self.backwash_vel / self.layer_n

    # Temporary functions, delete all ergun functions when hannah merges 
    # her physchem changes
    def Re_Ergun(self, v_a, D_Sand, Temperature, Porosity):
        return (v_a*D_Sand/(pc.viscosity_kinematic(Temperature)*(1-Porosity))).to(u.dimensionless)

    def f_Ergun(self, v_a, D_Sand, Temperature, Porosity):
        return 300/self.Re_Ergun(v_a, D_Sand, Temperature, Porosity) + 3.5

    def hf_Ergun(self, v_a, D_Sand, Temperature, Porosity, L):
        return (self.f_Ergun(v_a, D_Sand, Temperature, Porosity)*L/D_Sand*v_a**2/(2*u.gravity)*(1-Porosity)/Porosity**3).to(u.m)
    @property
    def k_e(self):
        return hl.PIPE_ENTRANCE_K_MINOR + 3*hl.EL90_K_MINOR

    @property
    def clean_bed_hl_min(self):
        clean_bed_hl_min = self.hf_Ergun(
            self.vel,
            self.sand_diam, 
            self.temp_max, 
            self.porosity, 
            self.layer_h
        )
        return clean_bed_hl_min
        
    def _set_trunk_pipe(self):  
        self.trunk_pipe = Pipe(size = self.trunk_size, spec = self.trunk_spec, l = self.trunk_length)
        
    @property 
    def trunk_max_hl(self):
        """This is the maximum head loss through the bottom filter inlet 
        (backwash inlet) during FILTRATION mode given the constraint
        that the flow must be evenly distributed between sand layers """
        filter_sand_hl = self.hf_Ergun(
            self.filter_v, 
            self.sand_d, 
            self.temp_max, self.sand_porosity, 
            self.layer_h
        )
        term1 = (2 * self.ratio_qp + 1)/3 * (1 - self.ratio_qp)
        term2 = 4 * self.ratio_qp**2 - 1
        return (filter_sand_hl * term1)/term2
    
    @property
    def max_q(self):
        """This is the maximum flow through a filter with a given size of trunk
        given the constraint that the flow must be evenly distributed between 
        sand layers """
        return 6*pc.flow_pipe(
            self.trunk_pipe.id, 
            self.trunk_max_hl, 
            self.trunk_pipe.l, 
            pc.viscosity_kinematic(self.temp_max), 
            mat.PVC_PIPE_ROUGH, 
            self.k_e
            )

    @property
    def ratio_trunk_sand_hl(self):
        return ((2*self.ratio_qp+1)/3) * \
            ((1-self.ratio_qp) / (4*self.ratio_qp**2 - 1))
    
    @property
    def backwash_hl(self):
        return self.layer_h * \
            (1-self.porosity) * \
            (self.sand_density/pc.density_water(self.temp)-1)









#Design guidelines say 11 mm/s. The success of lab-scale backwashing at
# 10 mm/s suggests that this is a reasonable and conservative value
BACKWASH_VEL = 11 * u.mm / u.s

LAYER_N = 6

LAYER_VEL = 1.833 * u.mm / u.s ##VEL_FIBER_DIST_CENTER_/N_FIBER_LAYER

##Minimum thickness of each filter layer (can be increased to accomodate
# larger pipe diameters in the bottom layer)
LAYER_H_MIN = 20 * u.cm

##center to center distance for slotted pipes
MAN_CENTER_BRANCH_DIST = 10 * u.cm

##How far the branch extends into the trunk line
MAN_BRANCH_EXTENSION_L = 2 * u.cm

##The time to drain the filter box of the water above the fluidized bed
FIBER_BACKWASH_INITIATION_BOD_TIME = 3 * u.min

##Mickey suggested this value based on lab experience. This was moved to
# Expert Inputs 12/4/16 by mrf222 as a result of feedback from Monroe and
# Skyler. In the Moroceli plant, the Fi Entrance box was overflowing
# before filtration backwash. The HL of a dirty filter has therefore been
# increased from 40 to 60 cm.
HL_DIRTY = 60 * u.cm

##This is the extra head we are going to provide on top of steady state
# backwash head loss to ensure that we can fluidize the bed to initiate
# backwash.
HL_FIBER_BACKWASH_STEADY_FLOW = 20 * u.cm

##Maximum acceptable head loss through the siphon at steady state; used to
# calculate a diameter
SIPHON_HL_MAX = 35 * u.cm

##Diameter of sand drain pipe
SAND_OUTLET_D = 2 * u.inch

##Height of the barrier between the exit box and distribution box.
BARRIER_EXIT_DISTRIBUTION_H = 10 * u.cm

##Length that the siphon pipe extends up into the plant drain channel.
#Being able to shorten the stub from which the siphon discharges into the
# main plant drain channel allows for some flexibility in the hydraulic design.
SIPHON_CHANNEL_STUB_L_MIN = 20 * u.cm

ENTRANCE_PIPE_HL_MAX = 10 * u.cm

TRUNK_D_MAX = 6 * u.inch

BACKWASH_SIPHON_D_MAX = 8 * u.inch

##Purge valves on the trunk lines are angled downwards so that sediment is
# cleared more effectively. This angle allows the tees to fit on top of one
# another at the filter wall.
TRUNK_VALVES_ANGLE = 25 * u.deg

##Purge valves on the trunk lines are angled downwards so that sediment is
# cleared more effectively. This angle allows the tees to fit on top of one
# another at the filter wall.
WEIR_THICKNESS = 5 * u.cm

BRANCH_WALL_S = 5 * u.cm

GATE_VALUE_URL = "https://confluence.cornell.edu/download/attachments/173604905/Fi-Scaled-Gate-Valve-Threaded.dwg"
BALL_VALVE_URL = "https://confluence.cornell.edu/download/attachments/173604905/FiMetalBallValve.dwg"

WALL_PLANT_FLOOR_S_MIN = 10 * u.cm

INLET_WEIR_HL_MAX = 5 * u.cm

##Dimensions get too small for construction below a certain flow rate
Q_MIN = 8 * u.L / u.s

MAN_FEMCO_COUPLING_L = 6 * u.cm

##Nominal diameter of the spacer tees in the four corners of the filter
# manifold assembly.
MAN_WING_SPACER_ND = 2 * u.inch

##Length of the vertical pipe segment following the valve on the filter
# sand drain. This stub can be capped to allow the sand in the valve to
# settle, so that the valve can be closed without damage from fluidized sand.
SAND_OUTLET_PIPE_L = 20 * u.cm

#######Elevation Safety Margins

##Minimum depth in the entrance box during backwash such that there is
# standing water over the inlet.
BACKWASH_NO_SUCK_AIR_H = 20 * u.cm

##Minimum water depth over the orifices in the siphon manifold so that air
# is not entrained.
SIPHON_NO_SUCK_AIR_H = 10 * u.cm

FLUIDIZED_BED_TO_SIPHON_H = 20 * u.cm

FORWARD_NO_SUCK_AIR_H = 10 * u.cm

WEIR_FREEFALL_H = 3 * u.cm

AIR_REMOVAL_BLOCK_SUBMERGED_H = 5 * u.cm

BYPASS_SAFETY_H = 10 * u.cm

DRAIN_OUTLET_SAFETY_H = 10 * u.cm

OVERFLOW_WEIR_FREEFALL_H = 10 * u.cm

#We are going to take this pipe size for the slotted pipes as a given.
# Larger pipes may block too much flow and they are harder to install.
MAN_BRANCH_ND = 1*u.inch

MAN_BRANCH_BACKWASH_ND = 1.5*u.inch

#A slot thickness of 0.008 in or 0.2 mm is selected so that sand
# will not enter the slotted pipes.
MANIFOLD_SLOTS_W = 0.008*u.inch

BRANCH_HOLDER_ND = 2*u.inch

BACKWASH_BRANCH_HOLDER_ND = 2*u.inch

#Minimum vertical spacing between trunk line pipes going through
#the filter wall for concrete construction
TRUNK_S_MIN = 3 * u.cm

#Space between the ends of the branch receiver pipes and the walls so that
#the manifold assemblies are easy to lower into the filter boxes
# (if the branch receivers extended the entire length of the box they would
#just barely fit and it would be hard to get into place)
MAN_ASSEMBLY_S = 1 * u.cm

##Sand Properties

SAND_D_EFFECTIVE = 0.5 * u.mm

SAND_UNIFORMITY_RATIO = 1.65

DIAM_FILTER_SAND_60 = SAND_D_EFFECTIVE * SAND_UNIFORMITY_RATIO

#Porosity in a sand bed
SAND_POROSITY = 0.4

SAND_DENSITY = 2650 * u.kg / (u.m ** 3)

FLUIDIZED_RATIO = 1.3 #Bed expands 30% when fluidized
