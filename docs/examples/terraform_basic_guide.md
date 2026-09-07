# Guía básica de Terraform del equipo CloudOps AI

## Objetivo

Esta guía define el proceso básico para crear y modificar infraestructura con Terraform en CloudOps AI.

El objetivo es que todos los cambios sean revisables, reproducibles y seguros. Ninguna modificación de infraestructura debe realizarse manualmente si el recurso está administrado por Terraform.

## Conceptos básicos

Terraform describe la infraestructura mediante archivos con extensión `.tf`.

Los elementos principales son:

- **Resource:** infraestructura que Terraform crea o administra.
- **Data source:** información que Terraform consulta sin crearla.
- **Variable:** valor de entrada que puede cambiar entre entornos.
- **Local:** valor calculado y reutilizable dentro de la configuración.
- **Output:** dato que Terraform muestra después de crear la infraestructura.
- **Provider:** integración utilizada para comunicarse con una plataforma como Azure.
- **State:** registro que relaciona el código Terraform con los recursos reales.

## Flujo de trabajo obligatorio

Todo cambio de Terraform debe seguir este orden:

1. Modificar la configuración.
2. Ejecutar `terraform fmt`.
3. Ejecutar `terraform validate`.
4. Generar un plan guardado.
5. Revisar el plan.
6. Obtener aprobación.
7. Aplicar exactamente el plan revisado.
8. Generar un nuevo plan para comprobar que no existen diferencias.

No se debe ejecutar `terraform apply` directamente sin revisar antes un plan guardado.

## Inicialización

El comando:

```text
terraform init
```

prepara el directorio de trabajo.

Este comando:

- Descarga los providers necesarios.
- Inicializa los módulos.
- Configura el backend.
- Prepara el acceso al estado remoto.

Debe ejecutarse al preparar el proyecto por primera vez o cuando cambien el backend, los providers o los módulos.

La inicialización no crea la infraestructura definida en los recursos.

## Formato

El comando:

```text
terraform fmt -check
```

comprueba si los archivos utilizan el formato estándar de Terraform.

Para aplicar el formato automáticamente se utiliza:

```text
terraform fmt
```

Los cambios de formato deben revisarse antes de incluirlos en un commit.

## Validación

El comando:

```text
terraform validate
```

comprueba la sintaxis, los tipos y las referencias internas de la configuración.

La validación solo afecta al directorio Terraform actual y a los módulos que este utilice. No valida automáticamente otras carpetas independientes.

Una validación correcta no garantiza que Azure permita crear los recursos. Los permisos, cuotas, nombres disponibles y restricciones de la suscripción se comprueban durante el plan o el despliegue.

## Plan guardado

El plan muestra los cambios que Terraform propone realizar.

Debe generarse como archivo:

```text
terraform plan -out=change.tfplan
```

Los archivos de plan deben terminar en `.tfplan` y estar excluidos de Git.

El resumen debe revisarse siempre:

```text
Plan: X to add, Y to change, Z to destroy
```

Cualquier destrucción o reemplazo requiere una revisión especial.

Para inspeccionar un plan guardado se utiliza:

```text
terraform show change.tfplan
```

Los archivos de plan pueden contener información de la infraestructura y no deben compartirse públicamente.

## Revisión del plan

Antes de aprobar un plan se debe comprobar:

- Que solo aparecen los recursos esperados.
- Que no existen destrucciones accidentales.
- Que las ubicaciones y nombres son correctos.
- Que los tamaños y niveles de servicio coinciden con el presupuesto.
- Que las etiquetas obligatorias están presentes.
- Que no se habilitan accesos públicos innecesarios.
- Que los permisos siguen el principio de mínimo privilegio.
- Que no se muestran secretos.
- Que las imágenes utilizan etiquetas inmutables.

Si el código o las variables cambian después de generar el plan, el plan debe descartarse y generarse de nuevo.

## Apply

El comando:

```text
terraform apply change.tfplan
```

aplica exactamente el plan guardado y revisado.

Solo puede ejecutarse después de una aprobación consciente.

No se debe utilizar:

```text
terraform apply
```

sin proporcionar un plan guardado, porque Terraform calcularía un plan nuevo que no habría sido revisado previamente.

Después del despliegue debe ejecutarse otro plan. El resultado esperado es:

```text
No changes. Your infrastructure matches the configuration.
```

## Estado remoto

El estado de Terraform debe almacenarse en un backend remoto protegido.

No se permiten archivos `terraform.tfstate` dentro del repositorio.

El backend remoto debe proporcionar:

- Acceso restringido.
- Bloqueo para evitar ejecuciones simultáneas.
- Cifrado.
- Historial o recuperación.
- Separación entre configuraciones independientes.

El estado puede contener información sensible aunque una variable esté marcada como `sensitive`. Por ese motivo, el acceso al backend debe seguir el principio de mínimo privilegio.

## Variables

Los valores que cambian entre entornos deben declararse como variables.

Cada variable debe incluir:

- Tipo.
- Descripción.
- Valor predeterminado cuando sea seguro.
- Validación cuando existan restricciones importantes.

Los archivos reales `.tfvars` no deben subirse a Git.

El repositorio debe incluir un archivo `terraform.tfvars.example` con valores ficticios que muestre la configuración necesaria.

## Secretos

Terraform no debe administrar valores de secretos de aplicación salvo que exista una razón aprobada y documentada.

No se deben incluir claves, contraseñas o tokens en:

- Archivos `.tf`.
- Archivos `.tfvars` versionados.
- Outputs.
- Nombres de recursos.
- Comandos compartidos.
- Pull requests.
- Logs de CI.

Los secretos deben cargarse directamente en el gestor de secretos aprobado. Terraform puede administrar el Key Vault, los permisos y las referencias, pero no el valor del secreto.

Marcar un valor como `sensitive` evita que se muestre normalmente, pero no impide que quede almacenado en el estado.

## Outputs

Los outputs se utilizan para mostrar datos útiles, como:

- URL pública de una aplicación.
- Nombre de un registro.
- Nombre de un Key Vault.
- Identificadores necesarios para otros procesos.

Un output no crea recursos. Solo expone información obtenida o calculada por Terraform.

Los secretos nunca deben publicarse mediante outputs.

## Uso de `-target`

`terraform -target` no se utiliza como flujo habitual.

Puede aceptarse de forma excepcional para recuperar una infraestructura dañada o resolver una situación de bootstrap que no tenga una alternativa razonable.

Cualquier uso debe:

- Estar justificado.
- Ser aprobado.
- Quedar documentado.
- Ir seguido de un plan completo.
- Confirmar que no existen diferencias inesperadas.

No debe utilizarse para ocultar dependencias incorrectas ni para aplicar habitualmente partes de una configuración.

## Cambios destructivos

Una acción destructiva incluye:

- Eliminar un recurso.
- Reemplazar un recurso.
- Cambiar una propiedad que obligue a recrearlo.
- Reducir una retención que pueda eliminar datos.
- Modificar una red o permiso con riesgo de pérdida de acceso.

Antes de aprobarla se debe confirmar:

- Qué recurso será afectado.
- Qué datos contiene.
- Si existe copia de seguridad.
- Cuánto tiempo de interrupción se espera.
- Cómo se realizará el rollback.
- Quién ha autorizado el cambio.

Nunca se aprueba una destrucción únicamente porque Terraform la muestra como necesaria.

## Convención de nombres y etiquetas

Los recursos deben utilizar nombres predecibles y consistentes.

Siempre que Azure lo permita, los nombres deben incluir:

- Tipo de recurso.
- Nombre del proyecto.
- Entorno.
- Sufijo de unicidad cuando sea necesario.

Todos los recursos compatibles deben incluir como mínimo:

```text
project
environment
managed_by
```

El valor de `managed_by` debe ser `terraform`.

## Versiones

La versión de Terraform y las versiones de los providers deben estar restringidas.

El archivo de bloqueo de providers debe incluirse en Git para que los entornos locales y CI utilicen versiones compatibles.

Las actualizaciones de providers deben realizarse en cambios separados y revisar especialmente cualquier recurso que vaya a modificarse o reemplazarse.

## Integración continua

Cada pull request que modifique Terraform debe ejecutar al menos:

```text
terraform fmt -check
terraform init
terraform validate
terraform plan
```

El plan generado por CI debe revisarse antes de fusionar los cambios.

CI no debe ejecutar automáticamente cambios destructivos ni realizar un `apply` sin el control de aprobación definido para el entorno.

## Regla final

Si el resultado de un comando Terraform no se entiende completamente, el proceso debe detenerse.

No se ejecuta `apply`, no se acepta una destrucción y no se modifica el estado hasta comprender el impacto y obtener la aprobación necesaria.