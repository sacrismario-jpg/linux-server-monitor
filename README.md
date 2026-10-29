# Linux Server Monitor

Herramienta local de monitorización y diagnóstico de sistemas Linux desarrollada en Python. Recopila métricas del sistema, identifica servicios fallidos, consulta errores recientes del registro del sistema y genera informes en la terminal o en formato JSON.

## Objetivo

Desarrollar una herramienta práctica para tareas de administración de sistemas Linux, con especial atención a la monitorización de recursos, el diagnóstico de incidencias, la detección de anomalías y el tratamiento de errores.

## Funcionalidades implementadas

- **CPU:** cálculo del porcentaje de utilización.
- **Memoria RAM:** recopilación de memoria total, disponible y porcentaje utilizado.
- **Swap:** recopilación de memoria swap total, libre y porcentaje utilizado.
- **Disco:** espacio total, utilizado y libre, junto con el porcentaje de ocupación.
- **Información del sistema:** hostname, versión del kernel, arquitectura y tiempo de actividad.
- **Diagnóstico:** clasificación del estado de las métricas mediante `OK`, `WARNING`, `CRITICAL` y `UNKNOWN`.
- **Servicios systemd:** detección de unidades de servicio fallidas.
- **Logs del sistema:** consulta de errores recientes mediante `journalctl`, con filtros por prioridad y unidad.
- **Informes:** salida legible por terminal y salida JSON.
- **Códigos de salida:** valores diferenciados para los estados del diagnóstico y los errores generales.
- **Gestión de errores:** tratamiento de errores de lectura, datos inválidos y problemas al consultar servicios o registros.
- **Pruebas automatizadas:** validación de los recolectores, el diagnóstico, los servicios, los logs y la interfaz de línea de comandos.

## Requisitos

- Sistema Linux con `systemd` y `journalctl` para las funciones de servicios y registros.
- Python 3.12 o superior.
- Biblioteca estándar de Python para las funcionalidades actuales.
- Permisos de lectura suficientes para consultar los registros que se quieran analizar.

El desarrollo y las pruebas iniciales se han realizado en Zorin OS 18.1, basado en Ubuntu 24.04, con arquitectura x86_64.

## Instalación

Clona el repositorio y accede al directorio del proyecto:

```bash
git clone https://github.com/sacrismario-jpg/linux-server-monitor.git
cd linux-server-monitor
```

Crea y activa un entorno virtual:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Instala el proyecto en modo editable:

```bash
python -m pip install -e .
```

## Uso

### Diagnóstico completo

Ejecuta la herramienta para mostrar el informe en la terminal:

```bash
python -m linux_monitor
```

El informe incluye:

- Estado general del diagnóstico.
- Información básica del sistema.
- Métricas de CPU, RAM, swap y disco.
- Estado de los servicios gestionados por systemd.
- Resumen de los errores recientes encontrados en el registro del sistema.

### Salida JSON

Para obtener el informe en formato JSON:

```bash
python -m linux_monitor --json
```

La salida JSON facilita el procesamiento del resultado mediante scripts y otras herramientas de administración.

### Interpretación de los códigos de salida

La herramienta devuelve un código de salida que permite identificar el resultado de la ejecución.

| Código | Estado | Significado |
|---:|---|---|
| `0` | `OK` | Diagnóstico correcto. |
| `1` | `WARNING` | Se ha detectado una condición de advertencia. |
| `2` | `CRITICAL` | Se ha detectado una condición crítica. |
| `3` | `UNKNOWN` | No se puede determinar completamente el estado. |
| `4` | Error general | Se ha producido un error general durante la ejecución. |

Estos códigos permiten integrar la herramienta en scripts de administración y automatización.

## Umbrales de diagnóstico

Los umbrales predeterminados se definen en `DEFAULT_THRESHOLDS`, dentro del módulo de diagnóstico.

| Métrica | WARNING | CRITICAL |
|---|---:|---:|
| CPU | 80 % | 95 % |
| RAM | 80 % | 95 % |
| Swap | 50 % | 80 % |
| Disco | 80 % | 90 % |

Los valores se evalúan como porcentajes de utilización. Cuando una métrica alcanza los umbrales configurados, el diagnóstico clasifica su estado en consecuencia.

## Monitorización de servicios systemd

La herramienta consulta las unidades fallidas mediante `systemctl`.

La información recopilada permite identificar:

- Nombre de la unidad.
- Estado de carga.
- Estado de actividad.
- Subestado.
- Descripción del servicio.

Si no se detectan unidades fallidas, el informe indica que no hay servicios fallidos. Los errores durante la consulta se gestionan para evitar que un problema aislado pase inadvertido.

## Consulta de logs con journalctl

El módulo de logs permite consultar registros recientes del sistema mediante `journalctl`.

Entre sus funcionalidades se incluyen:

- Limitación del número de registros consultados.
- Filtrado por prioridad.
- Filtrado por unidad.
- Gestión de errores y tiempos de espera.
- Incorporación de los registros obtenidos al informe de diagnóstico.

La disponibilidad de determinados registros depende de los permisos del usuario y de la configuración del sistema.

## Ejecutar las pruebas automatizadas

Desde el directorio del proyecto y con el entorno virtual activado, ejecuta:

```bash
python -m unittest discover -s tests -v
```

La suite de pruebas cubre los principales componentes del proyecto:

- Recopilación de métricas del sistema.
- Validación de valores y tratamiento de errores.
- Evaluación de umbrales y diagnóstico global.
- Códigos de salida e interfaz de línea de comandos.
- Detección de servicios fallidos.
- Consulta de logs del sistema.

**Estado de las pruebas:** 49 pruebas automatizadas superadas en la última ejecución local registrada.

## Seguridad y limitaciones

- Diseñada para ejecutarse como usuario normal, sin privilegios elevados por defecto.
- Las consultas de monitorización son de solo lectura.
- No realiza reparaciones automáticas.
- No modifica servicios ni la configuración del sistema.
- Los registros disponibles dependen de los permisos del usuario.
- Los resultados describen el estado observado en el momento de la ejecución; la herramienta no sustituye a una plataforma de monitorización continua.
- La compatibilidad se ha comprobado inicialmente en el entorno indicado. No se afirma que todas las distribuciones Linux hayan sido validadas.

## Tecnologías utilizadas

- **Python 3:** implementación de la herramienta y sus pruebas.
- **Linux:** sistema operativo objetivo.
- **systemd / systemctl:** consulta del estado de los servicios.
- **journalctl:** consulta de los registros del sistema.
- **unittest:** pruebas automatizadas.
- **Git y GitHub:** control de versiones y publicación del proyecto.

## Estado del proyecto

**Versión funcional en desarrollo, publicada en GitHub.**

Linux Server Monitor permite recopilar métricas básicas, identificar información del sistema, evaluar umbrales, detectar servicios fallidos y consultar errores recientes del registro del sistema. Los resultados se presentan mediante informes de terminal o JSON.

La suite de pruebas cuenta con **49 pruebas automatizadas superadas** en la última ejecución local registrada.

### Próximas mejoras

- Ampliar la cobertura de pruebas en distintos entornos Linux.
- Mejorar la documentación de los diagnósticos y de los posibles errores.
- Incorporar nuevas comprobaciones de administración de sistemas.
- Valorar opciones de configuración para adaptar los umbrales a diferentes entornos.

## Autor y repositorio

Proyecto personal desarrollado como práctica de Python y administración de sistemas Linux.

Repositorio: https://github.com/sacrismario-jpg/linux-server-monitor
