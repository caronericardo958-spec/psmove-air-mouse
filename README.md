# 🖱️ PS Move Air Mouse

Transforma un mando de **PlayStation Move** en un ratón aéreo de alta precisión para Windows, optimizado con **cero latencia**, **trazos rectos inteligentes** para dibujo/interacción y **soporte multimonitor**.

---

## 🛠️ Requisitos Previos

1. **Windows 10 u 11 (64-bit)**.
2. **Bluetooth**: Un adaptador USB Bluetooth (recomendable versión 4.0 o superior) o Bluetooth integrado.
3. **Mando PS Move**: Totalmente cargado (conectado previamente por USB para verificar batería).
4. **PSMoveServiceEX**: Software para gestionar el emparejamiento Bluetooth en Windows.

---

## 📖 Tutorial: Cómo conectar el PS Move a la PC (PSMoveServiceEX)

Antes de iniciar la aplicación por primera vez, el mando PS Move debe estar emparejado correctamente mediante **PSMoveServiceEX**.

### Paso 1: Descargar e instalar PSMoveServiceEX
1. Descarga la última versión de **PSMoveServiceEX** desde su repositorio oficial en GitHub.
2. Extrae el contenido del archivo `.zip` en una carpeta de tu preferencia (ej. `C:\PSMoveServiceEX`).

### Paso 2: Registrar el PS Move vía USB (Primera vez)
1. Conecta tu mando PS Move a la PC mediante un **cable USB**.
2. Ve a la carpeta de PSMoveServiceEX y ejecuta **`PSMoveService.exe`** (se abrirá una consola de comandos). Déjala abierta.
3. En la misma carpeta, ejecuta **`PSMoveConfigTool.exe`**.
4. En el menú superior de la interfaz, selecciona **Controller Settings** > **Pair Controller**.
5. Sigue las instrucciones en pantalla para vincular la dirección MAC de tu adaptador Bluetooth con el mando PS Move.

### Paso 3: Conexión inalámbrica por Bluetooth
1. Una vez completado el emparejamiento, **desconecta el cable USB** del PS Move.
2. Presiona el botón **PS** del mando. La luz LED roja comenzará a parpadear y luego se quedará **fija**.
3. En `PSMoveConfigTool.exe`, confirma que el mando aparece como conectado e identificado.
4. Ya puedes cerrar `PSMoveConfigTool.exe` y `PSMoveService.exe`.

---

## 🚀 Uso del Air Mouse

1. Con el mando PS Move encendido y conectado por Bluetooth, ejecuta el archivo **`air_mouse_pruebas.exe`**.
2. El programa detectará el mando de forma automática.

### Controles integrados:
* **Mover el cursor**: Mantén presionado el **Gatillo Trasero (T)** y mueve la mano.
* **Clic Izquierdo**: Presiona el botón **MOVE** (el botón frontal grande).
* **Cerrar Aplicación**: Presiona el botón **PS**.

---

## 🎯 Características Principales

* **Filtro de Trazo Recto (Snapping)**: Si realizas movimientos principalmente horizontales o verticales, el algoritmo cancela las pequeñas desviaciones no deseadas para lograr líneas perfectamente rectas.
* **Respuesta Inmediata**: Algoritmo ajustado para vaciar el búfer Bluetooth en tiempo real, eliminando el arrastre o delay.
* **Soporte Multimonitor**: Detecta automáticamente el espacio de trabajo combinado de todas las pantallas conectadas.

---

## ❓ Solución de Problemas

* **El programa se queda en `Buscando mando PS Move...`**:
  * Apaga el mando manteniendo presionado el botón **PS** durante 10 segundos.
  * Presiona el botón **PS** una vez para volver a encenderlo (asegúrate de que la luz quede fija).
  * Vuelve a iniciar la aplicación.
* **El cursor salta o tiembla**:
  * Deja el mando apoyado sobre una superficie plana durante 2 segundos con el programa abierto para que la autocalibración de reposo se ajuste automáticamente.