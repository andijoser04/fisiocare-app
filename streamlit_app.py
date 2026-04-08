import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import os

# 1. CONFIGURACIÓN DE ALTA GAMA
st.set_page_config(page_title="FISIOCARE - Portal Médico", layout="wide", page_icon="🏥")

# --- CSS PROFESIONAL (Estilo Antares/Moderno) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');
    
    .main { background-color: #f0f4f8; font-family: 'Inter', sans-serif; }
    
    /* Estilo de Tarjetas (Cards) */
    .stApp div[data-testid="stVerticalBlock"] > div {
        background-color: white;
        padding: 10px;
        border-radius: 15px;
    }
    
    /* Botones con degradado Fisiocare */
    .stButton>button {
        width: 100%;
        border-radius: 25px !important;
        background: linear-gradient(135deg, #00a896 0%, #028090 100%) !important;
        color: white !important;
        font-weight: bold !important;
        border: none !important;
        transition: 0.3s all;
    }
    .stButton>button:hover { transform: translateY(-2px); box-shadow: 0 5px 15px rgba(0,168,150,0.3); }

    /* Sidebar */
    [data-testid="stSidebar"] { background-color: #028090; }
    [data-testid="stSidebar"] * { color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. CONEXIÓN Y FUNCIONES DE DATOS
conn = st.connection("gsheets", type=GSheetsConnection)

def load_sheet(name):
    try: return conn.read(worksheet=name, ttl=0).dropna(how='all')
    except: return pd.DataFrame()

def save_sheet(name, df):
    conn.update(worksheet=name, data=df)

# 3. SIDEBAR Y LOGO
LOGO_PATH = "logo.png"
if os.path.exists(LOGO_PATH):
    st.sidebar.image(LOGO_PATH, width=150)
else:
    st.sidebar.title("🏥 FISIOCARE")

menu = st.sidebar.radio("MENÚ PRINCIPAL", ["🏠 Dashboard", "📅 Recepción", "🩺 Módulo Licenciados", "👤 Historial Clínico"])

# --- MÓDULOS ---

if menu == "🏠 Dashboard":
    st.title("Atención de Excelencia FISIOCARE")
    st.markdown("##### Gestión Integral para una Recuperación Sostenible")
    
    df_agenda = load_sheet("Agenda")
    c1, c2, c3 = st.columns(3)
    with c1: st.metric("Citas Hoy", len(df_agenda[df_agenda['Estado'] == 'Pendiente']) if not df_agenda.empty else 0)
    with c2: st.metric("Terapeutas", "3 Activos")
    with c3: st.metric("Pacientes Mes", "+12")
    
    st.markdown("---")
    st.subheader("📌 Resumen de Agenda")
    st.dataframe(df_agenda, use_container_width=True, hide_index=True)

elif menu == "📅 Recepción":
    st.header("📅 Gestión de Citas y Cobros")
    df_precios = load_sheet("Precios")
    df_pacientes = load_sheet("Pacientes")
    
    with st.expander("➕ Registrar Cita y Cobro", expanded=True):
        with st.form("registro_cita"):
            col1, col2 = st.columns(2)
            fecha = col1.date_input("Fecha")
            hora = col1.selectbox("Hora", ["08:00", "09:00", "10:00", "11:00", "15:00", "16:00", "17:00"])
            
            # Buscador de paciente por nombre (si existe en la base de datos)
            lista_pacientes = df_pacientes['Nombre'].tolist() if not df_pacientes.empty else []
            pac_nom = col2.selectbox("Paciente", ["Nuevo Paciente"] + lista_pacientes)
            
            dni_val = ""
            if pac_nom == "Nuevo Paciente":
                pac_nom = col2.text_input("Nombre Completo")
                dni_val = col2.text_input("DNI")
            else:
                dni_val = df_pacientes[df_pacientes['Nombre'] == pac_nom]['DNI'].values[0]
                col2.info(f"DNI: {dni_val}")

            terapia = col1.selectbox("Tipo de Terapia", df_precios['Servicio'].tolist() if not df_precios.empty else ["Evaluación"])
            licenciado = col2.selectbox("Asignar a:", ["Lic. Anderson", "Lic. Sofia", "Lic. Ricardo"])
            
            # Cálculo de costo automático
            costo = 0
            if not df_precios.empty:
                costo = df_precios[df_precios['Servicio'] == terapia]['Precio_Soles'].values[0]
            
            st.markdown(f"### 💰 Monto a cobrar: **S/. {costo}**")
            
            if st.form_submit_button("Confirmar y Cobrar"):
                # Color según terapia (Regla de Oro)
                color = "Amarillo" if "Integral" in terapia else "Rojo" if "Evaluación" in terapia else "Verde"
                
                nueva_cita = pd.DataFrame([{
                    "ID_Cita": datetime.now().strftime("%H%M%S"),
                    "Fecha": str(fecha), "Hora": hora, "DNI_Paciente": dni_val,
                    "Nombre_Paciente": pac_nom, "Terapia": terapia, "Licenciado": licenciado,
                    "Estado": "Pendiente", "Costo": costo, "Color": color
                }])
                
                # Guardamos y lanzamos animación
                df_act = pd.concat([load_sheet("Agenda"), nueva_cita], ignore_index=True)
                save_sheet("Agenda", df_act)
                st.balloons()
                st.success(f"✅ Cita registrada. Cobro de S/. {costo} confirmado.")

elif menu == "🩺 Módulo Licenciados":
    st.header("🩺 Área de Tratamiento")
    lic_login = st.selectbox("Identifíquese Licenciado:", ["Lic. Anderson", "Lic. Sofia", "Lic. Ricardo"])
    
    df_agenda = load_sheet("Agenda")
    if not df_agenda.empty:
        mis_citas = df_agenda[(df_agenda['Licenciado'] == lic_login) & (df_agenda['Estado'] == "Pendiente")]
        
        if not mis_citas.empty:
            for i, row in mis_citas.iterrows():
                with st.expander(f"Atender a: {row['Nombre_Paciente']} - {row['Hora']}"):
                    st.write(f"**Terapia:** {row['Terapia']}")
                    eval_texto = st.text_area("Evaluación / Evolución del paciente", key=f"ev_{i}")
                    plan_texto = st.text_area("Plan para la próxima sesión", key=f"pl_{i}")
                    
                    if st.button("Finalizar y Guardar Historia", key=f"btn_{i}"):
                        # 1. Guardar Historia
                        nueva_h = pd.DataFrame([{
                            "Fecha": str(datetime.now().date()), "DNI_Paciente": row['DNI_Paciente'],
                            "Nombre_Paciente": row['Nombre_Paciente'], "Licenciado": lic_login,
                            "Evaluacion": eval_texto, "Plan_Siguiente": plan_texto
                        }])
                        df_h_act = pd.concat([load_sheet("Historias"), nueva_h], ignore_index=True)
                        save_sheet("Historias", df_h_act)
                        
                        # 2. Marcar como Atendido en Agenda
                        df_agenda.at[i, 'Estado'] = "Atendido"
                        save_sheet("Agenda", df_agenda)
                        
                        st.success("✅ Historia guardada. ¡Buen trabajo!")
                        st.rerun()
        else:
            st.info("No tienes pacientes pendientes por ahora.")

elif menu == "👤 Historial Clínico":
    st.header("👤 Buscador de Historias Clínicas")
    df_h = load_sheet("Historias")
    busqueda = st.text_input("Buscar por Nombre o DNI:")
    
    if busqueda and not df_h.empty:
        res = df_h[df_h['Nombre_Paciente'].str.contains(busqueda, case=False) | df_h['DNI_Paciente'].astype(str).str.contains(busqueda)]
        st.dataframe(res, use_container_width=True, hide_index=True)
