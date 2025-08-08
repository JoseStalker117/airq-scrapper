import firebase_admin, os
import matplotlib.pyplot as plt
import pandas as pd
from firebase_admin import credentials, db
from datetime import datetime
from dotenv import load_dotenv
import os, json

load_dotenv('config.env')
cred = credentials.Certificate('Firebase-admin.json')

try:
    firebase_admin.initialize_app(cred, {
        'databaseURL': os.getenv('rtdb_url', 'https://your-database-url.firebaseio.com/')
    })
    print("[Firebase] Conexión inicializada correctamente")
except ValueError:
    print("[Firebase] Firebase ya está inicializado")
except Exception as e:
    print(f"[Firebase] Error al inicializar: {e}")
    
    
class airq:
    def __init__(self):
        self.db = db.reference('/airq')
        self.data = None
        
    def consultar(self):
        try:
            data = self.db.get()
            self.data = data
            # Uncomment the following lines to print the data if needed
            # if data:
            #     print("Datos obtenidos de Firebase Realtime Database:")
            #     for key, value in data.items():
            #         print(f"{key}: {value}")
            # else:
            #     print("No hay datos disponibles en Firebase Realtime Database.")
        except Exception as e:
            print(f"Error al consultar datos: {e}")
            
    def procesar(self):
        # Placeholder for future processing functionality
        print("Función de procesar aún no implementada.")
    
    def depurar(self):
        with open('airq.json', 'w') as f:
            f.write(str(self.data))
            
    def graficar(self):
        df = pd.DataFrame(self.data).T
        # Rellenar valores faltantes con 0 temporalmente
        df = df.fillna(0)

        # Convertir a tipo numérico, forzando a NaN si no es número
        df = df.apply(pd.to_numeric, errors='coerce').fillna(0)
        
        print(df)

        # Graficar
        # df.plot(kind="bar", figsize=(12, 6))
        # plt.title("Concentración de contaminantes por ciudad")
        # plt.ylabel("µg/m³ o ppb")
        # plt.xlabel("Ciudad")
        # plt.legend(title="Contaminante")
        # plt.tight_layout()
        # plt.show()
        
            
a = airq()
a.consultar()
a.graficar()