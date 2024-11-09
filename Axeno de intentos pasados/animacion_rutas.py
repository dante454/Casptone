import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from caso_base import camiones  

# Configuración inicial
fig, ax = plt.subplots()
ax.set_xlim(0, 20000)
ax.set_ylim(0, 20000)

# Variables globales para las rutas y el tiempo
routes_to_show = []  # Aquí se irán agregando las rutas para mostrar
time_index = 520  # Índice para manejar el tiempo (ajustado según el rango de tiempo de la simulación)

# Inicializar las líneas de las rutas
lines = {}

# Colores para los camiones
colors = {1: 'red', 2: 'blue', 3: 'green'}

# Función de inicialización para FuncAnimation
def init():
    for line in lines.values():
        line.set_data([], [])
    return lines.values()

# Función que actualiza la animación en cada frame
def update(frame):
    global time_index, routes_to_show

    # Recorremos los camiones y actualizamos las rutas si corresponde
    for camion in camiones:
        rutas = camion.rutas  # Rutas del camión
        tiempos = [ruta[1] for ruta in rutas]  # Tiempo en que sale cada ruta (ajustar según tus datos de simulación)

        # Si el tiempo actual coincide con la salida de una ruta, la añadimos para mostrarla
        for idx, ruta in enumerate(rutas):
            if time_index == tiempos[idx]:  # Comparamos si el tiempo actual coincide
                # Añadir la ruta que debe mostrarse en este momento
                routes_to_show.append((camion.id, ruta[0]))  # ruta[0] es la lista de puntos

    # Dibujar las rutas de todos los camiones hasta el momento actual
    for camion_id, ruta in routes_to_show:
        x, y = zip(*ruta)
        lines[camion_id].set_data(x, y)

    # Aumentamos el índice del tiempo
    time_index += 1

    return lines.values()

# Preparar las líneas para cada camión (según tu simulación)
for camion in camiones:
    lines[camion.id] = ax.plot([], [], color=colors[camion.id], lw=2)[0]

# Crear la animación
ani = FuncAnimation(fig, update, frames=np.arange(520, 1020), init_func=init, blit=True, interval=200)

plt.show()
