# 🎛️ Personalización y Adaptaciones

Este agente fue personalizado para cumplir con un flujo de trabajo centrado en el estudio autodirigido. A continuación se describen las principales decisiones de diseño:

## Adaptación al estilo de aprendizaje

Aunque se eliminó el selector de estilos, se mantuvo internamente la posibilidad de adaptar el resumen (visual, auditivo, kinestésico). Esto puede reactivarse fácilmente si se desea reintroducir la funcionalidad.

## Exportación inteligente

El asistente exporta automáticamente todos los resultados generados (resumen, preguntas y respuesta a consulta) en un archivo PDF. Si algún componente no ha sido generado manualmente, se crea automáticamente antes de exportar.

## Indexación semántica

Se implementó una indexación por fragmentos usando ChromaDB y SentenceTransformers para responder preguntas con base en contenido real del documento cargado.

## Portabilidad

Todo está empaquetado en `app.py` y `src/study_agent.py`, con dependencias listadas en `requirements.txt`. Listo para desplegar en local o adaptar para la nube.