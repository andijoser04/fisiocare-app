import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import os

# 1. CONFIGURACIÓN PROFESIONAL
st.set_page_config(page_title="FISIOCARE - Sistema Integral", layout="wide", page_icon="🏥")

# --- ESTILO VISUAL MODERNO (CSS) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');
    .main { background-color: #f0f4f8; font-family: 'Inter', sans-serif; }
    
    /* Tarjetas de Métricas */
    div[data-testid="stMetric"] {
        background-color: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    
    /* Botones con degradado Fisiocare */
    .stButton>button {
        width: 100%;
        border-radius: 25px !important;
        background: linear-gradient(135deg, #00a896 0%, #028090 100%) !important;
        color: white !important;
        font-weight: bold !important;
        border: none !important;
        height: 3em;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] { background-color: #028090; }
    [data-testid="stSidebar"] * { color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. CONEXIÓN Y FUNCIONES DE DATOS
conn = st.connection("gsheets", type=GSheetsConnection)

def load_sheet(name):
    try:
        df = conn.read(worksheet=name, ttl=0)
        return df.dropna(how='all')
    except:
        return pd.DataFrame()

def save_to_sheet(name, new_df):
    existing = load_sheet(name)
    updated = pd.concat([existing, new_df], ignore_index=True)
    conn.update(worksheet=name, data=updated)
    return True

# 3. INTERFAZ LATERAL
LOGO_PATH = "logo.png"
if os.path.exists(LOGO_PATH):
    st.sidebar.image(LOGO_PATH, width=150)
else:
    st.sidebar.title("🏥 FISIOCARE")

menu = st.sidebar.radio("MENÚ PRINCIPAL", ["🏠 Dashboard", "📅 Recepción y Citas", "🩺 Módulo Licenciados", "👤 Historias Clínicas"])

# --- CARGA DE DATOS REALES PARA TODO EL SISTEMA ---
df_agenda = load_sheet("Agenda")
df_pacientes = load_sheet("Pacientes")
df_precios = load_sheet("Precios")
df_historias = load_sheet("Historias")

# --- MÓDULOS ---

if menu == "🏠 Dashboard":
    st.title("Panel de Control Real - FISIOCARE")
    
    # MÉTRICAS DINÁMICAS (Aquí ya no hay datos falsos, Anderson)
    hoy = str(datetime.now().date())
    citas_hoy = len(df_agenda[df_agenda['Fecha'].astype(str) == hoy]) if not df_agenda.empty else 0
    pacientes_total = len(df_pacientes) if not df_pacientes.empty else 0
    atendidos_hoy = len(df_agenda[(df_agenda['Fecha'].astype(str) == hoy) & (df_agenda['Estado'] == 'Atendido')]) if not df_agenda.empty else 0
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Citas para Hoy", citas_hoy)
    col2.metric("Total Pacientes", pacientes_total)
    col3.metric("Atenciones Listas", atendidos_hoy)
    
    st.markdown("---")
    st.subheader("📋 Vista Rápida de Agenda")
    if not df_agenda.empty:
        st.dataframe(df_agenda, use_container_width=True, hide_index=True)
    else:
        st.info("No hay registros en la Agenda todavía.")

elif menu == "📅 Recepción y Citas":
    st.header("📅 Registro de Citas y Cobros")
    
    with st.expander("➕ Nueva Cita", expanded=True):
        with st.form("form_cita", clear_on_submit=True):
            c1, c2 = st.columns(2)
            f = c1.date_input("Fecha", datetime.now())
            h = c1.selectbox("Hora", ["08:00", "09:00", "10:00", "11:00", "15:00", "16:00", "17:00"])
            
            # Buscador de pacientes existentes
            nombres_p = df_pacientes['Nombre'].tolist() if not df_pacientes.empty else []
            pac_sel = c2.selectbox("Paciente", ["-- NUEVO --"] + nombres_p)
            
            if pac_sel == "-- NUEVO --":
                nom_final = c2.text_input("Nombre Completo")
                dni_final = c2.text_input("DNI")
            else:
                nom_final = pac_sel
                dni_final = df_pacientes[df_pacientes['Nombre'] == pac_sel]['DNI'].values[0]
                c2.info(f"DNI cargado: {dni_final}")

            terapia = c1.selectbox("Plan/Terapia", df_precios['Servicio'].tolist() if not df_precios.empty else ["Evaluación", "Integral", "Convencional"])
            lic = c2.selectbox("Licenciado", ["Lic. Anderson", "Lic. Sofia", "Lic. Ricardo"])
            
            # Cálculo de costo
            costo_final = 0
            if not df_precios.empty and terapia in df_precios['Servicio'].values:
                costo_final = df_precios[df_precios['Servicio'] == terapia]['Precio_Soles'].values[0]
            
            st.markdown(f"### 💰 Monto a cobrar: S/. {costo_final}")
            
            if st.form_submit_button("Agendar y Registrar"):
                # Color (Regla de Oro)
                color = "Amarillo" if "Integral" in terapia else "Rojo" if "Evaluación" in terapia else "Verde"
                
                nueva_fila = pd.DataFrame([{
                    "ID_Cita": datetime.now().strftime("%d%m%H%M"),
                    "Fecha": str(f), "Hora": h, "DNI_Paciente": dni_val if 'dni_val' in locals() else dni_final,
                    "Nombre_Paciente": nom_final, "Tipo_Terapia": terapia, 
                    "Color": color, "Licenciado": lic, "Estado": "Pendiente", "Costo": costo_final
                }])
                
                if save_to_sheet("Agenda", nueva_fila):
                    st.success("✅ Cita guardada. ¡Revisa tu Excel!")
                    st.balloons()
                    st.rerun()

elif menu == "🩺 Módulo Licenciados":
    st.header("🩺 Módulo de Atención Médica")
    lic_filtro = st.selectbox("Licenciado:", ["Lic. Anderson", "Lic. Sofia", "Lic. Ricardo"])
    
    if not df_agenda.empty:
        pendientes = df_agenda[(df_agenda['Licenciado'] == lic_filtro) & (df_agenda['Estado'] == 'Pendiente')]
        
        if not pendientes.empty:
            for i, row in pendientes.iterrows():
                with st.expander(f"Paciente: {row['Nombre_Paciente']} - {row['Hora']}"):
                    ev = st.text_area("Evolución de la sesión", key=f"ev_{i}")
                    plan = st.text_area("Plan para la siguiente sesión", key=f"pl_{i}")
                    
                    if st.button("Finalizar Atención", key=f"btn_{i}"):
                        # 1. Guardar Historia
                        nueva_h = pd.DataFrame([{
                            "Fecha": str(datetime.now().date()), "DNI_Paciente": row['DNI_Paciente'],
                            "Nombre_Paciente": row['Nombre_Paciente'], "Licenciado": lic_filtro,
                            "Evaluacion": ev, "Plan_Siguiente": plan
                        }])
                        save_to_sheet("Historias", nueva_h)
                        
                        # 2. Actualizar Estado en Agenda
                        # Nota: Actualizar una sola celda requiere sobreescribir la pestaña
                        df_agenda.loc[i, 'Estado'] = 'Atendido'
                        conn.update(worksheet="Agenda", data=df_agenda)
                        
                        st.success("Historia Clínica guardada con éxito.")
                        st.rerun()
        else:
            st.info("No tienes citas pendientes para hoy.")

elif menu == "👤 Historias Clínicas":
    st.header("👤 Archivo de Historias Clínicas")
    busqueda = st.text_input("Buscar por Nombre o DNI:")
    
    if busqueda and not df_historias.empty:
        # Filtro real
        resultado = df_historias[df_historias['Nombre_Paciente'].str.contains(busqueda, case=False, na=False) | 
                                 df_historias['DNI_Paciente'].astype(str).str.contains(busqueda)]
        st.dataframe(resultado, use_container_width=True, hide_index=True)
    elif not busqueda:
        st.write("Ingresa un dato para buscar.")
