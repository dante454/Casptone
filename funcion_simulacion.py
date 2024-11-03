import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
import pickle
import parametros as p

# Función para cargar los datos desde un archivo pickle
def cargar_datos(ruta):
    with open(ruta, 'rb') as file:
        datos = pickle.load(file)
    return datos

# 1. Función para generar puntos aleatorios (sin clústeres)
def generar_puntos(num_puntos, rango_x=(0, 20000), rango_y=(0, 20000)):
    x = np.random.uniform(rango_x[0], rango_x[1], num_puntos)
    y = np.random.uniform(rango_y[0], rango_y[1], num_puntos)
    return np.column_stack((x, y))

# 2. Función para generar indicadores binarios (0 para delivery, 1 para pick-up)
def generar_indicadores(num_puntos, probabilidad_pickup):
    return np.random.binomial(1, probabilidad_pickup, num_puntos)

# 3. Función para graficar los puntos (independiente de si son generados o con clústeres)
def graficar_puntos(puntos, indicadores):
    plt.figure(figsize=(10, 10))

    # Colores para los diferentes indicadores
    color_delivery = 'blue'  # Color para delivery (0)
    color_pickup = 'red'     # Color para pick-up (1)
    colores = np.where(indicadores == 1, color_pickup, color_delivery)

    # Graficar los puntos con los colores correspondientes
    plt.scatter(puntos[:, 0], puntos[:, 1], color=colores, s=10, alpha=0.7)
    
    plt.xlabel('Coordenada X')
    plt.ylabel('Coordenada Y')
    plt.title('Puntos de Delivery y Pick-Up en el Mapa')
    plt.grid(True)
    plt.xlim(0, 20000)
    plt.ylim(0, 20000)
    plt.show()

# Función para generar puntos con clústeres, utilizando los centroides y desviaciones predefinidos
def generar_puntos_con_clusters(centroides, num_puntos, desviaciones):
    puntos_simulados = []
    num_clusters = len(centroides)

    for _ in range(num_puntos):
        # Elegir un clúster aleatoriamente
        cluster_id = np.random.randint(0, num_clusters)
        centroide = centroides[cluster_id]
        desviacion = desviaciones[cluster_id]

        # Generar un punto aleatorio alrededor del centroide
        punto_simulado = np.random.normal(loc=centroide, scale=desviacion)
        puntos_simulados.append(punto_simulado)

    return np.array(puntos_simulados)


# Función principal para generar la simulación con o sin clústeres
def generar_simulacion(num_puntos, probabilidad_pick_up, usar_clusters=False, centroides=None, desviaciones=None):
    if usar_clusters and centroides is not None and desviaciones is not None:
        # Generar puntos basados en los clústeres predefinidos
        puntos = generar_puntos_con_clusters(centroides, num_puntos, desviaciones)
    else:
        # Generar puntos de manera uniforme (sin clústeres)
        puntos = generar_puntos(num_puntos)

    # Generar indicadores binarios (pick-up o delivery)
    indicadores = generar_indicadores(num_puntos, probabilidad_pick_up)

    # Graficar los puntos generados
    graficar_puntos(puntos, indicadores)


#Funcion que se utilizo para encontrar los clasters
def obtener_parametros_claster(ruta_datos, numero_clases=3):
    # Cargar los datos reales desde un archivo pickle
    datos_pickle = cargar_datos(ruta_datos)

    # Unir los puntos de todas las simulaciones en un solo arreglo
    puntos_totales = np.concatenate(datos_pickle)

    # Identificar clústeres usando KMeans
    kmeans = KMeans(n_clusters=numero_clases)
    kmeans.fit(puntos_totales)

    # Obtener los centroides de los clústeres
    centroides = kmeans.cluster_centers_

    # Calcular las desviaciones estándar de cada clúster
    cluster_labels = kmeans.predict(puntos_totales)
    desviaciones = []
    for i in range(numero_clases):
        puntos_cluster = puntos_totales[cluster_labels == i]
        desviacion = np.std(puntos_cluster, axis=0)
        desviaciones.append(desviacion)

    # Devolver los centroides y desviaciones como una tupla
    return centroides, desviaciones


# Generar instancia I
generar_simulacion(num_puntos=10000, probabilidad_pick_up=0.38, usar_clusters=False)

# Generar instancia III
generar_simulacion(num_puntos=10000, probabilidad_pick_up=0.38, usar_clusters=True, centroides=p.centroides_instancia_III, 
                desviaciones=p.desviacion_estandar_instancia_III)

# Generar instancia IV
generar_simulacion(num_puntos=10000, probabilidad_pick_up=0.38, usar_clusters=True, centroides=p.centroides_instancia_IV, 
                desviaciones=p.desviacion_estandar_instancia_IV)


