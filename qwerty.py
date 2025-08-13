import fadmin as fb
import pandas as pd

a = fb.fbadmin()
a.consultar()

# print(a.dataframe())

raw = a.dataframe()

#Plot de datos promedio por dia
a.graficar_dataframe(
                    raw,
                    "Escobedo",
                    "Informacion promedio de Escobedo",
                    )


#Generacion de pronostico y plot
df_hist, df_forecast = a.diagnostico_lineal(
                                            raw,
                                            municipio="Escobedo",
                                            dias=30,
                                            pronostico_dias=7)


df_total = pd.concat([df_hist, df_forecast])
a.graficar_dataframe(df_total, titulo="Pronóstico lineal 7 días")