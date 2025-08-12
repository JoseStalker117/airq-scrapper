import main

a = main.fbadmin()
a.consultar()
a.graficar_dataframe(a.dataframe())

pron = a.pronostico(municipio_filtrar="Escobedo", dias=7)
a.graficar_dataframe(pron, titulo="Pronóstico de Escobedo")