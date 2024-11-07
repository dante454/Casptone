import optuna
from funciones_caso_base import EstadoSimulacion, Camion, procesar_tiempos, calcular_tiempo_ruta
from politica_final import simular_minuto_a_minuto, points, indicadores, arribos_por_minuto
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

def objetivo(trial):
    # Define los hiperparámetros a ajustar
    tiempo_maximo_entrega = trial.suggest_int("tiempo_maximo_entrega", 180, 180)
    umbral_salida = trial.suggest_float("umbral_salida", 0.5, 2.0)
    peso_min_pedidos = trial.suggest_float("peso_min_pedidos", 0.1, 3.0)
    peso_ventana_tiempo = trial.suggest_float("peso_ventana_tiempo", 0.1, 3.0)
    min_pedidos_salida = trial.suggest_int("min_pedidos_salida", 0, 50)
    x_minutos = trial.suggest_int("x_minutos", 1, 200)  # Añade este parámetro

    # Actualiza los parámetros en la simulación
    parametros = {
        "tiempo_maximo_entrega": tiempo_maximo_entrega,
        "umbral_salida": umbral_salida,
        "peso_min_pedidos": peso_min_pedidos,
        "peso_ventana_tiempo": peso_ventana_tiempo,
        "min_pedidos_salida": min_pedidos_salida,
        "x_minutos": x_minutos,
    }

    simulacion = EstadoSimulacion(minuto_inicial=520, puntos=points, indicadores=indicadores, arribos_por_minuto=arribos_por_minuto)
    camiones = [
        Camion(id=1, tiempo_inicial=0),
        Camion(id=2, tiempo_inicial=0),
        Camion(id=3, tiempo_inicial=0)
    ]

    # Ejecuta la simulación
    simular_minuto_a_minuto(simulacion, camiones, parametros)

    # Calcula el beneficio total obtenido
    benef_acumulado = simulacion.calcular_beneficio_acumulado()
    beneficio_total = simulacion.calcular_porcentaje_beneficio(benef_acumulado)
    
    return beneficio_total




# Crear un estudio de Optuna para maximizar el beneficio
estudio = optuna.create_study(direction="maximize")
estudio.optimize(objetivo, n_trials=100)  # n_trials es el número de iteraciones

# Muestra los mejores parámetros encontrados
print("Mejores parámetros:", estudio.best_params)
print("Mejor beneficio total:", estudio.best_value)

