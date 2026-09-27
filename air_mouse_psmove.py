import os
import sys
import time
import ctypes
import pyautogui
from screeninfo import get_monitors

pyautogui.FAILSAFE = False

# --- 1. CONFIGURACIÓN DE RUTAS Y DLL ---
DLL_PATH = r"D:\Downloads\psmoveapi-4.0.12-windows-msvc2017-x64\lib"
DLL_NAME = "psmoveapi.dll"

full_dll_path = os.path.join(DLL_PATH, DLL_NAME)

if os.path.exists(DLL_PATH):
    if hasattr(os, "add_dll_directory"):
        os.add_dll_directory(DLL_PATH)
    os.environ["PATH"] = DLL_PATH + os.pathsep + os.environ.get("PATH", "")

try:
    psmove_dll = ctypes.CDLL(full_dll_path)
except Exception as e:
    print(f"[ERROR] No se pudo cargar la DLL: {e}")
    sys.exit(1)

# Vincular funciones nativas
psmove_dll.psmove_count_connected.restype = ctypes.c_int
psmove_dll.psmove_connect_by_id.argtypes = [ctypes.c_int]
psmove_dll.psmove_connect_by_id.restype = ctypes.c_void_p
psmove_dll.psmove_poll.argtypes = [ctypes.c_void_p]
psmove_dll.psmove_poll.restype = ctypes.c_int
psmove_dll.psmove_get_buttons.argtypes = [ctypes.c_void_p]
psmove_dll.psmove_get_buttons.restype = ctypes.c_uint
psmove_dll.psmove_disconnect.argtypes = [ctypes.c_void_p]

psmove_dll.psmove_get_gyroscope_frame.argtypes = [
    ctypes.c_void_p,
    ctypes.c_int,
    ctypes.POINTER(ctypes.c_float),
    ctypes.POINTER(ctypes.c_float),
    ctypes.POINTER(ctypes.c_float)
]

# Botones
Btn_T = 1 << 20
Btn_MOVE = 1 << 19
Btn_PS = 1 << 16

# --- 2. CONFIGURACIÓN AJUSTADA ---
SENSIBILIDAD = 0.03      # Velocidad del puntero
DEADZONE = 0.35          # Umbral de ruido en reposo
SUAVIZADO = 0.10         # Alta velocidad de respuesta (casi 0 delay)

RATIO_LINETRAZO = 2.5    # Estabilizador de líneas rectas

INVERTIR_X = -1
INVERTIR_Y = -1


def obtener_limites_pantalla():
    """Calcula el área combinada de todos los monitores conectados."""
    min_x, min_y = 0, 0
    max_x, max_y = 0, 0
    
    try:
        monitors = get_monitors()
        min_x = min(m.x for m in monitors)
        min_y = min(m.y for m in monitors)
        max_x = max(m.x + m.width for m in monitors)
        max_y = max(m.y + m.height for m in monitors)
    except Exception as e:
        print(f"[!] Advertencia al detectar monitores: {e}. Usando monitor principal.")
        sw, sh = pyautogui.size()
        max_x, max_y = sw, sh

    return min_x, min_y, max_x - 1, max_y - 1


def estabilizar_trazo_recto(vx, vy):
    abs_x = abs(vx)
    abs_y = abs(vy)

    if abs_x > 0 and abs_y > 0:
        if abs_x / abs_y > RATIO_LINETRAZO:
            vy = 0.0
        elif abs_y / abs_x > RATIO_LINETRAZO:
            vx = 0.0

    return vx, vy


def aplicar_curva(valor):
    signo = 1.0 if valor > 0 else -1.0
    return signo * (abs(valor) ** 1.3)


def main():
    print("--- AIR MOUSE (MULTIMONITOR + TRAZO RECTO) ---", flush=True)
    print("-> Mantén presionado el GATILLO TRASERO (T) para mover el ratón.", flush=True)
    print("-> Presiona MOVE para hacer clic.", flush=True)
    print("-> Presiona el botón PS para salir.\n", flush=True)

    min_x, min_y, max_x, max_y = obtener_limites_pantalla()
    print(f"[*] Área de trabajo multimonitor: X({min_x} a {max_x}), Y({min_y} a {max_y})", flush=True)

    handle = None
    print("[*] Buscando mando PS Move...", flush=True)
    while handle is None:
        count = psmove_dll.psmove_count_connected()
        if count > 0:
            handle = psmove_dll.psmove_connect_by_id(0)
            if handle:
                print(f"[+] Mando vinculado correctamente. Handle: {handle}", flush=True)
                break
        time.sleep(0.5)

    gx_raw = ctypes.c_float()
    gy_raw = ctypes.c_float()
    gz_raw = ctypes.c_float()

    offset_z = 0.0
    offset_x = 0.0
    samples_z = []
    samples_x = []

    remainder_x = 0.0
    remainder_y = 0.0
    smooth_x = 0.0
    smooth_y = 0.0

    prev_buttons = 0
    running = True

    try:
        while running:
            if psmove_dll.psmove_poll(handle):
                buttons = psmove_dll.psmove_get_buttons(handle)

                psmove_dll.psmove_get_gyroscope_frame(
                    handle,
                    0,
                    ctypes.byref(gx_raw),
                    ctypes.byref(gy_raw),
                    ctypes.byref(gz_raw)
                )

                raw_z = gz_raw.value * INVERTIR_X
                raw_x = gx_raw.value * INVERTIR_Y

                # Autocalibración de deriva en reposo
                samples_z.append(raw_z)
                samples_x.append(raw_x)

                if len(samples_z) > 40:
                    samples_z.pop(0)
                    samples_x.pop(0)

                    if (max(samples_z) - min(samples_z)) < 0.2 and (max(samples_x) - min(samples_x)) < 0.2:
                        offset_z = sum(samples_z) / len(samples_z)
                        offset_x = sum(samples_x) / len(samples_x)

                gz = raw_z - offset_z
                gx = raw_x - offset_x

                # Deadzone & Trazo recto
                val_x = gz if abs(gz) > DEADZONE else 0.0
                val_y = gx if abs(gx) > DEADZONE else 0.0
                val_x, val_y = estabilizar_trazo_recto(val_x, val_y)

                curva_x = aplicar_curva(val_x)
                curva_y = aplicar_curva(val_y)

                smooth_x = (smooth_x * (1 - SUAVIZADO)) + (curva_x * SUAVIZADO)
                smooth_y = (smooth_y * (1 - SUAVIZADO)) + (curva_y * SUAVIZADO)

                # Movimiento con gatillo T
                if buttons & Btn_T:
                    remainder_x += smooth_x * SENSIBILIDAD
                    remainder_y += smooth_y * SENSIBILIDAD

                    move_x = int(remainder_x)
                    move_y = int(remainder_y)

                    remainder_x -= move_x
                    remainder_y -= move_y

                    if move_x != 0 or move_y != 0:
                        cur_x, cur_y = pyautogui.position()
                        new_x = min(max(min_x, cur_x + move_x), max_x)
                        new_y = min(max(min_y, cur_y + move_y), max_y)
                        
                        pyautogui.moveTo(new_x, new_y)
                else:
                    remainder_x = 0.0
                    remainder_y = 0.0
                    smooth_x = 0.0
                    smooth_y = 0.0

                # Botones
                pressed = buttons & ~prev_buttons

                if pressed & Btn_MOVE:
                    pyautogui.click()

                if pressed & Btn_PS:
                    print("\n[!] Saliendo del programa...", flush=True)
                    running = False

                prev_buttons = buttons

            time.sleep(0.002)

    finally:
        if handle:
            psmove_dll.psmove_disconnect(handle)
            print("[+] Mando desconectado limpiamente.", flush=True)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[!] Detenido por el usuario.")
    except Exception as e:
        print(f"\n[ERROR]: {e}")