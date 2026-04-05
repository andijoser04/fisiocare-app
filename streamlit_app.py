import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime, timedelta

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="FISIOCARE - Gestión Integral", layout="wide", page_icon="🏥")

# --- ESTILOS PERSONALIZADOS ---
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #007bff; color: white; }
    .stAlert { border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True) # <-- AQUÍ ESTABA EL ERROR, YA LO CORREGÍ

# 2. CONEXIÓN A GOOGLE SHEETS
# Usa las credenciales configuradas en los Secrets de Streamlit
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data(sheet_name):
    try:
        return conn.read(worksheet=sheet_name, ttl=0)
    except Exception as e:
        st.error(f"Error al conectar con la pestaña {sheet_name}: {e}")
        return pd.DataFrame()

# 3. MENÚ LATERAL
st.sidebar.title("🏥 FISIOCARE")
st.sidebar.markdown("---")
menu = st.sidebar.radio(
    "Navegación",
    ["📅 Agenda Diaria", "📦 Gestión de Paquetes", "👤 Registro de Pacientes"]
)

# --- LÓGICA DE LAS SECCIONES ---

# A. REGISTRO DE PACIENTES
if menu == "👤 Registro de Pacientes":
    st.header("👤 Registro de Nuevos Pacientes")
    st.write("Complete los datos para añadir un paciente a la base de datos de FISIOCARE.")
    
    with st.form("nuevo_paciente", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            dni = st.text_input("DNI / CE")
            nombre = st.text_input("Nombre Completo")
        with col2:
            celular = st.text_input("Celular (Ej: +51999888777)")
            color_prio = st.selectbox("Prioridad/Color", ["Verde", "Amarillo", "Rojo"])
        
        diagnostico = st.text_area("Diagnóstico Inicial")
        
        submit = st.form_submit_button("Guardar Paciente")
        
        if submit:
            if dni and nombre:
                # Aquí se añadiría la lógica de conn.update para escribir en el Excel
                st.success(f"✅ Paciente {nombre} listo para ser guardado en la base de datos.")
            else:
                st.error("⚠️ Por favor, complete DNI y Nombre.")

# B. GESTIÓN DE PAQUETES
elif menu == "📦 Gestión de Paquetes":
    st.header("📦 Control de Paquetes y Sesiones")
    st.info("💡 Los paquetes expiran automáticamente a los 90 días de la compra.")
    
    df_paquetes = load_data("Paquetes")
    
    if not df_paquetes.empty:
        # Lógica de vencimiento
        df_paquetes['Fecha_Compra'] = pd.to_datetime(df_paquetes['Fecha_Compra'])
        df_paquetes['Fecha_Vencimiento'] = df_paquetes['Fecha_Compra'] + timedelta(days=90)
        
        # Mostrar tabla con formato
        st.dataframe(df_paquetes, use_container_width=True)
    else:
        st.warning("No hay paquetes registrados en el sistema.")

# C. AGENDA DIARIA (La Regla de Oro)
elif menu == "📅 Agenda Diaria":
    st.header("📅 Agenda de Turnos FISIOCARE")
    
    # Mostrar Agenda Actual
    df_agenda = load_data("Agenda")
    
    col_ag, col_form = st.columns([2, 1])
    
    with col_ag:
        st.subheader("Citas Programadas")
        if not df_agenda.empty:
            st.dataframe(df_agenda, use_container_width=True)
        else:
            st.write("No hay citas para mostrar.")

    with col_form:
        st.subheader("📝 Agendar Cita")
        with st.form("nueva_cita", clear_on_submit=True):
            fecha = st.date_input("Fecha", datetime.now())
            hora = st.selectbox("Hora", ["08:00", "09:00", "10:00", "11:00", "12:00", "15:00", "16:00", "17:00", "18:00"])
            paciente = st.text_input("Nombre del Paciente")
            terapia = st.selectbox("Tipo de Terapia", ["Convencional", "Integral/Inductivo", "Evaluación"])
            
            # Definir color según terapia
            color_cita = "Amarillo" if terapia == "Integral/Inductivo" else "Rojo" if terapia == "Evaluación" else "Verde"
            
            check_cupo = st.form_submit_button("Verificar y Agendar")
            
            if check_cupo:
                # --- REGLA DE ORO ---
                # Filtrar citas en el mismo horario
                citas_mismo_horario = df_agenda[(df_agenda['Fecha'] == str(fecha)) & (df_agenda['Hora'] == hora)]
                
                cont_amarillo = len(citas_mismo_horario[citas_mismo_horario['Color'] == "Amarillo"])
                cont_rojo = len(citas_mismo_horario[citas_mismo_horario['Color'] == "Rojo"])
                
                if color_cita == "Amarillo" and cont_amarillo >= 3:
                    st.error(f"🚫 CAPACIDAD MÁXIMA: Ya hay {cont_amarillo} pacientes AMARILLOS a las {hora}. Elija otro horario.")
                elif color_cita == "Rojo" and cont_rojo >= 2:
                    st.error(f"🚫 CAPACIDAD MÁXIMA: Ya hay {cont_rojo} EVALUACIONES (Rojo) a las {hora}.")
                else:
                    st.success(f"✅ Cupo disponible para cita {color_cita}. Procediendo a registrar...")
                    # Aquí iría el conn.update para guardar en Google Sheets
