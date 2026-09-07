# Uso de la IA durante el desarrollo

CloudOps AI es tanto un portfolio como un proyecto de aprendizaje. Durante su desarrollo, he utilizado asistentes de IA como apoyo para comprender conceptos, comparar alternativas y revisar el trabajo realizado.

La IA ha actuado principalmente como tutor y compañero de revisión. Las decisiones sobre el alcance, la arquitectura y las tecnologías se han tomado teniendo en cuenta los objetivos del proyecto: profundizar en prácticas relacionadas con AI Engineering y MLOps, construir una aplicación funcional y crear un portfolio técnicamente defendible.

## Forma de trabajo

El proyecto se ha desarrollado de manera incremental, dividiendo el trabajo en sprints, issues y cambios pequeños.

El proceso habitual ha sido:

1. Definir el objetivo y las restricciones de cada tarea.
2. Utilizar la IA para entender los conceptos necesarios y valorar posibles soluciones.
3. Elegir una alternativa y realizar personalmente los cambios.
4. Revisar el resultado mediante pruebas, herramientas de calidad y ejecución manual.
5. Corregir los problemas encontrados antes de abrir una Pull Request.
6. Validar los cambios mediante CI y realizar el merge de forma consciente.

Valoré utilizar modos agénticos o generadores capaces de modificar el código de forma autónoma, pero decidí no delegar la implementación. El proyecto nació con el objetivo de asentar los conocimientos adquiridos, comprender cada cambio y mantener el control sobre el código incorporado.

Este proceso me ha permitido utilizar la IA como herramienta de aprendizaje sin delegar en ella la responsabilidad sobre el resultado final.

## Áreas en las que se ha utilizado

Los asistentes de IA se han utilizado para:

- Ayudar en la narración de PR e issues. El uso de IA me ha aportado ayuda para estructurar la información y mantener una narrativa consistente en cada caso.
- Debatir y profundizar en conceptos relacionados con LangGraph, Qdrant, Docker, observabilidad, Terraform, Azure y CI/CD.
- Ayudar a dividir funcionalidades grandes en tareas más pequeñas.
- Comparar alternativas arquitectónicas y analizar sus ventajas e inconvenientes.
- Soporte para interpretar errores, logs, planes de Terraform y resultados de workflows.
- Diseñar tests unitarios.
- Revisar la claridad y precisión de la documentación.
- Traducir el README del castellano al inglés.

La versión inglesa del README indica expresamente que su traducción se realizó con ayuda de IA.

## Interfaz web

La implementación de la interfaz web en HTML, CSS y JavaScript ha sido generada con IA a partir de mis directrices. He definido su alcance, comportamiento e integración con la API, y he comprobado manualmente su funcionamiento.

Esta decisión responde al enfoque del proyecto: CloudOps AI está orientado al desarrollo de sistemas de IA, backend, infraestructura, CI/CD y observabilidad. La interfaz cumple la función necesaria para utilizar y demostrar la aplicación, pero no pretende acreditar competencias especializadas en desarrollo frontend.

## Validación de los resultados

Las respuestas generadas por la IA se consideran propuestas y pueden contener errores o suposiciones incorrectas. Por este motivo, los cambios no se aceptan únicamente porque hayan sido sugeridos por un asistente.

Antes de realizar un cambio, busco comprender el concepto, su finalidad y cómo encaja en la arquitectura del proyecto. A partir de ahí, tomo la decisión e implemento personalmente el código o la configuración correspondiente. La IA se utiliza como apoyo para resolver dudas, revisar el razonamiento o ayudar a investigar los errores que aparecen durante el proceso.

Cada cambio sigue el flujo de validación habitual del proyecto. Dependiendo de su naturaleza, ejecuto pruebas unitarias, Ruff, Docker Compose, validaciones y planes de Terraform, GitHub Actions o comprobaciones manuales. Un cambio se considera terminado cuando entiendo su funcionamiento y he comprobado que se comporta como esperaba.

## Responsabilidad y límites

La IA puede ayudar a proponer y analizar una solución, pero la responsabilidad sobre las decisiones, los cambios realizados y su validación sigue siendo mía.

El objetivo de utilizarla de esta manera no es sustituir el aprendizaje, sino acelerar el proceso de investigación, recibir explicaciones adaptadas al contexto del proyecto y detectar aspectos que necesitan una revisión más profunda.