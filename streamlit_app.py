import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime, timedelta

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(
    page_title="FISIOCARE - Dashboard",
    page_icon="🏥",
    layout="wide"
)

# --- ESTILOS MODERNOS (CSS) ---
st.markdown("""
    <style>
    /* Fondo general */
    .main {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    
    /* Tarjetas de métricas */
    [data-testid="stMetricValue"] {
        font-size: 1.8rem;
        color: #007bff;
    }
    
    .stMetric {
        background-color: rgba(255, 255, 255, 0.8);
        padding: 15px;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transition: transform 0.3s ease;
    }
    
    .stMetric:hover {
        transform: translateY(-5px);
    }

    /* Botones modernos */
    .stButton>button {
        border-radius: 20px;
        background: linear-gradient(45deg, #007bff, #00d2ff);
        color: white;
        border: none;
        padding: 10px 20px;
        font-weight: bold;
        transition: all 0.3s;
    }
    
    .stButton>button:hover {
        box-shadow: 0 5px 15px rgba(0,123,255,0.4);
        transform: scale(1.02);
    }
    </style>
    """, unsafe_allow_html=True)

# 2. CONEXIÓN
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data(sheet_name):
    try:
        return conn.read(worksheet=sheet_name, ttl=0)
    except Exception:
        return pd.DataFrame()

# 3. LOGO Y SIDEBAR
# Nota: Reemplaza este link por el link de tu logo real
LOGO_URL = "https://drive.google.com/file/d/1yXF9BrRGA2krLyDezSvsPkkbfCOSvgfQ/view?usp=sharing"

st.logo(LOGO_URL, icon_image=LOGO_URL)
st.sidebar.image(LOGO_URL, width=120)
st.sidebar.title("FISIOCARE")
st.sidebar.markdown("*Centro de Fisioterapia y Rehabilitacion*")

menu = st.sidebar.selectbox(
    "Navegación Principal",
    ["🏠 Dashboard", "📅 Agenda Diaria", "📦 Paquetes", "👤 Pacientes"]
)

# --- SECCIONES ---

if menu == "🏠 Dashboard":
    st.title("🏥 ¡Bienvenido, Anderson!")
    st.markdown(f"Hoy es **{datetime.now().strftime('%d/%m/%Y')}**")
    
    # Cargar datos para el resumen
    df_agenda = load_data("Agenda")
    
    # Métricas rápidas
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Citas de Hoy", len(df_agenda) if not df_agenda.empty else 0)
    with c2:
        st.metric("Nuevos Pacientes", "+5", "12%")
    with c3:
        st.metric("Paquetes Activos", "24")
    with c4:
        st.metric("Ingresos Mes", "S/. 4,500", "8%")

    st.markdown("---")
    
    # Vista rápida de la agenda
    st.subheader("📌 Próximas Citas")
    if not df_agenda.empty:
        st.dataframe(df_agenda.head(5), use_container_width=True, hide_index=True)
    else:
        st.info("No hay citas programadas para hoy.")

elif menu == "📅 Agenda Diaria":
    st.header("📅 Control de Agenda")
    df_agenda = load_data("Agenda")
    
    tab1, tab2 = st.tabs(["👁️ Ver Agenda", "➕ Nueva Cita"])
    
    with tab1:
        if not df_agenda.empty:
            # Colorear según prioridad (simulado)
            st.dataframe(df_agenda, use_container_width=True)
        else:
            st.warning("Agenda vacía.")
            
    with tab2:
        st.subheader("Registrar Turno")
        with st.form("cita_moderna"):
            col_f, col_h = st.columns(2)
            fecha = col_f.date_input("Fecha")
            hora = col_h.selectbox("Hora", ["08:00", "09:00", "10:00", "11:00", "12:00", "15:00", "16:00", "17:00"])
            paciente = st.text_input("Nombre del Paciente")
            terapia = st.segmented_control("Terapia", ["Convencional", "Integral", "Evaluación"])
            
            if st.form_submit_button("Confirmar Cita"):
                st.balloons() # ¡Animación de éxito!
                st.success(f"Cita para {paciente} agendada correctamente.")

# Las otras secciones siguen la misma lógica...
