import matplotlib.pyplot as plt
import pickle
from politica_final import simular_minuto_a_minuto, EstadoSimulacion, Camion
from funciones_complementarias import *
import parametros as p

# Función para inicializar una simulación con una cantidad específica de camiones
def inicializar_simulacion(camion_count, indx):
    # Cargar datos necesarios
    with open('Instancia Tipo IV/scen_points_sample.pkl', 'rb') as f:
        points = pickle.load(f)[indx]
    with open('Instancia Tipo IV/scen_arrivals_sample.pkl', 'rb') as f:
        llegadas = pickle.load(f)[indx]
    with open('Instancia Tipo IV/scen_indicador_sample.pkl', 'rb') as f:
        indicadores = pickle.load(f)[indx]

    arribos_por_minuto = procesar_tiempos([llegadas], division_minutos=60)[0]
    simulacion = EstadoSimulacion(minuto_inicial=520, puntos=points, indicadores=indicadores, arribos_por_minuto=arribos_por_minuto)

    # Crear camiones según el parámetro `camion_count`
    camiones = [Camion(id=i+1, tiempo_inicial=0) for i in range(camion_count)]
    return simulacion, camiones


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


# Configuraciones del análisis
max_beneficio = 100  # Beneficio total deseado como porcentaje
beneficios = []
num_camiones = []


# Análisis de sensibilidad
for camion in range (3, 25):
    beneficios_iteracion=[]
    # Inicializar la simulación y los camiones
    for i in range(100):
        
        simulacion, camiones = inicializar_simulacion(camion, indx=i)
    
    # Ejecutar la simulación
        simular_minuto_a_minuto(simulacion, camiones, parametros_ventana_1, parametros_ventana_2, parametros_ventana_3)
    
    # Calcular beneficio acumulado
        beneficio_total = simulacion.calcular_beneficio_acumulado()
        beneficio_porcentaje = calcular_beneficio(simulacion)
    
    # Guardar resultados
        beneficios_iteracion.append(beneficio_porcentaje)

    promedio_recuperado = sum(beneficios_iteracion)/len(beneficios_iteracion)
    beneficios.append(promedio_recuperado)
    num_camiones.append(camion)
    
    # Condición de parada: si alcanzamos o superamos el 100% de beneficio
    if promedio_recuperado >= max_beneficio:
        break

# Graficar resultados
plt.figure(figsize=(10, 6))
plt.plot(num_camiones, beneficios, marker='o')
plt.title("Análisis de sensibilidad: Beneficio vs Cantidad de camiones")
plt.xlabel("Cantidad de camiones")
plt.ylabel("Beneficio (%)")
plt.grid()
plt.show()

