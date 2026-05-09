# flight.py
import numpy as np
from scipy.integrate import solve_ivp
from scipy.interpolate import interp1d
from config import RocketSpec, EngineDesign, FixedGrain
from config import SIM_MAX_TIME, G0
from physics import get_isa_atmosphere

class RocketFlightSim:
    def __init__(self, spec: RocketSpec):
        self.spec = spec

    def _eom_dynamic(self, t, X, thrust_interp, tb_end):
        h, v = X
        F = float(thrust_interp(t)) if t <= tb_end else 0.0
        rho, _ = get_isa_atmosphere(h)
        m = self.spec.m0 - (self.spec.mp/tb_end * t if t <= tb_end else self.spec.mp)
        
        net_force = F - (0.5 * rho * self.spec.CD_A * (v**2) * np.sign(v)) - (m * G0)
        if h <= 0 and net_force <= 0: return [0, 0]
        
        return [v, net_force / m]

    def run_dynamic_thrust(self, time_arr: np.ndarray, thrust_arr: np.ndarray) -> tuple:
        if len(time_arr) < 2: return np.array([0.0]), np.array([[0.0], [0.0]])
        
        thrust_f = interp1d(time_arr, thrust_arr, bounds_error=False, fill_value=0.0)
        tb_end = time_arr[-1]

        def hit_ground(t, y):
            if t < 0.1: return 1
            return y[0] if y[1] < 0 else 1
        hit_ground.terminal = True
        hit_ground.direction = -1

        sol = solve_ivp(
            fun=lambda t, y: self._eom_dynamic(t, y, thrust_f, tb_end),
            t_span=[0, SIM_MAX_TIME], y0=[0.0, 0.0],
            events=hit_ground, t_eval=np.linspace(0, SIM_MAX_TIME, 2000), rtol=1e-5
        )
        return sol.t, sol.y

class NozzleOptimizer:
    def __init__(self, spec: RocketSpec, design: EngineDesign):
        self.sim = RocketFlightSim(spec)
        self.design = design

    def maximize_altitude(self, motor, grain: FixedGrain):
        best_h = 0.0
        best_motor_res = None
        best_flight_res = None
        
        # 노즐 목 직경을 10mm ~ 30mm 범위에서 촘촘하게 탐색 (스윕)
        Dt_candidates = np.linspace(10.0, 30.0, 100)
        max_Pc_bar = self.design.max_Pc_limit / 1e5
        
        for Dt in Dt_candidates:
            res = motor.evaluate_fixed_grain(Dt, grain)
            
            # 구조적 안정성 검토: 챔버 압력이 케이싱 허용치를 넘으면 탈락
            if res['sim_max_pressure_bar'] > max_Pc_bar:
                continue
                
            # 압력 조건 통과 시 비행 궤적 해석
            t_sim, y_sim = self.sim.run_dynamic_thrust(res['sim_time'], res['sim_thrust'])
            h_max = np.max(y_sim[0])
            
            # 최고 고도 갱신
            if h_max > best_h:
                best_h = h_max
                best_motor_res = res
                best_flight_res = (t_sim, y_sim)
                
        return best_h, best_motor_res, best_flight_res