import streamlit as st
import pandas as pd

st.set_page_config(page_title="Estrategia de Cobranza", layout="wide")

# --- Carga de datos ---
# Se asume que el archivo 'DatosSeleccionada.csv' está en el mismo directorio
try:
    df = pd.read_csv('DatosSeleccionada.csv')
except FileNotFoundError:
    st.error("No se encontró el archivo 'DatosSeleccionada.csv'. Asegúrate de que esté en el directorio actual.")
    st.stop()

# --- Mapeo de bancos ---
# Claves según tabla: 2=Banamex, 14=Santander, 12=BBVA, 72=Banorte; otros = 'Otro Banco'
banco_map = {
    2: 'Banamex',
    14: 'Santander',
    12: 'BBVA',
    72: 'Banorte'
}

# --- Interfaz de consulta ---
st.title("Consulta de Tipo de Cliente y Estrategia de Cobro")
st.write("Ingresa el idCredito para obtener su clasificación y la estrategia recomendada.")

id_input = st.text_input("idCredito:")

if id_input:
    # Convertir a número si es dígito
    id_val = int(id_input) if id_input.isdigit() else id_input

    # Buscar en DataFrame
    if id_val in df['idCredito'].values:
        row = df[df['idCredito'] == id_val].iloc[0].to_dict()
    else:
        # Nuevo cliente: Tipo01 con monto 0
        row = {
            'idCredito': id_val,
            'idBanco': None,
            'montoExigible': 0.0,
            'TipoCliente': 'Tipo01'
        }

    # Banco de origen
    banco_id = row.get('idBanco')
    banco_nombre = banco_map.get(banco_id, 'Otro Banco') if banco_id is not None else 'Nuevo Cliente'

    # Definir estrategia de cobro
    def estrategia_ind(f):
        tipo = f['TipoCliente']
        banco = f.get('idBanco')
        monto = float(f.get('montoExigible', 0) or 0)

        # Tipo01: siempre interbancario Banamex
        if tipo == 'Tipo01':
            return {'canal': 'Interbancario Banamex', 'comision': 1.75, 'detalle': 'Ruta más económica para clientes nuevos'}

        # Tipo02: 1–5 intentos
        if tipo == 'Tipo02':
            base = {'canal': 'Interbancario Banamex', 'comision': 1.75, 'detalle': 'Ruta estándar'}
            if banco == 14:  # Santander
                return base
            if banco == 12:  # BBVA
                if monto >= 1000:
                    return {'canal': 'BBVA Matutino', 'comision': 8.0, 'detalle': 'Solo cobra si éxito (85% éxito)'}
                else:
                    return base
            return base

        # Tipo03: ≥6 intentos sin pago
        if tipo == 'Tipo03':
            if monto < 300:
                return {'canal': 'Interbancario Banamex', 'comision': 1.75, 'detalle': 'Suspender tras 5 intentos (monto bajo)'}
            return {'canal': 'BBVA Tradicional', 'comision': 8.0, 'detalle': 'Hasta 5 intentos matutinos sin cobro por fallo'}

        # Tipo04: ≥6 intentos con pago
        if tipo == 'Tipo04':
            return {'canal': 'Interbancario Banamex', 'comision': 1.75, 'detalle': 'Cliente valioso - ofrecer incentivos'}

        # Caso por defecto
        return {'canal': 'N/A', 'comision': 0.0, 'detalle': 'Sin estrategia definida'}

    estr = estrategia_ind(row)

    # Mostrar resultados
    st.subheader(f"Detalle para idCredito {row['idCredito']}")
    st.markdown(f"""
- **TipoCliente:** {row['TipoCliente']}
- **Banco Origen:** {banco_nombre}
- **Monto Exigible:** {row.get('montoExigible', 0):.2f} MXN
""", unsafe_allow_html=True)

    st.markdown("**Estrategia de Cobro**", unsafe_allow_html=True)
    st.markdown(f"""
- Canal: {estr['canal']}
- Comisión: {estr['comision']} MXN
- Detalle: {estr['detalle']}
""", unsafe_allow_html=True)
else:
    st.info("Ingrese un idCredito para consultar su clasificación y estrategia.")

