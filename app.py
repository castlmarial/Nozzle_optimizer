import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import io
from datetime import datetime

from config import Propellant, RocketSpec, EngineDesign, FixedGrain, G0
from engine import SolidMotor
from flight import RocketFlightSim, NozzleOptimizer

# --- 1. 페이지 설정 (최상단에 한 번만!) ---
st.set_page_config(
    page_title="KNSB Rocket Simulator",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

def show_welcome_page():
    st.title("🚀 KNSB Nozzle Performance Optimizer")
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col1: st.info("### 🔒 Fixed Grain\n고정된 KNSB 그레인 볼륨과 연소 면적을 기반으로 추진 에너지 고정")
    with col2: st.success("### 🛠️ Nozzle Optimization\n추진제의 에너지를 최대한 사용하는 최대고도 도달하는 노즐 스펙 탐색")
    with col3: st.warning("### 📊 Engineering Report\n입력 변수부터 시계열 데이터까지 원클릭 Excel 리포트 생성 및 추출")

# --- 푸터 함수 정의 ---
def show_footer():
    st.markdown("---")
    st.markdown(
        """
        <div style="text-align: center; padding: 40px 0px 20px 0px; color: #64748b;">
            <p style="font-size: 14px; letter-spacing: 1px; margin-bottom: 10px;">
                © 2026 KNSB Rocket Project
            </p>
            <p style="font-size: 18px; font-weight: 700; color: #3b82f6;">
                KARS2026 | Propulsion Team Leader | PARK SEONG-JAE
            </p>
            <div style="margin-top: 15px; font-family: monospace; font-size: 13px;">
                Mechatronics Engineering & Control Systems Focus
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with st.sidebar:
    st.header("🛠️ Design Parameters")
    
    st.subheader("🧪 Fixed Propellant Grain")
    grain_od = st.number_input("Grain Outer Diameter (mm)", value=50.0, disabled=True)
    grain_core = st.number_input("Grain Core Diameter (mm)", value=20.3, disabled=True)
    grain_len = st.number_input("Grain Length (mm)", value=147.9, disabled=True)
    prop_rho = st.number_input("Density (kg/m³)", value=1650.0, disabled=True)
    prop_mass = st.number_input("Propellant Mass (kg)", value=0.400, disabled=True)
    
    grain = FixedGrain(OD=grain_od, d_core=grain_core, length=grain_len)
    c_star_input = st.number_input("C* (m/s)", value=910.0, step=1.0)
    prop = Propellant(density=prop_rho, a=0.1007/1000.0, n=0.319, c_star=c_star_input)

    st.subheader("🚀 Rocket Specs & Limits")
    m0 = st.number_input("Total Initial Mass (kg)", value=6.00, format="%.2f")
    CD_A = st.number_input("CD_A (m²)", value=0.01397, format="%.5f") # 154mm 직경 기준 Cd=0.75 가정
    max_pc_bar = st.number_input("Max Allowed Pressure (bar)", value=30.0, help="모터 케이싱의 구조적 파괴를 막기 위한 한계 압력입니다.")
    spec = RocketSpec(m0=m0, mp=prop_mass, CD_A=CD_A)

    st.subheader("🔥 Nozzle Settings")
    k_gamma = st.number_input("Specific Heat Ratio", value=1.137, format="%.3f")
    epsilon = st.number_input("Expansion Ratio", value=5.000, format="%.3f")
    efficiency_factor = st.slider("Efficiency (η)", 0.5, 1.0, 0.92, 0.01)
    
    alpha_div = st.number_input("Divergence Half Angle (deg)", value=12.0, format="%.1f")
    beta_conv = st.number_input("Convergence Half Angle (deg)", value=30.0, format="%.1f")
    
    design = EngineDesign(
        k_gamma=k_gamma, epsilon=epsilon, efficiency=efficiency_factor,
        max_Pc_limit=max_pc_bar * 1e5
    )

    run_button = st.button("Run Optimization", type="primary", use_container_width=True)

if not run_button:
    show_welcome_page()
else:
    with st.spinner('Sweeping Nozzle Configurations...'):
        motor = SolidMotor(design, prop)
        optimizer = NozzleOptimizer(spec, design)
        h_max, best_motor_res, best_flight_res = optimizer.maximize_altitude(motor, grain)
        
    if best_motor_res is None:
        st.error("⚠️ 시뮬레이션 실패: 입력된 조건에서는 케이싱 압력 한계를 초과하지 않고 연소할 수 있는 노즐 형상을 찾지 못했습니다.")
    else:
        t_sim, y_sim = best_flight_res
        v_max = np.max(y_sim[1])
        
        # 데이터 계산 및 추가 항목 추출
        sim_impulse = best_motor_res['sim_total_impulse']
        sim_isp = sim_impulse / (spec.mp * G0)
        burn_time = best_motor_res['burn_time']
        avg_thrust = sim_impulse / burn_time if burn_time > 0 else 0
        peak_thrust = np.max(best_motor_res['sim_thrust']) # Peak Thrust 계산 추가

        st.markdown("---")
        st.header("🏆 Optimization Results")
        
        m_col1, m_col2, m_col3 = st.columns(3)
        m_col1.metric("Maximum Altitude", f"{h_max:.2f} m", "Target: Maximize")
        m_col2.metric("Optimized Throat (Dt)", f"{best_motor_res['Dt_mm']:.2f} mm")
        m_col3.metric("Peak Chamber Pressure", f"{best_motor_res['sim_max_pressure_bar']:.2f} bar", f"Limit: {max_pc_bar} bar")

        st.markdown("---")
        plt.style.use('dark_background')
        fig, axs = plt.subplots(2, 2, figsize=(15, 10))
        fig.patch.set_facecolor('#0E1117') 
        
        for ax in axs.flat:
            ax.set_facecolor('#0E1117')
            
        axs[0, 0].plot(t_sim, y_sim[0], color='dodgerblue', lw=2)
        axs[0, 0].set_title('Altitude vs Time', fontweight='bold')
        axs[0, 0].grid(True, ls='--', alpha=0.6)

        axs[0, 1].plot(t_sim, y_sim[1], color='mediumseagreen', lw=2)
        axs[0, 1].set_title('Velocity vs Time', fontweight='bold')
        axs[0, 1].grid(True, ls='--', alpha=0.6)

        axs[1, 0].plot(best_motor_res['sim_time'], best_motor_res['sim_pressure_bar'], color='darkorange', lw=2)
        axs[1, 0].axhline(max_pc_bar, color='red', ls='--', label='Safety Limit')
        axs[1, 0].set_title('Chamber Pressure vs Time', fontweight='bold')
        axs[1, 0].legend(); axs[1, 0].grid(True, ls='--', alpha=0.6)

        axs[1, 1].plot(best_motor_res['sim_time'], best_motor_res['sim_thrust'], color='crimson', lw=2)
        axs[1, 1].set_title('Thrust vs Time', fontweight='bold')
        axs[1, 1].grid(True, ls='--', alpha=0.6)

        plt.tight_layout()
        st.pyplot(fig)

        # ---------------------------------------------------------
        # [3] Excel Export 섹션
        # ---------------------------------------------------------
        st.markdown("---")
        st.subheader("📤 Export Comprehensive Data")

        # Sheet 1: Design_Input
        df_inputs = pd.DataFrame({
            "Category": [
                "Propellant", "Propellant", 
                "Rocket", "Rocket", "Rocket",
                "Engine", "Engine", "Engine", "Engine",
                "Nozzle", "Nozzle", "Engine"
            ],
            "Parameter": [
                "Density", "C*", 
                "Initial Mass", "Propellant Mass", "CD_A", 
                "Specific Heat Ratio", "Expansion Ratio", "Max Allowed Pressure", "Efficiency",
                "Divergence Half Angle", "Convergence Half Angle", "Grain Outer Diameter"
            ],
            "Value": [
                prop.density, prop.c_star, 
                spec.m0, spec.mp, spec.CD_A, 
                design.k_gamma, design.epsilon, max_pc_bar * 100000, design.efficiency,
                alpha_div, beta_conv, grain_od
            ],
            "Unit": [
                "kg/m³", "m/s", 
                "kg", "kg", "m²", 
                "-", "-", "Pa", "-",
                "deg", "deg", "mm"
            ]
        })

        # Sheet 2: Output_Data
        df_output = pd.DataFrame({
            "Metric": [
                "Peak Thrust", "Avg Thrust", "Total Impulse", "Burn Time", "Isp",
                "Peak Pressure", "Avg Pressure",
                "Nozzle Throat", "Nozzle Exit",
                "Div Angle", "Conv Angle", "Nozzle Efficiency",
                "Grain Outer Diameter", "Grain Core Diameter", "Grain Length", "Grain Density",
                "Maximum Altitude", "Maximum Velocity"
            ],
            "Value": [
                peak_thrust, avg_thrust, sim_impulse, burn_time, sim_isp,
                best_motor_res['sim_max_pressure_bar'], best_motor_res['sim_avg_pressure_bar'],
                best_motor_res['Dt_mm'], best_motor_res['De_mm'],
                alpha_div, beta_conv, design.efficiency * 100,
                grain_od, grain_core, grain_len, prop.density,
                h_max, v_max
            ],
            "Unit": [
                "N", "N", "N·s", "s", "s",
                "bar", "bar",
                "mm", "mm",
                "deg", "deg", "%",
                "mm", "mm", "mm", "kg/m³",
                "m", "m/s"
            ]
        })

        st.markdown("#### 📋 Output Data Summary")
        st.dataframe(df_output.set_index('Metric'), width='stretch')

        # Sheet 3: Raw_Time_Data
        df_series = pd.DataFrame({
            "Time (s)": best_motor_res['sim_time'],
            "Thrust (N)": best_motor_res['sim_thrust'],
            "Pressure (bar)": best_motor_res['sim_pressure_bar']
        })

        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
            df_inputs.to_excel(writer, sheet_name='Design_Input', index=False)
            df_output.to_excel(writer, sheet_name='Output_Data', index=False)
            df_series.to_excel(writer, sheet_name='Raw_Time_Data', index=False)
        
        st.download_button(
            label="💾 Download Comprehensive Excel Report",
            data=excel_buffer.getvalue(),
            file_name=f"Nozzle_Opt_Data_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
show_footer()