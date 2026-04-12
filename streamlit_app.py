import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import os
import base64

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="FISIOCARE - Portal Médico Premium", layout="wide", page_icon="🏥")

# --- RECURSOS (URL DEL EXCEL) ---
SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/1RYsepIDKxV0hOl5FWIymAZOwSwjeLSHUxWKOScrJkaU"

# --- VIDEO DE FONDO Y ESTILOS BLINDADOS ---
def get_base64(bin_file):
    with open(bin_file, 'rb') as f:
        return base64.b64encode(f.read()).decode()

video_file = "videobackground.mp4"
if os.path.exists(video_file):
    bin_str = get_base64(video_file)
    st.markdown(f"""
        <style>
        /* 1. Volver transparente la raíz absoluta de Streamlit */
        .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"], .main {{ 
            background: transparent !important; 
            background-color: transparent !important;
        }}
        [data-testid="stHeader"] {{ height: 0px !important; }}
        
        /* 2. El Panel Izquierdo (Sidebar) de Cristal */
        [data-testid="stSidebar"] {{
            background-color: rgba(2, 128, 144, 0.3) !important;
            backdrop-filter: blur(12px) !important;
            border-right: 1px solid rgba(255, 255, 255, 0.2);
        }}
        [data-testid="stSidebar"] * {{ 
            color: white !important; 
            text-shadow: 2px 2px 4px #000; 
            font-weight: 600; 
        }}

        /* 3. Contenedor Fijo del Video (Capa -1, no -9999) */
        #video-container {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            z-index: -1; 
        }}
        
        #bgVideo {{ 
            width: 100%; 
            height: 100%; 
            object-fit: cover; 
            opacity: 0.5; /* Subí un poco la intensidad para que se note más */
        }}
        </style>
        
        <div id="video-container">
            <video autoplay muted loop id="bgVideo" playsinline>
                <source src="data:video/mp4;base64,{bin_str}" type="video/mp4">
            </video>
        </div>
    """, unsafe_allow_html=True)
else:
    st.warning("⚠️ No se encontró el video 'videobackground.mp4'. Verifica el nombre en GitHub.")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');
    
    /* Diseño de las Tarjetas de Contenido */
    .stApp div[data-testid="stVerticalBlock"] > div {
        background-color: rgba(255, 255, 255, 0.88) !important;
        padding: 25px; 
        border-radius: 20px; 
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
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
    .stButton>button:hover { transform: scale(1.02); }
    </style>
""", unsafe_allow_html=True)

# 2. MOTOR DE DATOS
conn = st.connection("gsheets", type=GSheetsConnection)

def load_sheet(name):
    try: return conn.read(worksheet=name, ttl=0).dropna(how='all')
    except: return pd.DataFrame()

def save_sheet(name, df):
    try:
        conn.update(worksheet=name, data=df, spreadsheet=SPREADSHEET_URL)
        return True
    except Exception as e:
        st.error(f"❌ Error al guardar en {name}. Verifica permisos de Editor.")
        return False

# 3. INTERFAZ
LOGO = "logo.png"
if os.path.exists(LOGO): st.sidebar.image(LOGO, width=150)
else: st.sidebar.title("🏥 FISIOCARE")

menu = st.sidebar.radio("SISTEMA FISIOCARE", ["🏠 Dashboard", "📅 Recepción y Agenda", "🩺 Módulo Licenciados", "👤 Expedientes Clínicos"])

# Carga de datos
df_agenda = load_sheet("Agenda")
df_pacientes = load_sheet("Pacientes")
df_precios = load_sheet("Precios")
df_historias = load_sheet("Historias")

# Variables de control
licenciados = ["Lic. Paul", "Lic. Andrea", "Lic. Diana", "Lic. Sofia"]
horas = [f"{h:02d}:00" for h in range(8, 20) if h != 13 and h != 14] # Bloques de 8am a 7pm (sin almuerzo)

# --- MÓDULOS ---

if menu == "🏠 Dashboard":
    st.title(f"Gestión Integral FISIOCARE")
    hoy = datetime.now().strftime('%Y-%m-%d')
    
    c_hoy = len(df_agenda[df_agenda['Fecha'].astype(str) == hoy]) if not df_agenda.empty else 0
    p_tot = len(df_pacientes) if not df_pacientes.empty else 0
    at_hoy = len(df_agenda[(df_agenda['Fecha'].astype(str) == hoy) & (df_agenda['Estado'] == 'Atendido')]) if not df_agenda.empty else 0
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Citas de Hoy", c_hoy)
    col2.metric("Atenciones Listas", at_hoy)
    col3.metric("Base de Pacientes", p_tot)
    
    st.markdown("---")
    st.subheader("📋 Agenda Próxima")
    if not df_agenda.empty:
        st.dataframe(df_agenda.sort_values(by=['Fecha', 'Hora'], ascending=[False, True]), use_container_width=True, hide_index=True)
    else:
        st.info("No hay datos registrados aún.")

elif menu == "📅 Recepción y Agenda":
    st.header("📅 Recepción y Control de Horarios")
    t1, t2, t3 = st.tabs(["📊 Cuadrícula Horaria", "📝 Nueva Cita", "🗑️ Gestionar Agenda"])
    
    with t1:
        st.subheader("Disponibilidad por Licenciado")
        fecha_q = st.date_input("Ver día:", datetime.now())
        f_str = str(fecha_q)
        # Crear cuadrícula como tu Excel
        grid = pd.DataFrame(index=horas, columns=licenciados).fillna("")
        if not df_agenda.empty:
            hoy_data = df_agenda[df_agenda['Fecha'].astype(str) == f_str]
            for _, r in hoy_data.iterrows():
                if r['Hora'] in horas and r['Licenciado'] in licenciados:
                    grid.at[r['Hora'], r['Licenciado']] = f"👤 {r['Nombre_Paciente']}"
        st.table(grid)

    with t2:
        with st.form("form_reg", clear_on_submit=True):
            c1, c2 = st.columns(2)
            f = c1.date_input("Fecha")
            h = c1.selectbox("Hora", horas)
            lic = c2.selectbox("Licenciado", licenciados)
            
            p_list = df_pacientes['Nombre'].tolist() if not df_pacientes.empty else []
            p_sel = c2.selectbox("Paciente", ["-- NUEVO --"] + p_list)
            
            if p_sel == "-- NUEVO --":
                nom = c2.text_input("Nombre Completo")
                dni = c2.text_input("DNI (Importante para historial)")
            else:
                nom = p_sel
                dni = df_pacientes[df_pacientes['Nombre'] == p_sel]['DNI'].values[0]
            
            ter = c1.selectbox("Terapia", df_precios['Servicio'].tolist() if not df_precios.empty else ["Evaluación", "Integral"])
            
            if st.form_submit_button("Agendar Cita"):
                costo = df_precios[df_precios['Servicio'] == ter]['Precio_Soles'].values[0] if not df_precios.empty else 0
                nueva_c = pd.DataFrame([{
                    "ID": datetime.now().strftime("%d%m%H%M%S"), "Fecha": str(f), "Hora": h, 
                    "DNI": str(dni), "Nombre_Paciente": nom, "Terapia": ter, 
                    "Licenciado": lic, "Estado": "Pendiente", "Costo": costo
                }])
                if p_sel == "-- NUEVO --":
                    new_p = pd.DataFrame([{"DNI": str(dni), "Nombre": nom, "Celular": "", "Diagnostico": ""}])
                    save_sheet("Pacientes", pd.concat([df_pacientes, new_p]))
                
                if save_sheet("Agenda", pd.concat([df_agenda, nueva_c])):
                    st.success("✅ Cita agendada.")
                    st.rerun()

    with t3:
        if not df_agenda.empty:
            for i, r in df_agenda.iterrows():
                col_i, col_b = st.columns([5,1])
                col_i.write(f"**{r['Fecha']} {r['Hora']}** | {r['Nombre_Paciente']} ({r['Licenciado']})")
                if col_b.button("Borrar 🗑️", key=f"del_{i}"):
                    df_upd = df_agenda.drop(i)
                    if save_sheet("Agenda", df_upd):
                        st.warning("Cita eliminada.")
                        st.rerun()

elif menu == "🩺 Módulo Licenciados":
    st.header("🩺 Atención Médica")
    doc = st.selectbox("Licenciado:", licenciados)
    
    if not df_agenda.empty:
        pendientes = df_agenda[(df_agenda['Licenciado'] == doc) & (df_agenda['Estado'] == 'Pendiente')]
        
        if not pendientes.empty:
            for i, r in pendientes.iterrows():
                with st.expander(f"Atender a: {r['Nombre_Paciente']} ({r['Hora']})"):
                    ev = st.text_area("Evolución de la sesión", key=f"ev_{i}")
                    pl = st.text_area("Plan siguiente", key=f"pl_{i}")
                    if st.button("Finalizar Atención", key=f"f_{i}"):
                        hist = pd.DataFrame([{
                            "Fecha": str(datetime.now().date()), "DNI": str(r['DNI']), 
                            "Nombre": r['Nombre_Paciente'], "Licenciado": doc, "Evolucion": ev, "Plan": pl
                        }])
                        if save_sheet("Historias", pd.concat([df_historias, hist])):
                            df_agenda.at[i, 'Estado'] = 'Atendido'
                            save_sheet("Agenda", df_agenda)
                            st.success("✅ Evolución guardada en el expediente.")
                            st.rerun()
        else: st.info("No hay pacientes pendientes.")
    else: st.info("Agenda vacía.")

elif menu == "👤 Expedientes Clínicos":
    st.header("📂 Expediente Digital")
    busq = st.text_input("Buscar por Nombre o DNI:")
    if busq and not df_historias.empty:
        res = df_historias[df_historias['Nombre'].str.contains(busq, case=False, na=False) | 
                           df_historias['DNI'].astype(str).str.contains(busq)]
        if not res.empty:
            for _, h in res.sort_values(by='Fecha', ascending=False).iterrows():
                st.markdown(f"""
                <div style="background: rgba(0, 168, 150, 0.1); padding: 15px; border-radius: 12px; margin-bottom: 15px; border-left: 6px solid #00a896;">
                    <strong>📅 Fecha: {h['Fecha']}</strong> | 🩺 <strong>Licenciado:</strong> {h['Licenciado']}<br>
                    <hr style="border: 0.5px solid #ccc;">
                    <p>📝 <strong>Evolución:</strong><br>{h['Evolucion']}</p>
                    <p>🎯 <strong>Plan Siguiente:</strong><br>{h['Plan']}</p>
                </div>
                """, unsafe_allow_html=True)
        else: st.warning("No hay historias para este paciente.")
