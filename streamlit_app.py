import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime, timedelta

# Configuración de la página
st.set_page_config(page_title="FISIOCARE - Sistema de Gestión", layout="wide")

# --- TÍTULO Y LOGO ---
st.title("🏥 Sistema de Gestión FISIOCARE")
st.markdown("---")

# --- CONEXIÓN A GOOGLE SHEETS ---
# Asegúrate de configurar st.secrets con tu URL de Google Sheet
conn = st.connection("gsheets", type=GSheetsConnection)

# Función para leer datos
def load_data(sheet_name):
    # Esto obliga al sistema a buscar la pestaña exacta
    return conn.read(worksheet=sheet_name, ttl="0")

# --- MENÚ LATERAL ---
st.sidebar.image("https://via.placeholder.com/150", caption="FISIOCARE") # Aquí pondremos tu logo luego
menu = st.sidebar.radio(
    "Seleccione una sección:",
    ["📅 Agenda Diaria", "📦 Gestión de Paquetes", "👤 Registro de Pacientes"]
)

# --- LÓGICA DE SECCIONES ---

# 1. REGISTRO DE PACIENTES
if menu == "👤 Registro de Pacientes":
    st.header("Registrar Nuevo Paciente")
    with st.form("form_paciente"):
        dni = st.text_input("DNI del Paciente")
        nombre = st.text_input("Nombre Completo")
        celular = st.text_input("Celular (con código de país)")
        diagnostico = st.text_area("Diagnóstico Inicial")
        color = st.selectbox("Asignar Color/Prioridad", ["Verde", "Amarillo", "Rojo"])
        
        submitted = st.form_submit_button("Guardar Paciente")
        if submitted:
            # Aquí iría la lógica para hacer el append al Google Sheet
            st.success(f"Paciente {nombre} registrado con éxito (Simulado).")

# 2. GESTIÓN DE PAQUETES
elif menu == "📦 Gestión de Paquetes":
    st.header("Seguimiento de Paquetes de Sesiones")
    st.info("Los paquetes vencen automáticamente a los 90 días de la compra.")
    
    # Cargar datos de paquetes (Simulado)
    df_paquetes = load_data("Paquetes")
    
    if not df_paquetes.empty:
        # Calcular días restantes (Lógica de los 90 días)
        df_paquetes['Fecha_Compra'] = pd.to_datetime(df_paquetes['Fecha_Compra'])
        df_paquetes['Vencimiento'] = df_paquetes['Fecha_Compra'] + timedelta(days=90)
        
        st.dataframe(df_paquetes, use_container_width=True)
    else:
        st.warning("No hay paquetes registrados aún.")

# 3. AGENDA DIARIA (El Corazón del Sistema)
elif menu == "📅 Agenda Diaria":
    st.header("Agenda de Citas y Cupos")
    
    # Mostrar citas del día
    df_agenda = load_data("Agenda")
    st.subheader("Citas Programadas")
    st.dataframe(df_agenda, use_container_width=True)

    st.markdown("---")
    st.subheader("🆕 Agendar Nueva Cita")

    with st.form("form_cita"):
        fecha_cita = st.date_input("Fecha de la cita", datetime.now())
        hora_cita = st.time_input("Hora de la cita")
        dni_pac = st.text_input("DNI del Paciente")
        tipo_t = st.selectbox("Tipo de Terapia", ["Convencional", "Integral", "Inductivo", "Evaluación"])
        
        # Mapeo de colores según tipo de terapia
        color_cita = "Amarillo" if tipo_t in ["Integral", "Inductivo"] else "Rojo" if tipo_t == "Evaluación" else "Verde"
        
        btn_agendar = st.form_submit_button("Verificar Cupos y Agendar")

        if btn_agendar:
            # --- REGLA DE ORO: LÓGICA DE CUPOS ---
            # Filtramos las citas para esa fecha y hora
            citas_bloque = df_agenda[(df_agenda['Fecha'] == str(fecha_cita)) & (df_agenda['Hora'] == str(hora_cita))]
            
            amarillos_hoy = len(citas_bloque[citas_bloque['Color'] == "Amarillo"])
            rojos_hoy = len(citas_bloque[citas_bloque['Color'] == "Rojo"])

            if color_cita == "Amarillo" and amarillos_hoy >= 3:
                st.error("🚫 ¡ALERTA! Ya existen 3 pacientes Amarillos en este horario. No se puede agendar más.")
            elif color_cita == "Rojo" and rojos_hoy >= 2:
                st.error("🚫 ¡ALERTA! Capacidad máxima de Evaluaciones (Rojo) alcanzada para este turno.")
            else:
                # Si pasa las reglas, se procedería a guardar
                st.success(f"✅ Cupo disponible para cita {color_cita}. Registrando...")
                # Lógica para guardar en Google Sheets aquí...
