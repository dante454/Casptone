from funciones import analizar_instancia

#Parametros por simulacion
division_minutos_prueba = 60
area_densidad_prueba = 15
numero_simulaciones_mapa_prueba = 15

#Instacia 1
analizar_instancia('Instancia Tipo I/scen_arrivals_sample.pkl', 'Instancia Tipo I/scen_deadlines_sample.pkl', 'Instancia Tipo I/scen_indicador_sample.pkl',
                    'Instancia Tipo I/scen_points_sample.pkl', 'Instancia Tipo I/scen_profits_sample.pkl', 'Instancia Tipo I/scen_ready_times_sample.pkl',
                    'Instancia Tipo I/scen_service_times_sample.pkl', 'Instancia 1', division_minutos_prueba, area_densidad_prueba, 
                    numero_simulaciones_mapa_prueba)

#Instacia 2
analizar_instancia('Instancia Tipo II/scen_arrivals_sample.pkl', 'Instancia Tipo II/scen_deadlines_sample.pkl', 'Instancia Tipo II/scen_indicador_sample.pkl',
                    'Instancia Tipo II/scen_points_sample.pkl', 'Instancia Tipo II/scen_profits_sample.pkl', 'Instancia Tipo II/scen_ready_times_sample.pkl',
                    'Instancia Tipo II/scen_service_times_sample.pkl', 'Instancia 2', division_minutos_prueba, area_densidad_prueba, 
                    numero_simulaciones_mapa_prueba)

#Instacia 3
analizar_instancia('Instancia Tipo III/scen_arrivals_sample.pkl', 'Instancia Tipo III/scen_deadlines_sample.pkl', 'Instancia Tipo III/scen_indicador_sample.pkl',
                    'Instancia Tipo III/scen_points_sample.pkl', 'Instancia Tipo III/scen_profits_sample.pkl', 'Instancia Tipo III/scen_ready_times_sample.pkl',
                    'Instancia Tipo III/scen_service_times_sample.pkl', 'Instancia 3', division_minutos_prueba, area_densidad_prueba, 
                    numero_simulaciones_mapa_prueba)

#Instancia 4
analizar_instancia('Instancia Tipo IV/scen_arrivals_sample.pkl', 'Instancia Tipo IV/scen_deadlines_sample.pkl', 'Instancia Tipo IV/scen_indicador_sample.pkl',
                    'Instancia Tipo IV/scen_points_sample.pkl', 'Instancia Tipo IV/scen_profits_sample.pkl', 'Instancia Tipo IV/scen_ready_times_sample.pkl',
                    'Instancia Tipo IV/scen_service_times_sample.pkl', 'Instancia 4', division_minutos_prueba, area_densidad_prueba, 
                    numero_simulaciones_mapa_prueba)


