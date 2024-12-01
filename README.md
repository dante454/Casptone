# Proyecto de Simulación de Rutas para Deliveries y Pick-ups Dinámicos

## Índice

1. [Introducción](#introducción)
2. [Estructura del Código](#estructura-del-código)
   - [Archivos Principales](#archivos-principales)
3. [Clases y Funciones Principales](#clases-y-funciones-principales)
   - [Clases en `funciones_complementarias.py`](#clases-en-funciones_complementariaspy)
   - [Funciones en `politica_final.py`](#funciones-en-politica_finalpy)
   - [Funciones en `ruteo.py`](#funciones-en-ruteopy)
4. [Uso del Código para Generar Resultados](#uso-del-código-para-generar-resultados)
5. [Instrucciones para Reproducir los Resultados](#instrucciones-para-reproducir-los-resultados)

---

###### Introducción ########

Este proyecto implementa un modelo de simulación para gestionar entregas (`deliveries`) y recogidas (`pick-ups`) en un escenario dinámico. El problema se aborda en un mapa de 20,000 x 20,000 metros con un depósito central, tres camiones con capacidad infinita y una velocidad constante de 25 km/h. Los camiones están sujetos a restricciones de tiempo y deben optimizar sus rutas para maximizar el beneficio.

---

###### Estructura del Código #######

### Archivos Principales

1. **`politica_final.py`**:
   - Define la estructura y el flujo principal del problema.
   - Llama a funciones específicas de `ruteo.py` y `funciones_complementarias.py`.

2. **`optuna_opti.py`**:
   - Optimiza los parámetros utilizando 5 días de simulación.
   - Los resultados se almacenan en el archivo `parametros.py`.

3. **`simulacion_100_dias.py`**:
   - Valida los parámetros optimizados mediante simulaciones extendidas de 100 días.
   - Compara la política optimizada con el caso base.

4. **Carpeta `analisis`**:
   - Contiene scripts para analizar cómo afectan diferentes variables al problema:
     - Cantidad de camiones.
     - Velocidad de los camiones.
     - Diferencias en la utilidad de deliveries y pick-ups.

5. **`funciones_complementarias.py`**:
   - Contiene clases y funciones auxiliares que simplifican la lógica del código.

6. **`ruteo.py`**:
   - Implementa algoritmos de ruteo para generar y ajustar dinámicamente las rutas de los camiones.

---
## Clases y Funciones Principales

### Clases en `funciones_complementarias.py`

#### Clase `EstadoSimulacion`

- **Descripción**:
  Modela el estado general de la simulación, gestionando el tiempo, los pedidos y los camiones.

- **Atributos**:
  - `minuto_actual`: Minuto actual de la simulación.
  - `pedidos_no_disponibles`: Lista de pedidos que aún no están disponibles.
  - `pedidos_disponibles`: Lista de pedidos disponibles para ser entregados.
  - `pedidos_entregados`: Lista de pedidos completados.
  - `pedidos_tercerizados`: Lista de pedidos que fueron tercerizados.
  - `puntos`: Coordenadas de los puntos de los pedidos con los archivos de los registros historicos.
  - `indicadores`: Tipos de los pedidos (0: delivery, 1: pick-up) con los archivos de los registros historicos.
  - `arribos_por_minuto`: Cantidad de pedidos que llegan en cada minuto con los archivos de los registros historicos.
  - `punto_index`: Índice del próximo punto a usar.
  - `beneficio_por_intervalo`: Registro del beneficio calculado en intervalos de tiempo para luego ver como se comporta en intervalos.
  - `registro_minuto_a_minuto`: Historial de la simulación minuto a minuto.
  - `pickups_intervalos`: Porcentaje de pickups completados por intervalo.
  - `deliveries_intervalos`: Porcentaje de deliveries completados por intervalo.

- **Funciones**:
  - `avanzar_minuto(parametros)`: Avanza un minuto en la simulación, revisa pedidos y crea nuevos si corresponde.
  - `revisar_pedidos_disponibles()`: Mueve los pedidos de la lista de "no disponibles" a "disponibles" si cumplen los criterios.
  - `calcular_beneficio_acumulado()`: Calcula el beneficio total obtenido en la simulación.
  - `calcular_beneficio_maximo()`: Calcula el beneficio máximo posible basado en los pedidos disponibles y entregados.
  - `calcular_porcentaje_beneficio(beneficio_acumulado)`: Calcula el porcentaje del beneficio captado respecto al máximo posible.
  - `registrar_estado(camiones)`: Registra el estado actual de los pedidos y camiones en el historial.
  - `tercerizar_pedido(depot, velocidad_camion)`: Marca pedidos que no alcanzan a ser atendidos como tercerizados.

---

#### Clase `Pedido`

- **Descripción**:
  Representa un pedido en la simulación, con atributos clave como coordenadas y tiempos de llegada.

- **Atributos**:
  - `coordenadas`: Coordenadas del pedido.
  - `indicador`: Tipo de pedido (0: delivery, 1: pick-up).
  - `minuto_llegada`: Minuto en el que llega el pedido.
  - `disponible`: Indica si el pedido está disponible (0: no, 1: sí).
  - `entregado`: Indica si el pedido fue entregado (0: no, 1: sí).
  - `tiempo_entrega`: Minuto en que se entregó el pedido.
  - `momento_entrega`: Tiempo total desde la llegada hasta la entrega.
  - `area`: Área asignada al pedido según los parámetros.

- **Funciones**:
  - `hacer_disponible(minuto_actual)`: Marca el pedido como disponible si han pasado 15 minutos desde su llegada.
  - `entregar(minuto_entrega)`: Marca el pedido como entregado y registra el tiempo de entrega.
  - `determinar_area(parametros)`: Asigna el área del pedido según su ubicación y los parámetros.

---

#### Clase `Camion`

- **Descripción**:
  Representa un camión en la simulación, con capacidad infinita y atributos para manejar rutas y tiempos.

- **Atributos**:
  - `id`: Identificador único del camión.
  - `tiempo_restante`: Minutos restantes para que el camión esté disponible.
  - `velocidad`: Velocidad del camión en metros/minuto.
  - `rutas`: Lista de rutas realizadas.
  - `tiempo_inicio_ruta`: Tiempo en que comenzó la última ruta.
  - `posicion_actual`: Posición actual del camión.
  - `pickups_evaluados`: Indica si los pickups dinámicos han sido evaluados en la ruta actual.
  - `pickups_actuales`: Número de pickups dinámicos añadidos en la ruta actual.

- **Funciones**:
  - `actualizar_tiempo()`: Reduce el tiempo restante hasta que el camión esté disponible.
  - `asignar_ruta(ruta, tiempo_ruta, tiempo_inicio)`: Asigna una nueva ruta al camión y actualiza sus tiempos.
  - `actualizar_posicion(minuto_actual)`: Calcula y actualiza la posición actual del camión.

---

### Funciones en `politica_final.py`

- **`simular_minuto_a_minuto(simulacion, camiones, parametros_ventana_1, parametros_ventana_2, parametros_ventana_3)`**:
  Simula las operaciones minuto a minuto, evaluando salidas, rutas y beneficios y ademas actualiza la informacion de la simulacion todos los minutos.

- **`evaluar_salida(camion, simulacion, parametros)`**:
  Decide si un camión debe salir a rutear según criterios de pedidos disponibles y umbrales.

- **`flujo_ruteo(camion, simulacion, parametros)`**:
  Controla las decisiones de ruteo y asignación de rutas a los camiones una vez que se tomo la desicion de salir a repartir.

- **`actualizar_estado_simulacion(simulacion, ruta)`**:
  Marca los pedidos en una ruta como entregados y actualiza las listas correspondientes.

---

### Funciones en `ruteo.py`

- **`calcular_prioridad(pedido, minuto_actual)`**:
  Calcula la prioridad de los pedidos según su tiempo restante y la forma en la que priorizan los diferentes pedidos, funciona distinto para pick ups
  que para deliverys.

- **`generar_ruta(depot, camion, minuto_actual, pedidos_disponibles, parametros, tiempo_limite=195)`**:
  Genera una ruta inicial priorizando los pedidos más urgentes y cercanos al depósito haciendo uso de cheapest instertion.

- **`cheapest_insertion(tiempo_total, unvisited, route, pedidos_validos, depot, camion, minuto_actual, parametros, tiempo_limite=195)`**:
  Ajusta rutas mediante el algoritmo de inserción más económica, evaluando restricciones y beneficios ademas tiene un criterio inteligente
  de descarte de pedidos segun su urgencia ajustable por optuna.

- **`calculate_arrival_times(ruta_indices, pedidos_validos, depot, camion_velocidad, minuto_actual, service_time=3)`**:
  Calcula los tiempos de llegada de cada pedido y el tiempo total necesario para una ruta.

- **`cheapest_insertion_caso_base(points, depot, camion, minuto_actual, pedidos_disponibles, tiempo_limite=195)`**:
  Variante de inserción económica para el caso base.

- **`cheapest_insertion_adaptacion(...)`**:
  Ajusta dinámicamente rutas activas para incorporar nuevos pickups sin afectar viabilidad de los deliveries planeados.

- **`hora_entrega_pedidos(...)`**:
  Calcula los tiempos de llegada para los pedidos en una ruta específica.

---

## Uso del Código para Generar Resultados

1. **Estructura General**:
   - `politica_final.py` define el flujo principal del problema.
   - `optuna_opti.py` ajusta los parámetros.
   - `simulacion_100_dias.py` valida los parámetros en escenarios extendidos.
   - Los análisis de sensibilidad se realizan en la carpeta `analisis`.

2. **Proceso de Generación**:
   - Se optimizan parámetros con `optuna_opti.py`.
   - Se validan los parámetros con `simulacion_100_dias.py`.
   - Se generan visualizaciones y métricas clave para evaluar los resultados.

---

## Instrucciones para Reproducir los Resultados


### Optimización de Parámetros con `optuna_opti.py`

¡¡¡¡ Esto es solo en caso de que se quieran volver a optimizar los parametros, esta paso se recomienda saltar, cabe destacar que los resultados pueden 
cambiar ya que optuna no siempre entrega el mismo resultado !!!!

1. **Ajustes Iniciales**:
   - Abre el archivo `optuna_opti.py`.
   - Cambia las líneas según la configuración deseada:
     - **Líneas 82, 84, 86**: Selecciona la instancia específica con el número correspondiente.
     - **Línea 79**: Ajusta el rango de días utilizados para entrenar cambiando `range(x)`.
     - **Línea 128**: Cambia el número de iteraciones de `Optuna` con `n_trials=y`.

2. **Ejecutar Optimización**:
   - Corre el archivo ejecutando:
     ```bash
     python optuna_opti.py
     ```
   - La terminal mostrará los valores óptimos de los parámetros.

3. **Actualizar Parámetros**:
   - Abre el archivo `parametros.py`.
   - Sustituye los valores existentes por los valores obtenidos de la optimización en la terminal.

---

### Validación de Parámetros con `simulacion_100_dias.py`

1. **Ajustes Iniciales**:
   - Abre el archivo `simulacion_100_dias.py`.
   - Cambia la **Línea 16** para seleccionar la instancia correspondiente.

2. **Evaluar el Caso Base**:
   - Para validar el caso base:
     - **Descomenta** las líneas 12, 83 y 84.
     - **Comenta** la línea 80 para deshabilitar la política final.

3. **Validar la Política Final**:
   - Después de obtener resultados del caso base:
     - **Reinvierta el proceso** comentando las líneas del caso base y descomentando las líneas de la política final.

4. **Ejecutar Validación**:
   - Corre el archivo ejecutando:
     ```bash
     python simulacion_100_dias.py
     ```
   - Observa los resultados y compáralos con el caso base para evaluar la efectividad de la política optimizada.

---

### Análisis de Sensibilidad

1. **Propósito**:
   - Evaluar cómo afectan diferentes variables al desempeño de la simulación, como:
     - **Cantidad de camiones**.
     - **Velocidad de los camiones**.
     - **Diferencias en la utilidad** asignada a deliveries y pick-ups.

2. **Configuración**:
   - Abre los archivos correspondientes dentro de la carpeta `analisis`.
   - Ajusta los valores de entrada según las necesidades del análisis.

3. **Ejecutar los Análisis**:
   - Corre cada script según las instrucciones internas de cada archivo.
   - Observa los resultados para evaluar el impacto de las variables modificadas.

---

**Con estas instrucciones completas, puedes ajustar, validar y analizar el comportamiento del sistema para cualquier configuración deseada.**
