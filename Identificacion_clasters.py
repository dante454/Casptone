import pickle
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans

# Función para leer los datos desde el archivo pickle
def leer_datos_pickle(nombre_archivo):
    with open(nombre_archivo, 'rb') as archivo:
        datos = pickle.load(archivo)
    return datos

# Función original para identificar clústeres (sin cambios)
def identificar_clusters(points, numero_clases):
    puntos_totales = np.concatenate(points)  # Unimos todos los puntos de todas las simulaciones
    kmeans = KMeans(n_clusters=numero_clases)
    kmeans.fit(puntos_totales)
    print(kmeans)
    return kmeans

# Función para simular puntos basados en los clústeres utilizando la desviación estándar real
def simular_puntos_desde_clusters_con_desviacion_real(kmeans, points, numero_puntos_simulacion):
    """
    Simula nuevos puntos a partir de los centroides identificados en los clústeres, utilizando la desviación
    estándar real de los datos originales para cada clúster.
    
    :param kmeans: El modelo KMeans ajustado que contiene los centroides
    :param points: Los puntos originales utilizados para calcular las desviaciones estándar
    :param numero_puntos_simulacion: Número de puntos a simular
    :return: Array de puntos simulados
    """
    puntos_totales = np.concatenate(points)
    cluster_labels = kmeans.predict(puntos_totales)
    
    centroides = kmeans.cluster_centers_
    num_clusters = len(centroides)
    
    desviaciones = []
    
    # Calculamos la desviación estándar de los puntos dentro de cada clúster
    for i in range(num_clusters):
        puntos_cluster = puntos_totales[cluster_labels == i]
        desviacion = np.std(puntos_cluster, axis=0)  # Desviación estándar en las dimensiones x e y
        desviaciones.append(desviacion)
    
    puntos_simulados = []
    
    for _ in range(numero_puntos_simulacion):
        # Elegimos un clúster aleatorio para simular un punto
        cluster_id = np.random.randint(0, num_clusters)
        centroide = centroides[cluster_id]
        
        # Generamos un punto alrededor del centroide elegido, con la desviación estándar real del clúster
        punto_simulado = np.random.normal(loc=centroide, scale=desviaciones[cluster_id])
        puntos_simulados.append(punto_simulado)
    
    return np.array(puntos_simulados)

# Función para graficar los puntos originales, los clústeres y los puntos simulados
def graficar_clusters_y_simulacion(points, numero_clases, kmeans, puntos_simulados):
    plt.figure(figsize=(10, 6))
    colores = plt.cm.viridis(np.linspace(0, 1, numero_clases))
    
    # Graficar los puntos de cada simulación y su correspondiente clúster
    for i, puntos_simulacion in enumerate(points):
        puntos_simulacion = np.array(puntos_simulacion)
        cluster_labels = kmeans.predict(puntos_simulacion)
        
        for j in range(numero_clases):
            cluster_puntos = puntos_simulacion[cluster_labels == j]
            x = cluster_puntos[:, 0]
            y = cluster_puntos[:, 1]
            plt.scatter(x, y, color=colores[j], s=10, alpha=0.7, label=f'Cluster {j + 1} - Simulación {i + 1}')

    # Graficar los puntos simulados en color rojo
    plt.scatter(puntos_simulados[:, 0], puntos_simulados[:, 1], color='red', s=10, alpha=0.7, label='Puntos Simulados')

    # Graficar los centroides de los clústeres
    centroides = kmeans.cluster_centers_
    plt.scatter(centroides[:, 0], centroides[:, 1], color='black', s=100, marker='X', label='Centroides')
    
    plt.xlabel('Coordenada X')
    plt.ylabel('Coordenada Y')
    plt.title(f'Clusters con {numero_clases} Clases y Puntos Simulados')
    plt.legend()
    plt.grid(True)
    plt.show()

# Nueva función para graficar solo los puntos simulados
def graficar_solo_puntos_simulados(puntos_simulados):
    plt.figure(figsize=(10, 6))
    plt.scatter(puntos_simulados[:, 0], puntos_simulados[:, 1], color='blue', s=10, alpha=0.7, label='Puntos Simulados')
    
    plt.xlabel('Coordenada X')
    plt.ylabel('Coordenada Y')
    plt.title('Puntos Simulados a partir de los Clústeres')
    plt.legend()
    plt.grid(True)
    plt.show()

# Función principal que ejecuta todo el flujo de identificación de clústeres y simulación de puntos
def ejecutar_simulacion(file_path, numero_clases, numero_puntos_simulacion):
    # Leer los datos del archivo
    datos_pickle = leer_datos_pickle(file_path)

    # Identificar clústeres
    kmeans = identificar_clusters(datos_pickle, numero_clases)

    # Simular puntos alrededor de los clústeres utilizando la desviación estándar real
    puntos_simulados = simular_puntos_desde_clusters_con_desviacion_real(kmeans, datos_pickle, numero_puntos_simulacion)

    # Graficar los clústeres y los puntos simulados junto con los reales
    graficar_clusters_y_simulacion(datos_pickle, numero_clases, kmeans, puntos_simulados)

    # Graficar solo los puntos simulados
    graficar_solo_puntos_simulados(puntos_simulados)

# Llamada a la función principal para ejecutar el ejemplo de uso
file_path = 'Instancia Tipo IV/scen_points_sample.pkl'
numero_clases = 3  # Número de clústeres
numero_puntos_simulacion = 50000  # Número de puntos simulados

# Ejecutar simulación y graficar resultados
ejecutar_simulacion(file_path, numero_clases, numero_puntos_simulacion)
