# Batería de preguntas de ejemplo

Este documento contiene una selección de preguntas para probar la búsqueda semántica y el flujo RAG de CloudOps AI.

Las respuestas se basan en los siguientes documentos de ejemplo:

- [Guía básica de Terraform](terraform_basic_guide.md)
- [Guía del equipo Scrum](scrum_team_guide.md)

La batería incluye consultas que requieren recuperar contexto, preguntas conversacionales que pueden responderse sin consultar Qdrant y algunos casos pensados para comprobar cómo se comporta el sistema cuando la información solicitada no está disponible.

## Documento Scrum
1. ¿Cuánto dura un sprint en CloudOps AI?
2. ¿A qué hora comienza la Sprint Planning?
3. ¿Cuánto puede durar como máximo la Daily Scrum?
4. ¿Quién decide las prioridades del Product Backlog?
5. ¿El Scrum Master puede asignar tareas al equipo?
6. ¿Qué condiciones debe cumplir una historia para entrar en un sprint?
7. ¿Qué requisitos debe cumplir una historia para considerarse terminada?
8. ¿Qué tipo de incidencia puede interrumpir directamente un sprint?
9. ¿Quién debe aprobar la entrada de trabajo urgente?
10. ¿Qué ocurre con una historia que no se termina durante el sprint?
11. ¿Puede el Product Owner añadir unilateralmente una historia al sprint activo?
12. ¿Cuántas acciones de mejora pueden salir como máximo de una retrospectiva?
13. ¿Cuándo puede cancelar un sprint el Product Owner?
14. ¿Se puede presentar trabajo incompleto durante la Sprint Review?
15. ¿Se utiliza la velocidad para comparar equipos o evaluar personas?

## Documento Terraform
1. ¿Cuál es el flujo obligatorio antes de ejecutar un terraform apply?
2. ¿Qué hace terraform init?
3. ¿terraform init crea recursos en Azure?
4. ¿Qué diferencia existe entre terraform fmt y terraform validate?
5. ¿Qué valida exactamente terraform validate?
6. ¿Cómo se genera un plan guardado?
7. ¿Qué debe revisarse antes de aprobar un plan?
8. ¿Qué significa que el plan muestre un recurso to destroy?
9. ¿Por qué no se debe ejecutar terraform apply sin un plan guardado?
10. ¿Dónde debe almacenarse el estado de Terraform?
11. ¿Se pueden subir archivos .tfvars reales a Git?
12. ¿Marcar una variable como sensitive evita que llegue al estado?
13. ¿Puede Terraform mostrar una contraseña mediante un output?
14. ¿Cuándo está permitido utilizar terraform -target?
15. ¿Qué debe hacerse después de un apply?
16. ¿Qué etiquetas mínimas deben tener los recursos?
17. ¿Qué valor debe tener la etiqueta managed_by?
18. ¿Por qué se debe versionar el archivo de bloqueo de providers?
19. ¿Qué validaciones debe ejecutar CI para un cambio de Terraform?
20. ¿Qué debe hacerse si no se entiende completamente el resultado de un plan?

## Preguntas que combinan ambos documentos

1. ¿Qué validaciones deben completarse para que una historia de Terraform se considere terminada?
2. ¿Puede entrar en un sprint una tarea de infraestructura que todavía tiene decisiones críticas pendientes?
3. ¿Qué proceso debe seguir el equipo antes de aplicar un cambio urgente de Terraform?
4. ¿Quién debe aprobar una modificación destructiva introducida por una incidencia SEV-1?
5. ¿Puede marcarse como terminada una historia si el plan Terraform todavía contiene cambios inesperados?
6. ¿Qué debe ocurrir si una tarea de Terraform no termina antes del cierre del sprint?
7. ¿Qué controles de Terraform ayudan a cumplir la Definition of Done?
8. ¿Puede una urgencia justificar ejecutar terraform apply sin revisar un plan?
9. ¿Cómo debería tratarse en la retrospectiva un despliegue Terraform que causó una interrupción?
10. ¿Puede el Product Owner ordenar que se aplique un cambio destructivo sin la revisión técnica correspondiente?