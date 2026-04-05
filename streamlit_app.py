import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime, timedelta

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(
    page_title="FISIOCARE - Sistema de Gestión",
    page_icon="🏥",
    layout="wide"
)

# --- ESTILOS VISUALES ---
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { 
        width: 100%; 
        background-color: #007bff; 
        color: white; 
        border-radius: 8px;
        height: 3em;
        font-weight: bold;
    }
    .stDataFrame { border: 1px solid #e6e9ef; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# 2. CONEXIÓN AUTOMÁTICA A GOOGLE SHEETS
# Esto usa los Secrets (Service Account) que pusimos en Streamlit
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data(sheet_name):
    try:
        # ttl=0 asegura que siempre lea los datos reales y no use memoria vieja
        df = conn.read(worksheet=sheet_name, ttl=0)
        if df is not None:
            return df
        return pd.DataFrame()
    except Exception as e:
        st.sidebar.error(f"Error cargando {sheet_name}: {e}")
        return pd.DataFrame()

# 3. MENÚ LATERAL
st.sidebar.title("🏥 FISIOCARE")
st.sidebar.markdown("---")
menu = st.sidebar.radio(
    "Seleccione una opción:",
    ["📅 Agenda Diaria", "📦 Gestión de Paquetes", "👤 Registro de Pacientes"]
)

# --- LÓGICA DE LAS SECCIONES ---

# SECCIÓN: AGENDA DIARIA (Regla de Oro)
if menu == "📅 Agenda Diaria":
    st.header("📅 Agenda de Turnos y Cupos")
    
    df_agenda = load_data("Agenda")
    
    col_tabla, col_form = st.columns([2, 1])
    
    with col_tabla:
        st.subheader("Citas Programadas")
        if not df_agenda.empty:
            st.dataframe(df_agenda, use_container_width=True, hide_index=True)
        else:
            st.info("No hay citas registradas en la pestaña 'Agenda'.")

    with col_form:
        st.subheader("📝 Agendar Nueva Cita")
        with st.form("nueva_cita", clear_on_submit=True):
            f_cita = st.date_input("Fecha", datetime.now())
            h_cita = st.selectbox("Hora", ["08:00", "09:00", "10:00", "11:00", "12:00", "15:00", "16:00", "17:00", "18:00"])
            p_nombre = st.text_input("Nombre del Paciente")
            t_terapia = st.selectbox("Tipo de Terapia", ["Convencional", "Integral/Inductivo", "Evaluación"])
            
            # Definir color automático
            if t_terapia == "Integral/Inductivo":
                color_val = "Amarillo"
            elif t_terapia == "Evaluación":
                color_val = "Rojo"
            else:
                color_val = "Verde"
            
            if st.form_submit_button("Validar y Agendar"):
                if not p_nombre:
                    st.error("⚠️ Ingrese el nombre del paciente.")
                else:
                    # --- REGLA DE ORO: VALIDACIÓN DE CUPOS ---
                    citas_hora = df_agenda[(df_agenda['Fecha'].astype(str) == str(f_cita)) & (df_agenda['Hora'].astype(str) == h_cita)]
                    
                    n_amarillos = len(citas_hora[citas_hora['Color'] == "Amarillo"])
                    n_rojos = len(citas_hora[citas_hora['Color'] == "Rojo"])
                    
                    if color_val == "Amarillo" and n_amarillos >= 3:
                        st.error(f"🚫 BLOQUEADO: Ya hay 3 pacientes Amarillos a las {h_cita}.")
                    elif color_val == "Rojo" and n_rojos >= 2:
                        st.error(f"🚫 BLOQUEADO: Máximo 2 Evaluaciones (Rojo) permitidas a las {h_cita}.")
                    else:
                        st.success(f"✅ Cupo disponible para {color_val}. Conexión lista para guardar.")

# SECCIÓN: GESTIÓN DE PAQUETES
elif menu == "📦 Gestión de Paquetes":
    st.header("📦 Control de Paquetes de Sesiones")
    st.info("💡 Los paquetes expiran automáticamente a los 90 días de la compra.")
    
    df_paquetes = load_data("Paquetes")
    
    if not df_paquetes.empty:
        # Lógica de cálculo de vencimiento (90 días)
        df_paquetes['Fecha_Compra'] = pd.to_datetime(df_paquetes['Fecha_Compra'])
        df_paquetes['Vencimiento'] = df_paquetes['Fecha_Compra'] + timedelta(days=90)
        st.dataframe(df_paquetes, use_container_width=True, hide_index=True)
    else:
        st.warning("No hay paquetes registrados.")

# SECCIÓN: REGISTRO DE PACIENTES
elif menu == "👤 Registro de Pacientes":
    st.header("👤 Base de Datos de Pacientes")
    df_pacientes = load_data("Pacientes")
    
    if not df_pacientes.empty:
        st.dataframe(df_pacientes, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    with st.expander("➕ Registrar Nuevo Paciente"):
        with st.form("form_p"):
            c1, c2 = st.columns(2)
            dni_p = c1.text_input("DNI / CE")
            nom_p = c1.text_input("Nombre y Apellido")
            cel_p = c2.text_input("Celular")
            diag_p = st.text_area("Diagnóstico")
            
            if st.form_submit_button("Guardar en FISIOCARE"):
                st.success(f"Datos de {nom_p} listos para ser enviados al Excel.")
