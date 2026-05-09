# 🚀 KNSB Nozzle Performance Optimizer

![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-UI-FF4B4B.svg)
![SciPy](https://img.shields.io/badge/SciPy-solve__ivp-8CAAE6.svg)

본 프로젝트는 엄격한 추진제 질량 제한(ex. KNSB 400g) 규정 하에서 고체 로켓의 비행 고도를 극대화하기 위한 **노즐 형상 자동 최적화 및 비행 동역학 시뮬레이터**입니다. 

사용자는 Streamlit 대시보드를 통해 고정된 그레인(Grain) 제원과 케이싱의 최대 허용 압력을 입력하고, 모터 파열 한계를 넘지 않으면서 추력을 극한으로 끌어올리는 최적의 노즐 목(Throat)과 팽창비(Expansion Ratio)를 산출할 수 있습니다.

## ✨ Key Features

* **Fixed-Grain Ballistics:** BATES 그레인 형상의 실시간 연소 면적(Ab) 변화를 반영한 정밀한 순방향 내탄도학(Internal Ballistics) 해석.
* **Nozzle Sweep Optimization:** 10mm ~ 30mm 구간의 노즐 목 직경(Dt) 후보군을 스윕(Sweep)하여, 가장 높은 Apogee를 달성하는 최적의 형상 탐색.
* **Structural Safety Filter:** 케이싱의 구조적 파괴를 방지하기 위해, 시뮬레이션 중 최대 챔버 압력이 허용치(Max Allowed Pressure)를 초과하는 노즐 설계는 자동으로 필터링.
* **1-DOF Flight Dynamics:** `scipy.integrate.solve_ivp` (RK45) 기반의 공기 저항 및 고도별 대기압(ISA) 모델이 반영된 궤적 예측.
* **Comprehensive Excel Export:** 최적화된 엔진 제원, 비행 결과, 그리고 시계열(Time-series) 추력/압력 원시 데이터를 3개의 시트로 분리하여 원클릭 추출.

## 📂 Project Structure

프로젝트는 유지보수와 물리 모델의 독립성을 위해 5개의 핵심 파일로 구성되어 있습니다.

```text
├── app.py         # Streamlit UI 렌더링, 사용자 입력 및 엑셀 Export 컨트롤러
├── config.py      # 물리 상수, 추진제 물성치, 고정 그레인 및 제약 조건 데이터 클래스
├── engine.py      # SolidMotor 클래스: 주어진 노즐과 그레인 제원으로 시계열 내탄도학 적분 수행
├── flight.py      # RocketFlightSim & NozzleOptimizer: 1-DOF 비행 해석 및 최대 고도 탐색 알고리즘
└── physics.py     # ISA 표준 대기 모델 및 마하 수 루트 파인딩(Root-finding) 물리 유틸리티
```

## ⚙️ Installation
본 프로그램을 실행하기 위해서는 Python 3.9 이상의 환경이 필요합니다. 가상 환경 활성화 후 아래 명령어를 통해 필수 패키지를 설치하십시오.

```markdown
pip install streamlit numpy scipy matplotlib pandas xlsxwriter
```
## 🚀 Quick Start
터미널에서 아래 명령어를 실행하여 웹 기반 GUI 대시보드를 시작합니다.

```markdown
streamlit run app.py
```
## 📊 Outputs & Visualizations
시뮬레이션을 실행하면 다음 결과가 대시보드에 즉각 렌더링됩니다.

Optimization Metrics: 도출된 최적 노즐 목 직경(Dt), 예상 최고 고도, 최고 챔버 압력.
Dynamic Charts: 시간에 따른 고도(Altitude), 속도(Velocity), 챔버 압력(Chamber Pressure), 추력(Thrust) 변화 추이 그래프 (다크모드 최적화).
Excel Report: Design_Input, Output_Data, Raw_Time_Data 시트로 깔끔하게 포맷팅된 종합 엔지니어링 리포트 다운로드.

## 🧑‍💻 Maintainer
Developed by: PARK SEONG-JAE, Propulsion Team Leader, KARS2026
Focus Area: Mechatronics Engineering, Control Systems, Solid Propulsion System Design & Numerical Modeling.
