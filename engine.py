# engine.py
import numpy as np
from config import GRAIN_DT, PA_SL
from config import Propellant, EngineDesign, FixedGrain
from physics import calculate_exit_mach

class SolidMotor:
    def __init__(self, design: EngineDesign, prop: Propellant):
        self.design = design
        self.prop = prop

    def evaluate_fixed_grain(self, Dt_mm: float, grain: FixedGrain) -> dict:
        """주어진 노즐 목 직경(Dt)과 고정된 그레인 형상에 대한 내탄도학 해석"""
        rho, a, n, c_star = self.prop.density, self.prop.a, self.prop.n, self.prop.c_star
        At = (np.pi / 4) * (Dt_mm / 1000.0)**2
        
        D_grain = grain.OD / 1000.0
        L_grain = grain.length / 1000.0
        d_core = grain.d_core / 1000.0
        
        time_axis, thrust_axis, pressure_axis = [0.0], [0.0], [PA_SL]
        burn_depth, total_impulse = 0.0, 0.0
        
        # CF 계산을 위한 사전 세팅
        k = self.design.k_gamma
        epsilon = self.design.epsilon
        Ma = calculate_exit_mach(epsilon, k)
        Pe_ratio = (1 + (k - 1) / 2 * Ma**2)**(-k / (k - 1))
        
        while True:
            curr_d = d_core + 2 * burn_depth
            curr_L = L_grain - 2 * burn_depth
            if curr_d >= D_grain or curr_L <= 0: break
                
            Ab = (np.pi * curr_d * curr_L) + 2 * (np.pi/4 * (D_grain**2 - curr_d**2))
            Kn = Ab / At
            Pc = (Kn * rho * a * c_star) ** (1 / (1 - n))
            
            # 챔버 압력이 대기압보다 높을 때만 정상 연소 및 추력 발생
            if Pc > PA_SL * 1.05:
                term1 = (2 * k**2 / (k - 1))
                term2 = (2 / (k + 1))**((k + 1) / (k - 1))
                term3 = (1 - Pe_ratio**((k - 1) / k))
                CF_ideal_momentum = np.sqrt(term1 * term2 * term3) if term3 > 0 else 0
                CF_ideal_pressure = (Pe_ratio - PA_SL / Pc) * epsilon
                
                Cf_real = (CF_ideal_momentum + CF_ideal_pressure) * self.design.efficiency
                F_inst = Pc * At * Cf_real
            else:
                F_inst = 0.0
            
            time_axis.append(time_axis[-1] + GRAIN_DT)
            pressure_axis.append(Pc)
            thrust_axis.append(F_inst)
            
            total_impulse += F_inst * GRAIN_DT
            burn_depth += (a * (Pc ** n)) * GRAIN_DT
            
            if time_axis[-1] > 15.0: break # 안전망

        return {
            "Dt_mm": Dt_mm,
            "De_mm": Dt_mm * np.sqrt(epsilon),
            "sim_time": np.array(time_axis),
            "sim_thrust": np.array(thrust_axis),
            "sim_pressure_bar": np.array(pressure_axis) / 1e5,
            "sim_max_pressure_bar": np.max(pressure_axis) / 1e5,
            "sim_avg_pressure_bar": np.mean(pressure_axis) / 1e5,
            "sim_total_impulse": total_impulse,
            "burn_time": time_axis[-1]
        }