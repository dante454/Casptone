#    ------------------- ¡¡¡¡ IMPORTANTE !!!!!!--------------------
#Para correr este archivo es necesario comentar la linea 336 del archivo politica_final


import optuna
from funciones_complementarias import EstadoSimulacion, Camion, procesar_tiempos, calcular_tiempo_ruta
from politica_final import simular_minuto_a_minuto, points, indicadores, arribos_por_minuto
import matplotlib.pyplot as plt
import pickle
import pandas as pd


beneficios_incumbentes = []


# Define la función objetivo de Optuna para optimizar los parámetros en tres ventanas de tiempo distintas
def objetivo(trial):
    # Parámetros para la primera ventana de tiempo (desde el inicio hasta el minuto 650)
    parametros_ventana_1 = {
        "min_pedidos_salida": trial.suggest_int("min_pedidos_salida_1", 1, 20),
        "x_minutos": trial.suggest_int("x_minutos_1", 1, 60),
        "limite_area1": trial.suggest_int("limite_area1_1", 90, 150),
        "limite_area2": trial.suggest_int("limite_area2_1", 180, 270),
        "peso_min_pedidos": trial.suggest_float("peso_min_pedidos_1", 0.5, 2.0),
        "peso_ventana_tiempo": trial.suggest_float("peso_ventana_tiempo_1", 0.5, 2.0),
        "umbral_salida": trial.suggest_float("umbral_salida_1", 1.0, 2.0),
        "max_aumento_distancia": trial.suggest_int("max_aumento_distancia_1", 1, 1000),
        "tiempo_necesario_pick_up": trial.suggest_int("tiempo_necesario_pick_up_1", 1, 1500),
        "tiempo_restante_max": trial.suggest_int("tiempo_restante_max_1", 1, 200),
        "max_aumento_distancia_delivery": trial.suggest_int("max_aumento_distancia_delivery_1", 0, 1500),
        "tiempo_necesario_pick_up_en_ruta": trial.suggest_int("tiempo_necesario_pick_up_en_ruta_1", 1, 1500),
        "max_aumento_distancia_en_ruta": trial.suggest_int("max_aumento_distancia_en_ruta_1", 5, 100),
        "maximo_incorporacion_pick_up": trial.suggest_float("maximo_incorporacion_pick_up_1", 0, 15),
        "tiempo_maximo_entrega": 180,  # Valor constante
    }

    # Parámetros para la segunda ventana de tiempo (651 al 780)
    parametros_ventana_2 = {
        "min_pedidos_salida": trial.suggest_int("min_pedidos_salida_2", 1, 20),
        "x_minutos": trial.suggest_int("x_minutos_2", 1, 60),
        "limite_area1": trial.suggest_int("limite_area1_2", 90, 150),
        "limite_area2": trial.suggest_int("limite_area2_2", 180, 270),
        "peso_min_pedidos": trial.suggest_float("peso_min_pedidos_2", 0.5, 2.0),
        "peso_ventana_tiempo": trial.suggest_float("peso_ventana_tiempo_2", 0.5, 2.0),
        "umbral_salida": trial.suggest_float("umbral_salida_2", 1.0, 2.0),
        "max_aumento_distancia": trial.suggest_int("max_aumento_distancia_2", 0, 1000),
        "tiempo_necesario_pick_up": trial.suggest_int("tiempo_necesario_pick_up_2", 1, 1500),
        "tiempo_restante_max": trial.suggest_int("tiempo_restante_max_2", 1, 200),
        "max_aumento_distancia_delivery": trial.suggest_int("max_aumento_distancia_delivery_2", 0, 1500),
        "tiempo_necesario_pick_up_en_ruta": trial.suggest_int("tiempo_necesario_pick_up_en_ruta_2", 1, 1500),
        "max_aumento_distancia_en_ruta": trial.suggest_int("max_aumento_distancia_en_ruta_2", 5, 100),
        "maximo_incorporacion_pick_up": trial.suggest_float("maximo_incorporacion_pick_up_2", 0, 15),
        "tiempo_maximo_entrega": 180,  # Valor constante
    }

    # Parámetros para la tercera ventana de tiempo (781 al 1020)
    parametros_ventana_3 = {
        "min_pedidos_salida": trial.suggest_int("min_pedidos_salida_3", 1, 20),
        "x_minutos": trial.suggest_int("x_minutos_3", 1, 60),
        "limite_area1": trial.suggest_int("limite_area1_3", 90, 150),
        "limite_area2": trial.suggest_int("limite_area2_3", 180, 270),
        "peso_min_pedidos": trial.suggest_float("peso_min_pedidos_3", 0.5, 2.0),
        "peso_ventana_tiempo": trial.suggest_float("peso_ventana_tiempo_3", 0.5, 2.0),
        "umbral_salida": trial.suggest_float("umbral_salida_3", 1.0, 2.0),
        "max_aumento_distancia": trial.suggest_int("max_aumento_distancia_3", 1, 1000),
        "tiempo_necesario_pick_up": trial.suggest_int("tiempo_necesario_pick_up_3", 1, 1500),
        "tiempo_restante_max": trial.suggest_int("tiempo_restante_max_3", 1, 200),
        "max_aumento_distancia_delivery": trial.suggest_int("max_aumento_distancia_delivery_3", 0, 1500),
        "tiempo_necesario_pick_up_en_ruta": trial.suggest_int("tiempo_necesario_pick_up_en_ruta_3", 1, 1500),
        "max_aumento_distancia_en_ruta": trial.suggest_int("max_aumento_distancia_en_ruta_3", 5, 100),
        "maximo_incorporacion_pick_up": trial.suggest_float("maximo_incorporacion_pick_up_3", 0, 15),
        "tiempo_maximo_entrega": 195,  # Valor constante
    }

    # Inicializar listas para almacenar los resultados de los KPIs
    beneficios = []

    # Ejecutar la simulación para cada uno de los 100 días
    for dia in range(5):
        print(f"Simulando el día {dia + 1}...")

        with open('Instancia Tipo IV/scen_points_sample.pkl', 'rb') as f:
            puntos_simulaciones = pickle.load(f)
        with open('Instancia Tipo IV/scen_arrivals_sample.pkl', 'rb') as f:
            llegadas_simulaciones = pickle.load(f)
        with open('Instancia Tipo IV/scen_indicador_sample.pkl', 'rb') as f:
            indicadores_simulaciones = pickle.load(f)
        # Cargar los datos específicos del día
        points = puntos_simulaciones[dia]
        llegadas = llegadas_simulaciones[dia]
        indicadores = indicadores_simulaciones[dia]

        # Procesar los arribos por minuto para este día
        arribos_por_minuto = procesar_tiempos([llegadas], division_minutos=60)[0]

        # Inicializar la simulación para el día
        simulacion = EstadoSimulacion(minuto_inicial=520, puntos=points, indicadores=indicadores, arribos_por_minuto=arribos_por_minuto)

        # Inicializar los camiones
        camiones = [
            Camion(id=1, tiempo_inicial=0),
            Camion(id=2, tiempo_inicial=0),
            Camion(id=3, tiempo_inicial=0)
        ]

    #    ------------------- ¡¡¡¡ IMPORTANTE !!!!!! --------------------
    #SI es para la solucion inicial ejecutar la siguente linea
        simular_minuto_a_minuto(simulacion, camiones, parametros_ventana_1, parametros_ventana_2, parametros_ventana_3)

    # Calcula el beneficio total obtenido
        benef_acumulado = simulacion.calcular_beneficio_acumulado()
        beneficio_total = simulacion.calcular_porcentaje_beneficio(benef_acumulado)
        beneficios.append(beneficio_total)

    promedio_recuperado = sum(beneficios)/len(beneficios)

    
    return promedio_recuperado

def registrar_beneficio(study, trial):
    beneficios_incumbentes.append(study.best_value)




# Crear un estudio de Optuna para maximizar el beneficio
estudio = optuna.create_study(direction="maximize")
estudio.optimize(objetivo, n_trials=200, callbacks=[registrar_beneficio])  # n_trials es el número de iteraciones

# Obtener los mejores parámetros y su valor de beneficio total
mejores_parametros = estudio.best_params
mejor_beneficio = estudio.best_value

# Separar los parámetros en diccionarios por ventana de tiempo
#esto es para luego poder utilizarlos 
mejores_parametros_ventana_1 = {k.replace('_1', ''): v for k, v in mejores_parametros.items() if '_1' in k}
mejores_parametros_ventana_2 = {k.replace('_2', ''): v for k, v in mejores_parametros.items() if '_2' in k}
mejores_parametros_ventana_3 = {k.replace('_3', ''): v for k, v in mejores_parametros.items() if '_3' in k}

print()
print(mejores_parametros_ventana_1)
print()
print(mejores_parametros_ventana_2)
print()
print(mejores_parametros_ventana_3)
print()

# Mostrar los mejores parámetros en forma de tabla
print("Mejores beneficio")
print(mejor_beneficio)

plt.figure(figsize=(10, 6))
plt.plot(beneficios_incumbentes, label="Beneficio Incumbente")
plt.title("Progreso del Beneficio Incumbente por Iteración")
plt.xlabel("Iteración")
plt.ylabel("Beneficio Incumbente")
plt.legend()
plt.grid()
plt.show()