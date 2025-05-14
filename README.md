# Proyecto: Asistente de Estudio Personalizado

Un agente de IA que ayuda al usuario generando preguntas, resúmenes y explicaciones basadas en materiales de estudio.

# Descripción

Este repositorio contiene un agente de IA en Python que ayuda al usuario a estudiar generando preguntas, resúmenes y explicaciones adaptadas a su estilo de aprendizaje.

## Estructura del repositorio
```text
personalized-study-assistant/
├── README.md
├── requirements.txt
├── .env.example
├── src/
│   ├── main.py
│   ├── config.py
│   ├── data_processing.py
│   ├── question_generator.py
│   ├── summarizer.py
│   ├── user_model.py
│   ├── progress_tracker.py
│   ├── agent.py
│   └── utils.py
├── tests/
│   ├── test_data_processing.py
│   ├── test_question_generator.py
│   ├── test_summarizer.py
│   ├── test_user_model.py
│   └── test_agent.py
└── docs/
    ├── architecture.md
    └── personalization.md
```

## Características
- Procesamiento de documentos (PDF, texto plano).
- Generación automática de preguntas relevantes.
- Resúmenes personalizados (short, long).
- Adaptación al perfil del estudiante (visual, auditivo, kinestésico).
- Seguimiento de progreso y métricas de efectividad.

## Instalación
```bash
git clone https://github.com/tu_usuario/personalized-study-assistant.git
cd personalized-study-assistant
python -m venv venv
source venv/bin/activate  # o venv\\Scripts\\activate en Windows
pip install -r requirements.txt
cp .env.example .env && edit .env
```

## Uso
```bash
streamlit run src/main.py
```

## Estructura
Consulta `docs/architecture.md` para detalles de diseño y `docs/personalization.md` para la lógica de adaptación.
```