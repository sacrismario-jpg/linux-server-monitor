# Linux Server Monitor

Herramienta local de monitorización y diagnóstico de sistemas Linux desarrollada en Python. Recopila métricas básicas del sistema, evalúa su estado mediante umbrales y genera informes en la terminal o en formato JSON.

## Objetivo

Desarrollar una herramienta práctica para tareas de administración de sistemas Linux, con especial atención a la monitorización de recursos, la detección de condiciones anómalas y el tratamiento de errores.

## Funcionalidades implementadas

- **CPU:** cálculo del porcentaje de utilización.
- **Memoria RAM:** recopilación de memoria total, disponible y porcentaje utilizado.
- **Swap:** recopilación de memoria swap total, libre y porcentaje utilizado.
- **Disco:** espacio total, utilizado y libre, junto con el porcentaje de ocupación.
- **Sistema:** identificación del equipo, kernel, arquitectura y tiempo de actividad.
- **Diagnóstico:** clasificación mediante los estados `OK`, `WARNING`, `CRITICAL` y `UNKNOWN`.
- **Informes:** salida legible por terminal y salida JSON.
- **Códigos de salida:** valores diferenciados para los estados del diagnóstico y los errores generales.
- **Pruebas automatizadas:** validación de los recolectores, el diagnóstico y la interfaz de línea de comandos.

## Requisitos

- Linux.
- Python 3.12 o superior.
- Biblioteca estándar de Python para las funcionalidades actuales.

El desarrollo y las pruebas iniciales se han realizado en Zorin OS 18.1, basado en Ubuntu 24.04, con arquitectura x86_64.

## Instalación para desarrollo

Clona el repositorio cuando esté publicado y entra en su directorio:

```bash
git clone <URL_DEL_REPOSITORIO>
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

Ejecuta el diagnóstico y muestra el informe en la terminal:

```bash
python -m linux_monitor
```

Genera el informe en formato JSON:

```bash
python -m linux_monitor --json
```

La herramienta devuelve un código de salida según el resultado global del diagnóstico. Consulta la sección de códigos de salida para interpretar el resultado en scripts.

## Códigos de salida

| Código | Significado |
|---:|---|
| `0` | `OK` |
| `1` | `WARNING` |
| `2` | `CRITICAL` |
| `3` | `UNKNOWN` |
| `4` | Error general de ejecución |

## Umbrales de diagnóstico

Los umbrales predeterminados se definen en el código:

| Métrica | WARNING | CRITICAL |
|---|---:|---:|
| CPU | 80 % | 95 % |
| RAM | 80 % | 95 % |
| Swap | 50 % | 80 % |
| Disco | 80 % | 90 % |

Los valores se evalúan como porcentajes. Los umbrales se definen en `DEFAULT_THRESHOLDS`, en el módulo de diagnóstico.

## Ejecutar las pruebas

Desde el directorio del proyecto, con el entorno virtual activado, ejecuta:

```bash
python -m unittest discover -s tests -v
```

En el estado actual del desarrollo, la suite contiene **32 pruebas automatizadas**, superadas en la última ejecución local.

## Seguridad y limitaciones

- Diseñada para ejecutarse como usuario normal, sin privilegios elevados por defecto.
- No realiza reparaciones automáticas.
- No modifica servicios ni la configuración del sistema.
- La recopilación de métricas es de solo lectura.
- El resultado describe las métricas recogidas en el momento de la ejecución; no sustituye a una plataforma de monitorización continua.
- La compatibilidad se ha comprobado inicialmente en el entorno indicado. No se afirma que todas las distribuciones Linux hayan sido validadas.

## Funcionalidades previstas

- Detección de servicios fallidos mediante `systemd`.
- Consulta de errores recientes mediante `journalctl`.
- Ampliación de las pruebas y de la documentación de instalación y uso.

Estas funcionalidades se consideran pendientes hasta que estén implementadas y verificadas.

## Estado del proyecto

**Versión inicial funcional en preparación para su publicación.**

El proyecto dispone de recolectores de métricas, diagnóstico, salida por terminal y JSON, además de una suite de pruebas automatizadas. El siguiente objetivo es completar la revisión del código y preparar el repositorio para su publicación en GitHub.
