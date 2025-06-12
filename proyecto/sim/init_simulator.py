# sim/init_simulator.py
from sim.simulator import OrderSimulator

def init_simulator():
    if 'simulador' not in st.session_state:
        st.session_state.simulador = OrderSimulator()
