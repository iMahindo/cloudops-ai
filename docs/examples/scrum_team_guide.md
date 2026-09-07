# Guía de trabajo Scrum del equipo CloudOps AI

## Objetivo

Esta guía define cómo trabaja el equipo de producto y operaciones de CloudOps AI. Su objetivo es mantener prioridades claras, entregar valor con frecuencia y evitar que el trabajo urgente desorganice los sprints.

## Duración del sprint

Los sprints duran dos semanas y comienzan los lunes a las 10:00.

Un sprint termina el segundo viernes a las 16:00. Después de la Sprint Review se celebra la retrospectiva y se prepara el siguiente ciclo.

No se modifica la duración de un sprint aunque existan festivos o ausencias. El equipo adapta la cantidad de trabajo durante la planificación.

## Roles

### Product Owner

El Product Owner decide las prioridades del Product Backlog, aclara los objetivos de negocio y acepta o rechaza el trabajo terminado.

También debe asegurar que las historias tengan suficiente información antes de entrar en un sprint.

### Scrum Master

El Scrum Master facilita las ceremonias, elimina impedimentos y ayuda al equipo a mejorar su forma de trabajo.

No asigna tareas ni decide las prioridades del producto.

### Equipo de desarrollo

El equipo decide cómo realizar el trabajo y comparte la responsabilidad de cumplir el Sprint Goal.

Las tareas no pertenecen exclusivamente a una persona. Cualquier miembro puede colaborar cuando exista un bloqueo o riesgo para el sprint.

## Sprint Planning

La Sprint Planning se celebra el primer lunes del sprint y tiene una duración máxima de dos horas.

Durante la sesión:

1. El Product Owner explica el objetivo del sprint.
2. El equipo revisa las historias prioritarias.
3. Se comprueba que cada historia cumple la Definition of Ready.
4. El equipo estima el esfuerzo.
5. Se selecciona una cantidad de trabajo acorde con la capacidad disponible.
6. Se acuerda un único Sprint Goal.

No se debe incluir trabajo adicional únicamente para mantener ocupadas a todas las personas.

## Daily Scrum

La Daily Scrum se celebra cada día laborable a las 09:30 y dura un máximo de 15 minutos.

Cada persona debe comunicar:

- Qué avance relevante ha realizado.
- Qué hará a continuación.
- Si existe algún bloqueo o riesgo.

La Daily no se utiliza para resolver problemas técnicos en detalle. Las conversaciones necesarias se realizan después con las personas implicadas.

## Sprint Review

La Sprint Review se celebra el último viernes del sprint a las 15:00.

El equipo demuestra únicamente trabajo terminado. No se presentan funcionalidades incompletas como si estuvieran finalizadas.

El Product Owner y las personas interesadas pueden aportar comentarios. Estos comentarios se añaden al Product Backlog y no modifican retroactivamente el Sprint Goal.

## Sprint Retrospective

La retrospectiva se celebra después de la Sprint Review y dura 45 minutos.

El equipo identifica:

- Qué ha funcionado bien.
- Qué ha dificultado el trabajo.
- Qué cambio concreto se probará durante el siguiente sprint.

Cada retrospectiva debe terminar con un máximo de dos acciones de mejora. Cada acción debe tener una persona responsable y una fecha de revisión.

## Definition of Ready

Una historia puede entrar en un sprint cuando:

- Explica el problema y el valor esperado.
- Tiene criterios de aceptación verificables.
- Sus dependencias conocidas están identificadas.
- No contiene decisiones críticas pendientes.
- Puede completarse dentro de un sprint.
- El equipo comprende el alcance.
- Dispone de una estimación.

Si una historia no cumple estas condiciones, permanece en el Product Backlog.

## Definition of Done

Una historia se considera terminada cuando:

- El cambio está implementado.
- La revisión de código está aprobada.
- Los tests automáticos pasan.
- Los criterios de aceptación están validados.
- La documentación necesaria está actualizada.
- No existen errores críticos conocidos.
- El cambio está integrado en la rama principal.
- El Product Owner acepta el resultado.

El trabajo que no cumple toda la Definition of Done no puede marcarse como terminado.

## Trabajo urgente

Solo una incidencia SEV-1 puede interrumpir directamente un sprint.

Una incidencia se considera SEV-1 cuando provoca una caída completa del servicio, pérdida confirmada de datos o un riesgo de seguridad activo con impacto en clientes.

El Product Owner y el responsable de operaciones deben aprobar conjuntamente la interrupción.

El nuevo trabajo urgente sustituye a trabajo de tamaño equivalente dentro del sprint. No se añade simplemente por encima del compromiso existente.

Las incidencias SEV-2 y SEV-3 se registran en el Product Backlog y se priorizan mediante el proceso habitual.

## Cambios de alcance

Después de la Sprint Planning no se añaden nuevas historias, salvo por una incidencia SEV-1.

El Product Owner puede cambiar el orden del Product Backlog, pero no puede modificar unilateralmente el contenido del sprint activo.

Si el Sprint Goal deja de tener valor para el negocio, el Product Owner puede cancelar el sprint después de consultar al equipo.

## Trabajo no terminado

Una historia no terminada vuelve al Product Backlog.

No pasa automáticamente al siguiente sprint. El Product Owner debe volver a priorizarla y el equipo debe revisar su estimación.

El trabajo parcialmente realizado debe quedar documentado antes de cerrar el sprint.

## Métricas

CloudOps AI utiliza las siguientes métricas para mejorar el proceso:

- Porcentaje de cumplimiento del Sprint Goal.
- Tiempo medio desde inicio hasta finalización.
- Número de historias trasladadas entre sprints.
- Número y duración de bloqueos.
- Acciones de retrospectiva completadas.

La velocidad no se utiliza para comparar equipos ni evaluar individualmente a las personas.