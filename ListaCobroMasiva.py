import streamlit as st
import pandas as pd

st.set_page_config(page_title="Estrategia de Cobranza", layout="wide")

# --- Carga de datos principal ---
try:
    df = pd.read_csv('DatosSeleccionada.csv')
except FileNotFoundError:
    st.error("No se encontró 'DatosSeleccionada.csv'. Colócalo en el directorio actual.")
    st.stop()

# --- Mapeo de bancos ---
banco_map = {2: 'Banamex', 14: 'Santander', 12: 'BBVA', 72: 'Banorte'}

# --- Función de estrategia ---
def estrategia_ind(f):
    tipo = f['TipoCliente']
    banco = f.get('idBanco')
    monto = float(f.get('montoExigible', 0) or 0)

    if tipo == 'Tipo01':
        return 'Interbancario Banamex'
    elif tipo == 'Tipo02':
        if banco == 14:
            return 'Interbancario Banamex'
        elif banco == 12 and monto >= 1000:
            return 'BBVA Matutino'
        else:
            return 'Interbancario Banamex'
    elif tipo == 'Tipo03':
        if monto < 300:
            return 'Interbancario Banamex'
        else:
            return 'BBVA Tradicional'
    elif tipo == 'Tipo04':
        return 'Interbancario Banamex'
    else:
        return 'Sin estrategia'

# --- Interfaz principal ---
st.title("Estrategia de Cobranza para Lista de Créditos")
st.write("Sube un archivo CSV con una columna 'idCredito' para obtener la estrategia agrupada.")

upload = st.file_uploader("Archivo CSV con idCredito", type='csv')
if upload:
    ids_df = pd.read_csv(upload)
    if 'idCredito' not in ids_df.columns:
        st.error("El CSV debe contener la columna 'idCredito'.")
    else:
        # Merge con datos principales
        merged = ids_df.merge(df, on='idCredito', how='left')
        # Asignar nuevos clientes
        merged['TipoCliente'] = merged['TipoCliente'].fillna('Tipo01')
        merged['idBanco'] = merged['idBanco'].fillna(0).astype(int)
        merged['montoExigible'] = merged['montoExigible'].fillna(0)
        merged['BancoOrigen'] = merged['idBanco'].map(banco_map).fillna('Otro Banco')
                # Filtrar montos no zero
        merged = merged[merged['montoExigible'] != 0]
        # Calcular estrategia
        merged['Estrategia'] = merged.apply(estrategia_ind, axis=1)

        # Mostrar resumen agrupado
        st.subheader("Resumen de Estrategias")
        resumen = merged['Estrategia'].value_counts().reset_index()
        resumen.columns = ['Estrategia', 'Cantidad']
        st.table(resumen)

        # Mostrar IDs agrupados por estrategia
        st.subheader("IDs Agrupados por Estrategia")
        estrategias = merged['Estrategia'].unique()
        for estr in estrategias:
            with st.expander(f"{estr} ({merged[merged['Estrategia']==estr].shape[0]} créditos)"):
                ids = merged.loc[merged['Estrategia']==estr, 'idCredito'].tolist()
                st.write(ids)

        # Mostrar detalle
        st.subheader("Detalle por Crédito")
        st.dataframe(merged[['idCredito', 'TipoCliente', 'BancoOrigen', 'montoExigible', 'Estrategia']])
else:
    st.info("Por favor, sube tu archivo CSV con los idCredito.")

