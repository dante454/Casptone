
import matplotlib.pyplot as plt
import pickle
from  politica_final import Camion
from ruteo_analisis_valores import *
from  funciones_caso_base import procesar_tiempos
import optuna

def calcular_porcentaje_beneficio(simulacion, beneficio_acumulado, valor_deliv, valor_pick):
        """Calcula el porcentaje del beneficio respecto al máximo beneficio disponible."""
        beneficio_maximo = calcular_beneficio_maximo(simulacion, valor_deliv, valor_pick)
        if beneficio_maximo == 0:
            return 0  # Evita división por cero
        return (beneficio_acumulado / beneficio_maximo) * 100


# Función para calcular el beneficio acumulado
def calcular_beneficio_acumulado(simulacion, valor_deliv, valor_pick):
    return sum(valor_pick if pedido.indicador == 1 else valor_deliv 
               for pedido in simulacion.pedidos_entregados)




# Función para optimizar parámetros usando Optuna
def funcion_opti_optuna(points, arribos_por_minuto, indicadores, iter, valor_deliv, valor_pick):
    def objetivo(trial):
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

        simulacion = EstadoSimulacion2(minuto_inicial=520, puntos=points, indicadores=indicadores, arribos_por_minuto=arribos_por_minuto)
        camiones = [Camion(id=i+1, tiempo_inicial=0) for i in range(3)]
        simular_minuto_a_minuto2(simulacion, camiones, parametros_ventana_1, parametros_ventana_2, parametros_ventana_3, valor_pick, valor_deliv)
        
        benef_acumulado = calcular_beneficio_acumulado(simulacion, valor_deliv, valor_pick)
        beneficio_total = calcular_porcentaje_beneficio(simulacion, benef_acumulado, valor_deliv, valor_pick)
        return beneficio_total

    estudio = optuna.create_study(direction="maximize")
    estudio.optimize(objetivo, n_trials=iter)
    mejores_parametros = estudio.best_params
    # Dividir parámetros por ventana
    return [
        {k.replace('_1', ''): v for k, v in mejores_parametros.items() if '_1' in k},
        {k.replace('_2', ''): v for k, v in mejores_parametros.items() if '_2' in k},
        {k.replace('_3', ''): v for k, v in mejores_parametros.items() if '_3' in k},
    ]

# Análisis de sensibilidad
def analisis_sensibilidad(iteraciones_optuna, pickups, deliveries):
    proporcion_pickups = []  # Lista para almacenar las proporciones de pickups tomados
    proporcion_deliveries = []  # Lista para almacenar las proporciones de deliveries tomados

    # Almacenar resultados de las 100 iteraciones
    resultados_pickups_iteraciones = []
    resultados_deliveries_iteraciones = []

    with open('Instancia Tipo IV/scen_points_sample.pkl', 'rb') as f:
        puntos_simulaciones = pickle.load(f)
    with open('Instancia Tipo IV/scen_arrivals_sample.pkl', 'rb') as f:
        llegadas_simulaciones = pickle.load(f)
    with open('Instancia Tipo IV/scen_indicador_sample.pkl', 'rb') as f:
        indicadores_simulaciones = pickle.load(f)

    points = puntos_simulaciones[5]
    llegadas = llegadas_simulaciones[5]
    indicadores = indicadores_simulaciones[5]
    arribos_por_minuto = procesar_tiempos([llegadas], division_minutos=60)[0]

    mejores_parametros = funcion_opti_optuna(points, arribos_por_minuto, indicadores, iteraciones_optuna, deliveries, pickups)

    for i in range(100):
        points = puntos_simulaciones[i]
        llegadas = llegadas_simulaciones[i]
        indicadores = indicadores_simulaciones[i]
        arribos_por_minuto = procesar_tiempos([llegadas], division_minutos=60)[0]

        simulacion = EstadoSimulacion2(minuto_inicial=520, puntos=points, indicadores=indicadores, arribos_por_minuto=arribos_por_minuto)
        camiones = [Camion(id=j+1, tiempo_inicial=0) for j in range(3)]
        simular_minuto_a_minuto2(
            simulacion, camiones, mejores_parametros[0], mejores_parametros[1], mejores_parametros[2],
            pickups, deliveries  # Pasa los valores a las funciones internas
        )

        total_pickups = sum(1 for pedido in simulacion.pedidos_entregados if pedido.indicador == 1)
        total_deliveries = sum(1 for pedido in simulacion.pedidos_entregados if pedido.indicador == 0)
        pickups_disponibles = sum(1 for pedido in simulacion.pedidos_disponibles + simulacion.pedidos_no_disponibles + simulacion.pedidos_entregados if pedido.indicador == 1)
        deliveries_disponibles = sum(1 for pedido in simulacion.pedidos_disponibles + simulacion.pedidos_no_disponibles + simulacion.pedidos_entregados if pedido.indicador != 1)

        # Calcular proporciones y evitar división por cero
        pickup_rate = (total_pickups / pickups_disponibles) * 100 if pickups_disponibles > 0 else 0
        delivery_rate = (total_deliveries / deliveries_disponibles) * 100 if deliveries_disponibles > 0 else 0

        # Guardar resultados individuales
        proporcion_pickups.append(pickup_rate)
        proporcion_deliveries.append(delivery_rate)

        # Guardar proporciones de las iteraciones
        resultados_pickups_iteraciones.append(pickup_rate)
        resultados_deliveries_iteraciones.append(delivery_rate)

    # Calcular promedios de las 100 iteraciones
    promedio_pickups = sum(resultados_pickups_iteraciones) / len(resultados_pickups_iteraciones)
    promedio_deliveries = sum(resultados_deliveries_iteraciones) / len(resultados_deliveries_iteraciones)

    print(f"Promedios para Pickup = {pickups}, Delivery = {deliveries}:")
    print(f"  Promedio de Pickups: {promedio_pickups}%")
    print(f"  Promedio de Deliveries: {promedio_deliveries}%")

    return promedio_pickups, promedio_deliveries


# Graficar promedios para diferentes combinaciones
combinaciones = [
    (1, 2),
    (2, 1),
    (1, 3),
    (3, 1),
]

promedios_pickups = []
promedios_deliveries = []
etiquetas = []

for pickups, deliveries in combinaciones:
    promedio_pickups, promedio_deliveries = analisis_sensibilidad(iteraciones_optuna=100, pickups=pickups, deliveries=deliveries)
    # Aquí ya son valores flotantes, no listas
    promedios_pickups.append(promedio_pickups)  # Agrega el promedio directamente
    promedios_deliveries.append(promedio_deliveries)
    etiquetas.append(f"Pickup={pickups}, Delivery={deliveries}")

# Crear gráfico
plt.figure(figsize=(12, 6))
plt.plot(range(len(combinaciones)), promedios_pickups, label='Promedio de Pickups (%)', marker='o')
plt.plot(range(len(combinaciones)), promedios_deliveries, label='Promedio de Deliveries (%)', marker='s')
plt.title("Promedio de Proporciones: Pickups vs Deliveries (100 simulaciones por combinación)")
plt.xticks(range(len(combinaciones)), etiquetas, rotation=45, ha='right')
plt.xlabel("Combinaciones de Pickup y Delivery")
plt.ylabel("Promedio de Proporción Tomada (%)")
plt.legend()
plt.grid()
plt.tight_layout()
plt.show()