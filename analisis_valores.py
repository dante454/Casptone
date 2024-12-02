
import matplotlib.pyplot as plt
import pickle
from  politica_final import Camion
from analisis_valores_ruteo import *
from  funciones_complementarias import procesar_tiempos
import parametros as p

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



# Análisis de sensibilidad
def analisis_sensibilidad(pickups, deliveries):
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


    instancia_archivo = 'Instancia Tipo IV'

    if instancia_archivo == 'Instancia Tipo I':
        parametros_ventana_1 = p.parametros_ventana_1_instancia_1
        parametros_ventana_2 = p.parametros_ventana_2_instancia_1
        parametros_ventana_3 = p.parametros_ventana_3_instancia_1
    elif instancia_archivo == 'Instancia Tipo II':
        parametros_ventana_1 = p.parametros_ventana_1_instancia_2
        parametros_ventana_2 = p.parametros_ventana_2_instancia_2
        parametros_ventana_3 = p.parametros_ventana_3_instancia_2
    elif instancia_archivo == 'Instancia Tipo III':
        parametros_ventana_1 = p.parametros_ventana_1_instancia_3
        parametros_ventana_2 = p.parametros_ventana_2_instancia_3
        parametros_ventana_3 = p.parametros_ventana_3_instancia_3
    elif instancia_archivo == 'Instancia Tipo IV':
        parametros_ventana_1 = p.parametros_ventana_1_instancia_4
        parametros_ventana_2 = p.parametros_ventana_2_instancia_4
        parametros_ventana_3 = p.parametros_ventana_3_instancia_4

    for i in range(100):
        points = puntos_simulaciones[i]
        llegadas = llegadas_simulaciones[i]
        indicadores = indicadores_simulaciones[i]
        arribos_por_minuto = procesar_tiempos([llegadas], division_minutos=60)[0]

        simulacion = EstadoSimulacion2(minuto_inicial=520, puntos=points, indicadores=indicadores, arribos_por_minuto=arribos_por_minuto)
        camiones = [Camion(id=j+1, tiempo_inicial=0) for j in range(3)]
        simular_minuto_a_minuto2(
            simulacion, camiones, parametros_ventana_1, parametros_ventana_2, parametros_ventana_3,
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
    (2, 1),
    (1, 3),
    (3, 1),
    (1, 5),
    (5, 1),
]

promedios_pickups = []
promedios_deliveries = []
etiquetas = []

for pickups, deliveries in combinaciones:
    promedio_pickups, promedio_deliveries = analisis_sensibilidad( pickups=pickups, deliveries=deliveries)
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