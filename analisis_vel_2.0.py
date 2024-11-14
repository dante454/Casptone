import optuna
import matplotlib.pyplot as plt
import pickle
from politica_final import simular_minuto_a_minuto, EstadoSimulacion, Camion
from funciones_caso_base import procesar_tiempos

# Función para inicializar una simulación con una cantidad específica de camiones y velocidad específica
def inicializar_simulacion(camion_count, velocidad, indx):
    # Cargar datos necesarios
    with open('Instancia Tipo IV/scen_points_sample.pkl', 'rb') as f:
        points = pickle.load(f)[indx]
    with open('Instancia Tipo IV/scen_arrivals_sample.pkl', 'rb') as f:
        llegadas = pickle.load(f)[indx]
    with open('Instancia Tipo IV/scen_indicador_sample.pkl', 'rb') as f:
        indicadores = pickle.load(f)[indx]

    arribos_por_minuto = procesar_tiempos([llegadas], division_minutos=60)[0]
    simulacion = EstadoSimulacion(minuto_inicial=520, puntos=points, indicadores=indicadores, arribos_por_minuto=arribos_por_minuto)

    # Crear camiones con la velocidad especificada
    camiones = [Camion(id=i+1, tiempo_inicial=0) for i in range(camion_count)]
    for camion in camiones:
        camion.velocidad = velocidad
    return simulacion, camiones

# Función para optimización diaria con Optuna
def optimizacion_con_optuna(points, arribos_por_minuto, indicadores, velocidad, iteraciones=100):
    def objetivo_diario(trial):
        # Configuración de parámetros optimizados para cada ventana de tiempo
        parametros_ventana_1 = {
        "min_pedidos_salida": trial.suggest_int("min_pedidos_salida_1", 1, 20),
        "porcentaje_reduccion_distancia": trial.suggest_int("porcentaje_reduccion_distancia_1", 30, 70),
        "max_puntos_eliminados": trial.suggest_int("max_puntos_eliminados_1", 5, 20),
        "x_minutos": trial.suggest_int("x_minutos_1", 1, 60),
        "limite_area1": trial.suggest_int("limite_area1_1", 90, 150),
        "limite_area2": trial.suggest_int("limite_area2_1", 180, 270),
        "peso_min_pedidos": trial.suggest_float("peso_min_pedidos_1", 0.5, 2.0),
        "peso_ventana_tiempo": trial.suggest_float("peso_ventana_tiempo_1", 0.5, 2.0),
        "umbral_salida": trial.suggest_float("umbral_salida_1", 1.0, 2.0),
        "tiempo_minimo_pickup": trial.suggest_int("tiempo_minimo_pickup_1", 15, 45),
        "max_aumento_distancia": trial.suggest_int("max_aumento_distancia_1", 5, 20),
        "tiempo_necesario_pick_up": trial.suggest_int("tiempo_necesario_pick_up_1", 1, 1500),
        "tiempo_restante_max": trial.suggest_int("tiempo_restante_max_1", 1, 200),
        "max_aumento_distancia_delivery": trial.suggest_int("max_aumento_distancia_delivery_1", 0, 1500),
        "tiempo_maximo_entrega": 180,  # Valor constante
    }

    # Parámetros para la segunda ventana de tiempo (651 al 780)
        parametros_ventana_2 = {
        "min_pedidos_salida": trial.suggest_int("min_pedidos_salida_2", 1, 20),
        "porcentaje_reduccion_distancia": trial.suggest_int("porcentaje_reduccion_distancia_2", 30, 70),
        "max_puntos_eliminados": trial.suggest_int("max_puntos_eliminados_2", 5, 20),
        "x_minutos": trial.suggest_int("x_minutos_2", 1, 60),
        "limite_area1": trial.suggest_int("limite_area1_2", 90, 150),
        "limite_area2": trial.suggest_int("limite_area2_2", 180, 270),
        "peso_min_pedidos": trial.suggest_float("peso_min_pedidos_2", 0.5, 2.0),
        "peso_ventana_tiempo": trial.suggest_float("peso_ventana_tiempo_2", 0.5, 2.0),
        "umbral_salida": trial.suggest_float("umbral_salida_2", 1.0, 2.0),
        "tiempo_minimo_pickup": trial.suggest_int("tiempo_minimo_pickup_2", 15, 45),
        "max_aumento_distancia": trial.suggest_int("max_aumento_distancia_2", 5, 20),
        "tiempo_necesario_pick_up": trial.suggest_int("tiempo_necesario_pick_up_2", 1, 1500),
        "tiempo_restante_max": trial.suggest_int("tiempo_restante_max_2", 1, 200),
        "max_aumento_distancia_delivery": trial.suggest_int("max_aumento_distancia_delivery_2", 0, 1500),
        "tiempo_maximo_entrega": 180,  # Valor constante
    }

    # Parámetros para la tercera ventana de tiempo (781 al 1020)
        parametros_ventana_3 = {
        "min_pedidos_salida": trial.suggest_int("min_pedidos_salida_3", 1, 20),
        "porcentaje_reduccion_distancia": trial.suggest_int("porcentaje_reduccion_distancia_3", 30, 70),
        "max_puntos_eliminados": trial.suggest_int("max_puntos_eliminados_3", 5, 20),
        "x_minutos": trial.suggest_int("x_minutos_3", 1, 60),
        "limite_area1": trial.suggest_int("limite_area1_3", 90, 150),
        "limite_area2": trial.suggest_int("limite_area2_3", 180, 270),
        "peso_min_pedidos": trial.suggest_float("peso_min_pedidos_3", 0.5, 2.0),
        "peso_ventana_tiempo": trial.suggest_float("peso_ventana_tiempo_3", 0.5, 2.0),
        "umbral_salida": trial.suggest_float("umbral_salida_3", 1.0, 2.0),
        "tiempo_minimo_pickup": trial.suggest_int("tiempo_minimo_pickup_3", 15, 45),
        "max_aumento_distancia": trial.suggest_int("max_aumento_distancia_3", 5, 20),
        "tiempo_necesario_pick_up": trial.suggest_int("tiempo_necesario_pick_up_3", 1, 1500),
        "tiempo_restante_max": trial.suggest_int("tiempo_restante_max_3", 1, 200),
        "max_aumento_distancia_delivery": trial.suggest_int("max_aumento_distancia_delivery_3", 0, 1500),
        "tiempo_maximo_entrega": 180,  # Valor constante
    }
        
        # Inicializar la simulación para este día
        simulacion = EstadoSimulacion(minuto_inicial=520, puntos=points, indicadores=indicadores, arribos_por_minuto=arribos_por_minuto)
        camiones = [Camion(id=j+1, tiempo_inicial=0) for j in range(3)]
        for camion in camiones:
            camion.velocidad = velocidad
        
        # Ejecutar la simulación con los parámetros optimizados
        simular_minuto_a_minuto(simulacion, camiones, parametros_ventana_1, parametros_ventana_2, parametros_ventana_3)
        
        benef_acumulado = simulacion.calcular_beneficio_acumulado()
        beneficio_total = simulacion.calcular_porcentaje_beneficio(benef_acumulado)
        return beneficio_total

    # Configuración del estudio de Optuna para maximizar el beneficio
    estudio = optuna.create_study(direction="maximize")
    estudio.optimize(objetivo_diario, n_trials=iteraciones)
    return estudio.best_params

# Función para convertir la velocidad a metros/minuto
def v_a_m(v):
    return ((v * 1000) / 60)

# Configuraciones del análisis
velocidad_inicial = v_a_m(25)  # Velocidad inicial en km/h
incremento_velocidad = v_a_m(5)  # Incremento en km/h por iteración
velocidad_maxima = v_a_m(200)  # Velocidad máxima deseada
beneficios_promedio = []
velocidades = [i for i in range(25, 200, 5)]

# Análisis de sensibilidad
for velocidad_kmh in range(25, 200, 5):
    velocidad = v_a_m(velocidad_kmh)
    beneficios_iteracion = []

    for i in range(100):  # 100 días para cada velocidad
        # Cargar un conjunto diferente de puntos, arribos e indicadores
        with open('Instancia Tipo IV/scen_points_sample.pkl', 'rb') as f:
            points = pickle.load(f)[i]
        with open('Instancia Tipo IV/scen_arrivals_sample.pkl', 'rb') as f:
            llegadas = pickle.load(f)[i]
        with open('Instancia Tipo IV/scen_indicador_sample.pkl', 'rb') as f:
            indicadores = pickle.load(f)[i]
        
        arribos_por_minuto = procesar_tiempos([llegadas], division_minutos=60)[0]

        # Optimización de parámetros para el día
        mejores_parametros = optimizacion_con_optuna(points, arribos_por_minuto, indicadores, velocidad, iteraciones=100)

        # Inicializar simulación y camiones
        simulacion, camiones = inicializar_simulacion(camion_count=3, velocidad=velocidad, indx=i)

        # Ejecutar la simulación con los parámetros optimizados
        simular_minuto_a_minuto(simulacion, camiones, mejores_parametros['parametros_ventana_1'], mejores_parametros['parametros_ventana_2'], mejores_parametros['parametros_ventana_3'])
        
        # Calcular el beneficio de la iteración
        benef_acumulado = simulacion.calcular_beneficio_acumulado()
        beneficio_total = simulacion.calcular_porcentaje_beneficio(benef_acumulado)
        beneficios_iteracion.append(beneficio_total)

    # Calcular el beneficio promedio para la velocidad actual
    promedio_beneficio = sum(beneficios_iteracion) / len(beneficios_iteracion)
    beneficios_promedio.append(promedio_beneficio)

# Graficar resultados
plt.figure(figsize=(10, 6))
plt.plot(velocidades, beneficios_promedio, marker='o')
plt.title("Análisis de sensibilidad: Beneficio vs Velocidad del camión")
plt.xlabel("Velocidad del camión (km/h)")
plt.ylabel("Beneficio Promedio (%)")
plt.grid()
plt.show()


