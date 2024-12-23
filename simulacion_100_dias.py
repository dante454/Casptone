import pickle
import pandas as pd
from funciones_complementarias import *
import parametros as p

#    -------------------  ¡¡¡¡ IMPORTANTE !!!!!! --------------------

#si se quiere simular Solucion inicial/Politica final dejar esta linea, si no comentarla
from politica_final import simular_minuto_a_minuto

#si se quiere ejecutar Caso_base ejecutar esta linea, si no comentarla:
#from caso_base_2 import simular_minuto_a_minuto



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



# Cargar los datos de la simulación para los 100 días
with open(f'{instancia_archivo}/scen_points_sample.pkl', 'rb') as f:
    puntos_simulaciones = pickle.load(f)
with open(f'{instancia_archivo}/scen_arrivals_sample.pkl', 'rb') as f:
    llegadas_simulaciones = pickle.load(f)
with open(f'{instancia_archivo}/scen_indicador_sample.pkl', 'rb') as f:
    indicadores_simulaciones = pickle.load(f)

# Inicializar listas para almacenar los resultados de los KPIs
beneficios = []
distancias_totales = []
tiempos_promedio_entrega = []
pickups_completados = []
deliveries_completados = []
numero_rutas = []
beneficio_intervalos =[]
deliveries_por_intervalo = []
pickups_por_intervalo = []

# Ejecutar la simulación para cada uno de los 100 días
for dia in range(100):
    print(f"Simulando el día {dia + 1}...")

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

    #si se esta simulando para el caso base ejecutar las siguentes lineas: SINO, COMENTARLAS
    #x_minutos = 60  
    #simular_minuto_a_minuto(simulacion, camiones, x_minutos)

    # Recopilar los KPIs del día
    beneficio_total = calcular_beneficio(simulacion)
    distancia_total = calcular_distancia_total(camiones)
    tiempos_respuesta = [pedido.tiempo_entrega for pedido in simulacion.pedidos_entregados if pedido.tiempo_entrega is not None]
    tiempo_respuesta_promedio = sum(tiempos_respuesta) / len(tiempos_respuesta)
    cantidad_pickups = sum(1 for pedido in simulacion.pedidos_entregados if pedido.indicador == 1)
    cantidad_deliveries = sum(1 for pedido in simulacion.pedidos_entregados if pedido.indicador == 0)
    rutas = sum(len(camion.rutas) for camion in camiones )



    tiempos_promedio_entrega.append(tiempo_respuesta_promedio)
    beneficios.append(beneficio_total)
    distancias_totales.append(distancia_total)
    pickups_completados.append(cantidad_pickups)
    deliveries_completados.append(cantidad_deliveries)
    numero_rutas.append(rutas)
    beneficio_intervalos.append(simulacion.beneficio_por_intervalo)
    deliveries_por_intervalo.append(simulacion.deliveries_intervalos)
    pickups_por_intervalo.append(simulacion.pickups_intervalos)



#calcualr % minimo y maximo obtenido
benef_max = max(beneficios)
benef_min = min(beneficios)
dia_max_ganancia = beneficios.index(benef_max) 

# Calcular los KPIs promedio
beneficio_promedio = sum(beneficios) / len(beneficios)
distancia_promedio = sum(distancias_totales) / len(distancias_totales)
tiempo_promedio_entrega = sum(tiempos_promedio_entrega) / len(tiempos_promedio_entrega)
pickup_promedio = sum(pickups_completados) / len(pickups_completados)
delivery_promedio = sum(deliveries_completados) / len(deliveries_completados)
rutas_promedio = sum(numero_rutas) / len(numero_rutas)
largo_rutas_prom = distancia_promedio / rutas_promedio


# Mostrar los resultados
print('\n', '--'*16)
print("\nResultados de la Simulación de 100 Días:\n")
print(f"Beneficio Promedio Capturado en porcentaje: {beneficio_promedio}")
print(f'Beneficio maximo en porcentaje: {benef_max} en el dia {dia_max_ganancia}')
print(f'Beneficio minimo en porcentaje: {benef_min}\n')
print(f"Distancia Promedio Recorrida: {distancia_promedio}")
print(f"Tiempo Promedio de Entrega: {tiempo_promedio_entrega}\n")
print(f"Pickups Completados Promedio: {pickup_promedio}")
print(f"Deliveries Completados Promedio: {delivery_promedio}")
print(f'Largo de ruta promedio: {largo_rutas_prom}')
print(f'Rutas promedio {rutas_promedio}')

intervalos_agrupados = {}
for dia in beneficio_intervalos:
    for minuto, beneficio in dia:
        if minuto not in intervalos_agrupados:
            intervalos_agrupados[minuto] = []
        intervalos_agrupados[minuto].append(beneficio)

# Paso 2: Calcular el promedio por minuto
minutos = sorted(intervalos_agrupados.keys())
promedio_beneficio_por_minuto = [
    np.mean(intervalos_agrupados[minuto]) for minuto in minutos
]

# Paso 3: Graficar los resultados
plt.figure(figsize=(10, 6))
plt.plot(minutos, promedio_beneficio_por_minuto, marker="o", label="Beneficio Promedio")
plt.title("Tendencia del Beneficio Promedio por Intervalo de Tiempo")
plt.xlabel("Minuto")
plt.ylabel("Beneficio (%)")
plt.grid(True, linestyle="--", alpha=0.7)
plt.legend()
plt.tight_layout()

# Mostrar el gráfico
plt.show()

intervalos_deliveries_agrupados = {}
intervalos_pickups_agrupados = {}

for dia in deliveries_por_intervalo:
    for minuto, porcentaje_delivery in dia:
        if minuto not in intervalos_deliveries_agrupados:
            intervalos_deliveries_agrupados[minuto] = []
        intervalos_deliveries_agrupados[minuto].append(porcentaje_delivery)

for dia in pickups_por_intervalo:
    for minuto, porcentaje_pickup in dia:
        if minuto not in intervalos_pickups_agrupados:
            intervalos_pickups_agrupados[minuto] = []
        intervalos_pickups_agrupados[minuto].append(porcentaje_pickup)

# Paso 2: Calcular el promedio por intervalo
minutos = sorted(intervalos_deliveries_agrupados.keys())  # Usamos los mismos minutos para ambos porcentajes
promedio_deliveries_por_minuto = [
    sum(intervalos_deliveries_agrupados[minuto]) / len(intervalos_deliveries_agrupados[minuto])
    for minuto in minutos
]

promedio_pickups_por_minuto = [
    sum(intervalos_pickups_agrupados[minuto]) / len(intervalos_pickups_agrupados[minuto])
    for minuto in minutos
]

# Paso 3: Graficar los promedios
import matplotlib.pyplot as plt

plt.figure(figsize=(10, 6))
plt.plot(minutos, promedio_deliveries_por_minuto, label='Promedio Deliveries', marker='o')
plt.plot(minutos, promedio_pickups_por_minuto, label='Promedio Pickups', marker='x')

plt.xlabel('Minuto')
plt.ylabel('Porcentaje')
plt.title('Promedio de Porcentajes de Deliveries y Pickups por Intervalos')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()