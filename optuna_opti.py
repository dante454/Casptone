#    IMPORTANTE
#Para correr este archivo es necesario comentar la linea 166, 167 y 318 del archivo politica_final

import optuna
from funciones_caso_base import EstadoSimulacion, Camion, procesar_tiempos, calcular_tiempo_ruta
from politica_final import simular_minuto_a_minuto, points, indicadores, arribos_por_minuto
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Define la función objetivo de Optuna para optimizar los parámetros en tres ventanas de tiempo distintas
def objetivo(trial):
    # Parámetros para la primera ventana de tiempo (desde el inicio hasta el minuto 650)
    parametros_ventana_1 = {
        "min_pedidos_salida": trial.suggest_int("min_pedidos_salida_1", 5, 20),
        "porcentaje_reduccion_distancia": trial.suggest_int("porcentaje_reduccion_distancia_1", 30, 70),
        "max_puntos_eliminados": trial.suggest_int("max_puntos_eliminados_1", 5, 20),
        "x_minutos": trial.suggest_int("x_minutos_1", 10, 60),
        "limite_area1": trial.suggest_int("limite_area1_1", 90, 150),
        "limite_area2": trial.suggest_int("limite_area2_1", 180, 270),
        "peso_min_pedidos": trial.suggest_float("peso_min_pedidos_1", 0.5, 2.0),
        "peso_ventana_tiempo": trial.suggest_float("peso_ventana_tiempo_1", 0.5, 2.0),
        "umbral_salida": trial.suggest_float("umbral_salida_1", 1.0, 2.0),
        "tiempo_minimo_pickup": trial.suggest_int("tiempo_minimo_pickup_1", 15, 45),
        "max_aumento_distancia": trial.suggest_int("max_aumento_distancia_1", 5, 20),
        "tiempo_necesario_pick_up": trial.suggest_int("tiempo_necesario_pick_up_1", 1000, 1500),
        "tiempo_restante_max": trial.suggest_int("tiempo_restante_max_1", 100, 200),
        "max_aumento_distancia_delivery": trial.suggest_int("max_aumento_distancia_delivery_1", 50, 150),
        "tiempo_maximo_entrega": 180,  # Valor constante
    }

    # Parámetros para la segunda ventana de tiempo (651 al 780)
    parametros_ventana_2 = {
        "min_pedidos_salida": trial.suggest_int("min_pedidos_salida_2", 5, 20),
        "porcentaje_reduccion_distancia": trial.suggest_int("porcentaje_reduccion_distancia_2", 30, 70),
        "max_puntos_eliminados": trial.suggest_int("max_puntos_eliminados_2", 5, 20),
        "x_minutos": trial.suggest_int("x_minutos_2", 10, 60),
        "limite_area1": trial.suggest_int("limite_area1_2", 90, 150),
        "limite_area2": trial.suggest_int("limite_area2_2", 180, 270),
        "peso_min_pedidos": trial.suggest_float("peso_min_pedidos_2", 0.5, 2.0),
        "peso_ventana_tiempo": trial.suggest_float("peso_ventana_tiempo_2", 0.5, 2.0),
        "umbral_salida": trial.suggest_float("umbral_salida_2", 1.0, 2.0),
        "tiempo_minimo_pickup": trial.suggest_int("tiempo_minimo_pickup_2", 15, 45),
        "max_aumento_distancia": trial.suggest_int("max_aumento_distancia_2", 5, 20),
        "tiempo_necesario_pick_up": trial.suggest_int("tiempo_necesario_pick_up_2", 1000, 1500),
        "tiempo_restante_max": trial.suggest_int("tiempo_restante_max_2", 100, 200),
        "max_aumento_distancia_delivery": trial.suggest_int("max_aumento_distancia_delivery_2", 50, 150),
        "tiempo_maximo_entrega": 180,  # Valor constante
    }

    # Parámetros para la tercera ventana de tiempo (781 al 1020)
    parametros_ventana_3 = {
        "min_pedidos_salida": trial.suggest_int("min_pedidos_salida_3", 5, 20),
        "porcentaje_reduccion_distancia": trial.suggest_int("porcentaje_reduccion_distancia_3", 30, 70),
        "max_puntos_eliminados": trial.suggest_int("max_puntos_eliminados_3", 5, 20),
        "x_minutos": trial.suggest_int("x_minutos_3", 10, 60),
        "limite_area1": trial.suggest_int("limite_area1_3", 90, 150),
        "limite_area2": trial.suggest_int("limite_area2_3", 180, 270),
        "peso_min_pedidos": trial.suggest_float("peso_min_pedidos_3", 0.5, 2.0),
        "peso_ventana_tiempo": trial.suggest_float("peso_ventana_tiempo_3", 0.5, 2.0),
        "umbral_salida": trial.suggest_float("umbral_salida_3", 1.0, 2.0),
        "tiempo_minimo_pickup": trial.suggest_int("tiempo_minimo_pickup_3", 15, 45),
        "max_aumento_distancia": trial.suggest_int("max_aumento_distancia_3", 5, 20),
        "tiempo_necesario_pick_up": trial.suggest_int("tiempo_necesario_pick_up_3", 1000, 1500),
        "tiempo_restante_max": trial.suggest_int("tiempo_restante_max_3", 100, 200),
        "max_aumento_distancia_delivery": trial.suggest_int("max_aumento_distancia_delivery_3", 50, 150),
        "tiempo_maximo_entrega": 180,  # Valor constante
    }

    # Inicializa la simulación y los camiones
    simulacion = EstadoSimulacion(minuto_inicial=520, puntos=points, indicadores=indicadores, arribos_por_minuto=arribos_por_minuto)
    camiones = [
        Camion(id=1, tiempo_inicial=0),
        Camion(id=2, tiempo_inicial=0),
        Camion(id=3, tiempo_inicial=0)
    ]

    # Ejecuta la simulación aplicando los parámetros específicos de cada ventana
    simular_minuto_a_minuto(simulacion, camiones, parametros_ventana_1, parametros_ventana_2, parametros_ventana_3)

    # Calcula el beneficio total obtenido
    benef_acumulado = simulacion.calcular_beneficio_acumulado()
    beneficio_total = simulacion.calcular_porcentaje_beneficio(benef_acumulado)
    
    return beneficio_total




# Crear un estudio de Optuna para maximizar el beneficio
estudio = optuna.create_study(direction="maximize")
estudio.optimize(objetivo, n_trials=100)  # n_trials es el número de iteraciones

# Obtener los mejores parámetros y su valor de beneficio total
mejores_parametros = estudio.best_params
mejor_beneficio = estudio.best_value

# Separar los parámetros en diccionarios por ventana de tiempo
#esto es para luego poder utilizarlos 
mejores_parametros_ventana_1 = {k.replace('_1', ''): v for k, v in mejores_parametros.items() if '_1' in k}
mejores_parametros_ventana_2 = {k.replace('_2', ''): v for k, v in mejores_parametros.items() if '_2' in k}
mejores_parametros_ventana_3 = {k.replace('_3', ''): v for k, v in mejores_parametros.items() if '_3' in k}

# Convertir los mejores parámetros a un DataFrame para una visualización más organizada
df_mejores_parametros = pd.DataFrame(mejores_parametros.items(), columns=["Parámetro", "Valor"])

# Añadir el beneficio total al final de la tabla para referencia
df_mejores_parametros = df_mejores_parametros._append({"Parámetro": "Mejor porcentaje obtenido", "Valor": mejor_beneficio}, ignore_index=True)

# Mostrar los mejores parámetros en forma de tabla
print("Mejores Parámetros de la Optimización")
print(df_mejores_parametros)

