import streamlit as st
import numpy as np
import pandas as pd
from PIL import Image
import matplotlib.pyplot as plt
import gspread
import pygsheets


# Función para calcular los pesos a partir de la matriz de comparación
def calcular_pesos(matriz):
    cant = matriz.shape[0]
    productos = np.prod(matriz, axis=1)
    raices = productos ** (1 / cant)
    pesos = raices / raices.sum()
    return pesos

# Función principal de la app de Streamlit
def app():
    #  Imágenes
    logoUPME = Image.open('img/UPME.png')
    logoUdeA = Image.open('img/UdeA.png')

    # Layout imágenes
    col1, col2 = st.columns([1, 1])
    with col1:
        st.image(logoUPME)
    with col2:
        st.image(logoUdeA)
    
    # HTML para título y subtítulos
    st.markdown("""
    <h1 style='text-align: center; font-size: 36px;'>Modelo de Conflictividad Socio-Ambiental</h1>
    <h3 style='text-align: center; font-size: 30px;'>Ponderación de Variables <br> Analytic Hierarchy Process - AHP</h3>
    """, unsafe_allow_html=True)

    # Captura del Nombre del Usuario
    nombreUsuario = st.text_input("Ingrese su Nombre, Perfil o Correo Electrónico")
    st.session_state['nombreUsuario'] = nombreUsuario

    # Captura del Nombre del Fenómeno o Aspecto sobre el quiere ponderar las variables
    nombreFenomeno = st.text_input("Nombre del Fenómeno o Aspecto, Objeto de Análisis:")
    st.session_state['nombreFenomeno'] = nombreFenomeno

    # Captura número de criterios
    cant = st.number_input("¿CUÁNTOS CRITERIOS DESEA EVALUAR?", min_value=2, max_value=15, step=1)

    # Si se ha establecido un número de criterios, solicitar sus nombres
    if cant > 0:
        criterios = [st.text_input(f"Nombre del criterio {i+1}:", key=f"criterio_{i}") for i in range(cant)]
    
    if all(criterios):
        # Crear una matriz de comparación
        matriz = np.ones((cant, cant))
        
        with st.form("matriz_comparacion"):
            st.subheader("Matriz de Comparación")
            # Crear campos de entrada para comparaciones
            opciones = [
                ("Igualmente importante", 1),
                ("Ligeramente más importante", 3),
                ("Bastante más importante", 5),
                ("Considerablemente más importante", 7),
                ("Absolutamente más importante", 9),
            ]
            for i in range(cant):
                for j in range(i+1, cant):
                    # Usar un selectbox con texto en lugar de números
                    opcion = st.selectbox(f"Cómo definirías la comparación entre {criterios[i]} y {criterios[j]}:", 
                                          options=[o[0] for o in opciones], 
                                          format_func=lambda x: x,
                                          key=f"select_{i}_{j}")
                    # Encontrar el valor numérico correspondiente a la opción de texto
                    valor = next(val for text, val in opciones if text == opcion)
                    matriz[i, j] = valor
                    matriz[j, i] = 1 / valor
            
            # Botón de envío
            submitted = st.form_submit_button("Calcular pesos")
            if submitted:
                # Calcular pesos
                pesos = calcular_pesos(matriz)
                # Mostrar pesos en formato de porcentaje
                st.subheader("Pesos calculados:")
                st.session_state['pesos_porcentaje'] = pd.Series(pesos * 100, index=criterios)
                st.dataframe(st.session_state['pesos_porcentaje'].to_frame(name="Peso (%)"))

            
                # Crear un gráfico de torta para los pesos
                # Aquí ajustamos el tamaño de la figura a un 75% del tamaño original
                fig, ax = plt.subplots(figsize=(6,4))
                ax.pie(pesos, labels=criterios, autopct='%1.1f%%', startangle=90)
                ax.axis('equal')  # Igual aspect ratio asegura que se dibuje el pie como un círculo.
                
                # Mostrar el gráfico de torta
                st.pyplot(fig)

                st.markdown("""
                    <style>
                    .impresion {
                        font-size: 10pt;
                        color: gray;
                        text-align: center;
                        font-style: italic;
                    }
                    </style>
                    <p class="impresion">Para garantizar la reproducibilidad de este modelo de ponderación, recomendamos obtener una copia de este informe utilizando la función de impresión del navegador.<br>
                        Presione 'CTRL + P' en Windows o 'CMD + P' en Mac para abrir la ventana de impresión.                
                    </p>
                    """, unsafe_allow_html=True)
            


        # Botón para guardar los datos en Google Sheets
        btnGuardar = st.button("Guardar Resultados")
        if btnGuardar and 'pesos_porcentaje' in st.session_state:
            try:
                # Autenticación con Google Sheets usando Streamlit secrets
                gc = gspread.service_account_from_dict(st.secrets["gcp_service_account"])

                # Acceder a la hoja de cálculo por su ID
                sh = gc.open_by_key("1zNXnSOc2qWxDpOo8kpEGsF2zDNC5yyZF80FnfzbQzyk")
                worksheet = sh.get_worksheet(0)  # Accede a la primera hoja por índice

                # Preparar los datos para insertar
                datos = [st.session_state['nombreUsuario'], st.session_state['nombreFenomeno']] + \
                    [item for pair in zip(criterios, st.session_state['pesos_porcentaje']) for item in pair]

                # Insertar la fila de datos en la hoja
                response = worksheet.append_row(datos)
                st.success("Datos guardados con éxito. Respuesta: {}".format(response))
            except gspread.exceptions.APIError as e:
                st.error("Error de la API de Google Sheets: {}".format(e))
            except Exception as e:
                st.error("Error al guardar datos: {}".format(e))



if __name__ == "__main__":
    app()


       # Creditos del Pie de página
    st.markdown("""
        <style>
        .credits {
            font-size: 10pt;
            color: gray;
            text-align: right;
        }
        </style>
        <p class="credits">Developed by: Julián Darío Giraldo Ocampo | ingenieria@juliangiraldo.co</p>
        """, unsafe_allow_html=True)