import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import os
import base64 # <-- NUEVA LIBRERÍA NECESARIA

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="FISIOCARE - Sistema Integral", layout="wide", page_icon="🏥")

# --- FUNCIÓN MÁGICA PARA EL VIDEO ---
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

# --- VIDEO DE FONDO Y ESTILOS AVANZADOS ---
video_file = "videobackground.mp4"

# Verificamos que el video exista para que la app no explote si te equivocas de nombre
if os.path.exists(video_file):
    video_base64 = get_base64_of_bin_file(video_file)
    video_html = f"""
        <style>
        #bgVideo {{
            position: fixed;
            right: 0;
            bottom: 0;
            min-width: 100%;
            min-height: 100%;
            z-index: -1;
            opacity: 0.3; /* 0.3 para que no moleste a la vista */
        }}
        </style>
        <video autoplay muted loop id="bgVideo">
            <source src="data:video/mp4;base64,{video_base64}" type="video/mp4">
        </video>
    """
    st.markdown(video_html, unsafe_allow_html=True)
else:
    st.warning(f"⚠️ Atención Ingeniero: No se encontró el archivo '{video_file}'")

st.markdown("""
    <style>
    .main { background: transparent; }
    
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');
    
    /* Tarjetas Semi-transparentes (Glassmorphism) */
    .stApp div[data-testid="stVerticalBlock"] > div {
        background-color: rgba(255, 255, 255, 0.85);
        padding: 20px;
        border-radius: 20px;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.15);
        backdrop-filter: blur(4px);
        border: 1px solid rgba(255, 255, 255, 0.18);
    }

    /* Botones Premium */
    .stButton>button {
        border-radius: 25px !important;
        background: linear-gradient(135deg, #00a896 0%, #028090 100%) !important;
        color: white !important;
        font-weight: bold !important;
        border: none !important;
        transition: 0.3s all;
    }
    .stButton>button:hover { transform: scale(1.02); box-shadow: 0 10px 20px rgba(0,168,150,0.3); }
    
    /* Botón de Eliminar (Rojo) */
    .btn-eliminar button {
        background: linear-gradient(135deg, #ff4b2b 0%, #ff416c 100%) !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. CONEXIÓN Y FUNCIONES (AQUÍ SIGUE TU CÓDIGO NORMAL...)
conn = st.connection("gsheets", type=GSheetsConnection)
# ...

# 2. CONEXIÓN Y FUNCIONES
conn = st.connection("gsheets", type=GSheetsConnection)

def load_sheet(name):
    try:
        df = conn.read(worksheet=name, ttl=0)
        return df.dropna(how='all')
    except:
        return pd.DataFrame()

def update_sheet(name, df):
    conn.update(worksheet=name, data=df)
    return True

# 3. INTERFAZ LATERAL
LOGO_PATH = "logo.png"
if os.path.exists(LOGO_PATH):
    st.sidebar.image(LOGO_PATH, width=150)
else:
    st.sidebar.title("🏥 FISIOCARE")

menu = st.sidebar.radio("MENÚ PRINCIPAL", ["🏠 Dashboard", "📅 Recepción y Agenda", "🩺 Módulo Licenciados", "👤 Expediente del Paciente"])

# --- CARGA INICIAL ---
df_agenda = load_sheet("Agenda")
df_pacientes = load_sheet("Pacientes")
df_precios = load_sheet("Precios")
df_historias = load_sheet("Historias")

# --- MÓDULOS ---

if menu == "🏠 Dashboard":
    st.title("Panel de Control - FISIOCARE")
    hoy = str(datetime.now().date())
    
    # Métricas Reales
    c_hoy = len(df_agenda[df_agenda['Fecha'].astype(str) == hoy]) if not df_agenda.empty else 0
    p_tot = len(df_pacientes) if not df_pacientes.empty else 0
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Citas para Hoy", c_hoy)
    col2.metric("Pacientes en Base", p_tot)
    col3.metric("Estado Sistema", "En Línea")

    st.markdown("---")
    st.subheader("📋 Turnos del Día")
    if not df_agenda.empty:
        st.dataframe(df_agenda[df_agenda['Fecha'].astype(str) == hoy], use_container_width=True, hide_index=True)
    else:
        st.info("Sin citas registradas para hoy.")

elif menu == "📅 Recepción y Agenda":
    st.header("📅 Gestión de Agenda")
    
    tab1, tab2 = st.tabs(["📝 Agendar Cita", "🗑️ Gestionar / Eliminar"])
    
    with tab1:
        with st.form("form_cita", clear_on_submit=True):
            c1, c2 = st.columns(2)
            f = c1.date_input("Fecha", datetime.now())
            h = c1.selectbox("Hora", ["08:00", "09:00", "10:00", "11:00", "12:00", "15:00", "16:00", "17:00", "18:00", "19:00"])
            
            nombres_p = df_pacientes['Nombre'].tolist() if not df_pacientes.empty else []
            pac_sel = c2.selectbox("Paciente", ["-- NUEVO --"] + nombres_p)
            
            if pac_sel == "-- NUEVO --":
                nom_final = c2.text_input("Nombre Completo")
                dni_final = c2.text_input("DNI")
            else:
                nom_final = pac_sel
                dni_final = df_pacientes[df_pacientes['Nombre'] == pac_sel]['DNI'].values[0]
            
            ter = c1.selectbox("Terapia", df_precios['Servicio'].tolist() if not df_precios.empty else ["Evaluación"])
            lic = c2.selectbox("Licenciado", ["Lic. Paul", "Lic. Andrea", "Lic. Diana", "Lic. Sofia"])
            
            if st.form_submit_button("Guardar Turno"):
                # Cálculo automático de costo y color
                costo = df_precios[df_precios['Servicio'] == ter]['Precio_Soles'].values[0] if not df_precios.empty else 0
                color = "Amarillo" if "Integral" in ter else "Rojo" if "Evaluación" in ter else "Verde"
                
                nueva_cita = pd.DataFrame([{
                    "ID_Cita": datetime.now().strftime("%d%m%H%M"),
                    "Fecha": str(f), "Hora": h, "DNI_Paciente": dni_final,
                    "Nombre_Paciente": nom_final, "Tipo_Terapia": ter, 
                    "Color": color, "Licenciado": lic, "Estado": "Pendiente", "Costo": costo
                }])
                
                # Si el paciente es nuevo, también lo guardamos en la base de pacientes
                if pac_sel == "-- NUEVO --":
                    nuevo_p = pd.DataFrame([{"DNI": dni_final, "Nombre": nom_final, "Celular": "", "Diagnostico": ""}])
                    df_p_act = pd.concat([df_pacientes, nuevo_p], ignore_index=True)
                    update_sheet("Pacientes", df_p_act)

                df_act = pd.concat([df_agenda, nueva_cita], ignore_index=True)
                update_sheet("Agenda", df_act)
                st.success(f"Cita de {nom_final} agendada.")
                st.rerun()

    with tab2:
        st.subheader("Eliminar Registros Mal Ingresados")
        if not df_agenda.empty:
            for i, row in df_agenda.iterrows():
                col_info, col_btn = st.columns([4, 1])
                col_info.write(f"**{row['Fecha']} - {row['Hora']}**: {row['Nombre_Paciente']} ({row['Licenciado']})")
                if col_btn.button("Eliminar 🗑️", key=f"del_{i}"):
                    df_nuevo = df_agenda.drop(i)
                    update_sheet("Agenda", df_nuevo)
                    st.warning("Cita eliminada.")
                    st.rerun()

elif menu == "🩺 Módulo Licenciados":
    st.header("🩺 Módulo de Atención")
    lic_sel = st.selectbox("Seleccione su nombre:", ["Lic. Paul", "Lic. Andrea", "Lic. Diana", "Lic. Sofia"])
    
    if not df_agenda.empty:
        # Filtrado corregido por licenciado y estado pendiente
        mis_citas = df_agenda[(df_agenda['Licenciado'] == lic_sel) & (df_agenda['Estado'] == 'Pendiente')]
        
        if not mis_citas.empty:
            for i, row in mis_citas.iterrows():
                with st.expander(f"Atender a: {row['Nombre_Paciente']} ({row['Hora']})"):
                    ev = st.text_area("Evolución de la sesión", key=f"ev_{i}")
                    plan = st.text_area("Plan siguiente", key=f"plan_{i}")
                    
                    if st.button("Finalizar Sesión", key=f"f_{i}"):
                        # 1. Guardar Historia
                        nueva_h = pd.DataFrame([{
                            "Fecha": str(datetime.now().date()), "DNI_Paciente": row['DNI_Paciente'],
                            "Nombre_Paciente": row['Nombre_Paciente'], "Licenciado": lic_sel,
                            "Evaluacion": ev, "Plan_Siguiente": plan
                        }])
                        df_h_act = pd.concat([df_historias, nueva_h], ignore_index=True)
                        update_sheet("Historias", df_h_act)
                        
                        # 2. Actualizar Agenda
                        df_agenda.at[i, 'Estado'] = 'Atendido'
                        update_sheet("Agenda", df_agenda)
                        st.success("Historia Clínica actualizada.")
                        st.rerun()
        else:
            st.info("No tienes pacientes pendientes.")

elif menu == "👤 Expediente del Paciente":
    st.header("📂 Expediente Clínico Digital")
    busq = st.text_input("Buscar Paciente (Nombre o DNI):")
    
    if busq and not df_historias.empty:
        # Filtro de búsqueda
        pax_hist = df_historias[df_historias['Nombre_Paciente'].str.contains(busq, case=False, na=False) | 
                                df_historias['DNI_Paciente'].astype(str).str.contains(busq)]
        
        if not pax_hist.empty:
            st.subheader(f"Historial de Evoluciones")
            # Mostrar como "Línea de Tiempo" invertida
            for _, h in pax_hist.sort_values(by='Fecha', ascending=False).iterrows():
                st.markdown(f"""
                <div style="background: rgba(0, 168, 150, 0.1); padding: 15px; border-radius: 10px; margin-bottom: 10px; border-left: 5px solid #00a896;">
                    <strong>📅 Fecha: {h['Fecha']}</strong> | 🩺 <strong>Licenciado:</strong> {h['Licenciado']}<br>
                    <hr>
                    <p>📝 <strong>Evolución:</strong><br>{h['Evaluacion']}</p>
                    <p>🎯 <strong>Plan Siguiente:</strong><br>{h['Plan_Siguiente']}</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.warning("No se encontraron registros para este paciente.")
