# config.py
from dataclasses import dataclass
import numpy as np

# --- Physical Constants ---
G0 = 9.80665          # m/s^2
PA_SL = 101325.0      # Pa 
T_SL = 288.15         # K 
R_AIR = 287.05        # J/(kg*K) 
RHO_SL = 1.225        # kg/m^3 

# --- Simulation Constants ---
SIM_MAX_TIME = 300.0  
GRAIN_DT = 0.005      

@dataclass
class Propellant:
    density: float
    a: float  
    n: float  
    c_star: float

@dataclass
class RocketSpec:
    m0: float
    mp: float
    CD_A: float

@dataclass
class FixedGrain:
    OD: float      # mm
    d_core: float  # mm
    length: float  # mm

@dataclass
class EngineDesign:
    k_gamma: float
    epsilon: float
    efficiency: float
    max_Pc_limit: float  # 케이싱 허용 최대 압력 (Pa)