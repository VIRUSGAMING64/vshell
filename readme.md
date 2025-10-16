# 🚀 vshell

[![License: PolyForm Noncommercial 1.0.0](https://img.shields.io/badge/license-PolyForm%20Noncommercial%201.0.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-3776AB.svg?logo=python&logoColor=white)](requirements.txt)

Proyecto modular en Python que combina un núcleo de automatización (bot) y un componente web, con utilidades para descargas, compresión y gestión de usuarios. Este README documenta la estructura del proyecto, los módulos disponibles y cómo ponerlo en marcha.

> ℹ️ Nota: Este documento se ha generado a partir de la estructura actual del repositorio. Si tu flujo real de trabajo difiere (por ejemplo, variables de entorno, comandos o servicios específicos), ajústalo en la sección Configuración.

---

## 📚 Tabla de contenidos
- 📦 Requisitos
- ⚙️ Instalación
- ▶️ Ejecución rápida
- 🗂️ Estructura del proyecto
- 🔌 Módulos
- 🛠️ Scripts auxiliares
- 🧰 Configuración
- 👩‍💻 Desarrollo
- 📝 Problemas conocidos / TODO
- 📄 Licencia

---

## 📦 Requisitos

- Python 3.10+ (recomendado)
- pip actualizado
- Entorno virtual (opcional pero recomendado)

Dependencias del proyecto: ver [requirements.txt](requirements.txt).

---

## ⚙️ Instalación

1) Clonar el repositorio:
```bash
git clone https://github.com/VIRUSGAMING64/vshell.git
cd vshell
```

2) Crear y activar un entorno virtual (opcional):
- Linux/macOS:
  ```bash
  python -m venv .venv
  source .venv/bin/activate
  ```
- Windows (PowerShell):
  ```powershell
  python -m venv .venv
  .venv\Scripts\Activate.ps1
  ```

3) Instalar dependencias:
```bash
pip install -r requirements.txt
```

---

## ▶️ Ejecución rápida

Ejecutar el núcleo (bot / servicio principal):
```bash
python bot.py
```

> 🌐 Si el proyecto expone un servidor web, revisa el módulo [modules/web.py](modules/web.py) y la carpeta [templates/](templates/) para confirmar el endpoint/puerto y el modo de arranque (puede estar integrado en `bot.py` o levantarse por separado).

---

## 🗂️ Estructura del proyecto

```text
.
├─ bot.py                  # Punto de entrada del servicio/bot principal
├─ requirements.txt        # Dependencias de Python
├─ TODO                    # Lista de pendientes
├─ modules/                # Módulos de negocio y utilidades
│  ├─ Gvar.py
│  ├─ IDM.py
│  ├─ Utils.py
│  ├─ VidDown.py
│  ├─ compressor.py
│  ├─ datatypes.py
│  ├─ imports.py
│  ├─ pool.py
│  ├─ users.py
│  └─ web.py
├─ templates/              # Plantillas utilizadas por el módulo web
├─ web/                    # Código/recursos del componente web
├─ subc.sh                 # Script auxiliar
└─ rmbots.sh               # Script auxiliar
```

---

## 🔌 Módulos

Descripción del directorio `modules/`:

- 🧭 Gvar.py
  - Gestión de variables globales y configuración compartida.
  - Centraliza banderas, rutas o parámetros usados por múltiples módulos.

- ⬇️ IDM.py
  - Abstracción de un gestor de descargas.
  - Maneja colas de descarga, seguimiento de progreso y reintentos.

- 🧰 Utils.py
  - Utilidades comunes y funciones de apoyo transversales (I/O, validaciones, formateo, logging, etc.).
  - Evita duplicación de código con helpers reutilizables.

- 🎥 VidDown.py
  - Lógica de descarga de videos desde distintas fuentes/plataformas.
  - Envuelve bibliotecas de descarga y normaliza la salida/formato.

- 🗜️ compressor.py
  - Compresión/descompresión de ficheros y directorios (p. ej., ZIP/TAR).
  - Manejo de tamaños, división de archivos y rutas temporales.

- 🧩 datatypes.py
  - Tipos, constantes y estructuras del dominio.
  - Ayuda al tipado y contratos internos entre módulos.

- 💤 imports.py
  - Gestión de imports opcionales y carga perezosa (lazy loading).
  - Mejora compatibilidad y tiempos de arranque.

- ⚡ pool.py
  - Pool de ejecución (hilos/procesos/tareas asíncronas) para trabajos en paralelo.
  - Ideal para operaciones intensivas de red/IO, descargas y tareas batch.

- 👤 users.py
  - Gestión de usuarios: autorización, perfiles/estados y persistencia asociada.
  - Puede incluir listas blanca/negra, roles o límites por usuario.

- 🌐 web.py
  - Servidor web/API y rutas.
  - Integra recursos de [templates/](templates/) y posiblemente [web/](web/).

---

## 🛠️ Scripts auxiliares

- 🧪 subc.sh
  - Script de apoyo para tareas de desarrollo/operación. Revisa su contenido para el uso exacto.

- 🧹 rmbots.sh
  - Script de apoyo minimalista. Revisa su contenido para el uso exacto.

> Asegura permisos de ejecución:
```bash
chmod +x subc.sh rmbots.sh
```

---

## 🧰 Configuración

La configuración depende de cómo `bot.py` y `modules/web.py` consuman parámetros. Patrones comunes:

- Variables de entorno (ejemplos):
  - `BOT_TOKEN`, `API_ID`, `API_HASH`, `ADMINS`
  - Rutas de salida para descargas/compresión
  - Parámetros del servidor web (`HOST`, `PORT`)

- Archivos de configuración:
  - Si se usa, puede ser `.env`, YAML o JSON.

Ejemplos:

Linux/macOS:
```bash
export BOT_TOKEN="TU_TOKEN"
export PORT=8080
```

Windows (PowerShell):
```powershell
$env:BOT_TOKEN="TU_TOKEN"
$env:PORT=8080
```

---

## 👩‍💻 Desarrollo

- Estilo de código:
  - Mantén funciones utilitarias en `Utils.py`.
  - Define tipos/constantes en `datatypes.py`.
  - Usa `pool.py` para tareas concurrentes.
  - Centraliza configuración compartida en `Gvar.py`.

- Añadir un nuevo módulo:
  1) Crea un archivo en `modules/` con una responsabilidad clara.
  2) Exporta funciones/clases públicas bien definidas.
  3) Integra el módulo en `bot.py` o donde corresponda.
  4) Documenta brevemente el módulo en este README.

- Plantillas/UI:
  - `web.py` utiliza `templates/`. Mantén lógica y presentación separadas.

---

## 📝 Problemas conocidos / TODO

Consulta [TODO](TODO) para la lista actual de pendientes. Si añades tareas nuevas, actualiza ese archivo y/o crea issues.

---

## 📄 Licencia

Este proyecto está licenciado bajo PolyForm Noncommercial License 1.0.0. Puedes usar, modificar y redistribuir el código para fines no comerciales. No se permite vender este software ni usarlo con fines comerciales.

- SPDX: `PolyForm-Noncommercial-1.0.0`
- Texto completo: https://polyformproject.org/licenses/noncommercial/1.0.0/