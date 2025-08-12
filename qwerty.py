import fadmin as fb

a = fb.fbadmin()
a.consultar()
# print(a.dataframe())
a.graficar_dataframe(a.dataframe(), "Escobedo")