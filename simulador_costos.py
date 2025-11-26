
import streamlit as st
import pandas as pd
import plotly.express as px

# =============================
# Funciones de cálculo
# =============================
def calcular_costos(df_tiendas, proveedor, tarifas, tipo_cambio, recargos):
    resultados = []
    for _, row in df_tiendas.iterrows():
        tienda = row['Tienda']
        ubicacion = row['Ubicacion']
        visitas_semana = row['Visitas Semana']
        dias_visita = row['Dias Visita'].split(',')
        dia_entrega = row['Dia Entrega']
        monto_menudo = row['Monto Menudo Semanal']

        # Calcular visitas mensuales (aprox 4 semanas)
        visitas_mes = visitas_semana * 4
        entregas_mes = 4  # una entrega semanal

        costo_recoleccion = 0
        costo_procesamiento = 0
        costo_entrega = 0

        if proveedor == 'BAC':
            tarifa_recoleccion = float(tarifas[(tarifas['Proveedor']=='BAC') & (tarifas['Servicio']=='Recoleccion')][ubicacion].values[0])
            tarifa_entrega = float(tarifas[(tarifas['Proveedor']=='BAC') & (tarifas['Servicio']=='Entrega')][ubicacion].values[0])
            porcentaje_proc = float(tarifas[(tarifas['Proveedor']=='BAC') & (tarifas['Servicio']=='Procesamiento')]['Tarifa'].values[0])

            # Recolección con recargo domingo
            for dia in dias_visita:
                if dia.strip().lower() == 'domingo':
                    costo_recoleccion += tarifa_recoleccion + recargos['BAC']
                else:
                    costo_recoleccion += tarifa_recoleccion
            costo_recoleccion *= 4

            # Procesamiento
            costo_procesamiento = monto_menudo * porcentaje_proc * 4

            # Entrega
            if dia_entrega.lower() == 'domingo':
                costo_entrega = (tarifa_entrega + recargos['BAC']) * entregas_mes
            else:
                costo_entrega = tarifa_entrega * entregas_mes

        elif proveedor == 'SCOTIA':
            tarifa_recoleccion = float(tarifas[(tarifas['Proveedor']=='SCOTIA') & (tarifas['Servicio']=='Recoleccion')][ubicacion].values[0])
            tarifa_entrega = float(tarifas[(tarifas['Proveedor']=='SCOTIA') & (tarifas['Servicio']=='Entrega')][ubicacion].values[0])
            monto_fijo_proc = float(tarifas[(tarifas['Proveedor']=='SCOTIA') & (tarifas['Servicio']=='Procesamiento')]['Tarifa'].values[0])

            # Recolección con recargo domingo
            for dia in dias_visita:
                if dia.strip().lower() == 'domingo':
                    costo_recoleccion += tarifa_recoleccion + recargos['SCOTIA']
                else:
                    costo_recoleccion += tarifa_recoleccion
            costo_recoleccion *= 4

            # Procesamiento
            costo_procesamiento = monto_fijo_proc * 4

            # Entrega
            if dia_entrega.lower() == 'domingo':
                costo_entrega = (tarifa_entrega + recargos['SCOTIA']) * entregas_mes
            else:
                costo_entrega = tarifa_entrega * entregas_mes

        elif proveedor == 'ProvC':
            tarifa_recoleccion_usd = float(tarifas[(tarifas['Proveedor']=='ProvC') & (tarifas['Servicio']=='Recoleccion')]['Tarifa'].values[0])
            tarifa_entrega_usd = float(tarifas[(tarifas['Proveedor']=='ProvC') & (tarifas['Servicio']=='Entrega')]['Tarifa'].values[0])
            tarifa_proc_usd = float(tarifas[(tarifas['Proveedor']=='ProvC') & (tarifas['Servicio']=='Procesamiento')]['Tarifa'].values[0])

            # Recolección con recargo domingo
            for dia in dias_visita:
                if dia.strip().lower() == 'domingo':
                    costo_recoleccion += (tarifa_recoleccion_usd * tipo_cambio) + recargos['ProvC']
                else:
                    costo_recoleccion += tarifa_recoleccion_usd * tipo_cambio
            costo_recoleccion *= 4

            # Procesamiento
            costo_procesamiento = tarifa_proc_usd * tipo_cambio * 4

            # Entrega
            if dia_entrega.lower() == 'domingo':
                costo_entrega = ((tarifa_entrega_usd * tipo_cambio) + recargos['ProvC']) * entregas_mes
            else:
                costo_entrega = (tarifa_entrega_usd * tipo_cambio) * entregas_mes

        costo_total = costo_recoleccion + costo_procesamiento + costo_entrega
        resultados.append({
            'Tienda': tienda,
            'Proveedor': proveedor,
            'Costo Recoleccion': costo_recoleccion,
            'Costo Procesamiento': costo_procesamiento,
            'Costo Entrega': costo_entrega,
            'Costo Total': costo_total
        })
    return pd.DataFrame(resultados)

# =============================
# Interfaz Streamlit
# =============================
st.title('Simulador de Costos - Transporte de Valores')

st.sidebar.header('Parámetros Globales')
tipo_cambio = st.sidebar.number_input('Tipo de Cambio (ProvC)', value=540.0)
recargo_bac = st.sidebar.number_input('Recargo Domingo BAC', value=2000.0)
recargo_scotia = st.sidebar.number_input('Recargo Domingo SCOTIA', value=1500.0)
recargo_provc = st.sidebar.number_input('Recargo Domingo ProvC', value=3.0)
recargos = {'BAC': recargo_bac, 'SCOTIA': recargo_scotia, 'ProvC': recargo_provc}

st.header('Carga de Datos')
file_tiendas = st.file_uploader('Cargar archivo de Tiendas (Excel o CSV)', type=['xlsx','csv'])
file_tarifas = st.file_uploader('Cargar archivo de Tarifas (Excel o CSV)', type=['xlsx','csv'])

if file_tiendas and file_tarifas:
    if file_tiendas.name.endswith('.xlsx'):
        df_tiendas = pd.read_excel(file_tiendas, engine='openpyxl')
    else:
        df_tiendas = pd.read_csv(file_tiendas)

    if file_tarifas.name.endswith('.xlsx'):
        df_tarifas = pd.read_excel(file_tarifas, engine='openpyxl')
    else:
        df_tarifas = pd.read_csv(file_tarifas)

    st.write('Datos de Tiendas:', df_tiendas)
    st.write('Tarifas:', df_tarifas)

    proveedor = st.selectbox('Seleccionar Proveedor', ['BAC','SCOTIA','ProvC'])

    if st.button('Calcular Costos'):
        resultados = calcular_costos(df_tiendas, proveedor, df_tarifas, tipo_cambio, recargos)
        st.write('Resultados:', resultados)

        fig = px.bar(resultados, x='Tienda', y='Costo Total', color='Proveedor', title='Costo Total por Tienda')
        st.plotly_chart(fig)

        # Descargar resultados
        csv = resultados.to_csv(index=False).encode('utf-8')
        st.download_button('Descargar Resultados CSV', csv, 'resultados_costos.csv', 'text/csv')
