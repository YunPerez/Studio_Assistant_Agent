# Arquitectura del Asistente

- **data_processing**: extracción y limpieza.
- **question_generator**: llama a OpenAI para generar preguntas.
- **summarizer**: resúmenes en distintos estilos.
- **user_model**: perfil y preferencias.
- **agent**: orquestador de flujo (ingest, preguntas, resumen, adaptación).
- **main**: interfaz Streamlit.