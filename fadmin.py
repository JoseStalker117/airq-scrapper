import firebase_admin, os, json, time
from firebase_admin import credentials, db, firestore
from dotenv import load_dotenv
from datetime import datetime
import pandas as pd

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

def timestamp():
    return str(int(time.time()))

class fbadmin:
    def __init__(self):
        # Cambiado a raíz para evitar errores en rutas
        self.db = db.reference('/')
        self.fs = firestore.client()

    def fb_guardar(self):
        try:
            with open(f"{os.getenv('dicc')}", 'r') as file:
                data = json.load(file)
                self.db.child('airq').child(timestamp()).set(data)
            print("✅ Datos guardados en Firebase Realtime Database")
        except FileNotFoundError:
            print("❌ El archivo contaminantes.json no se encontró.")
        except Exception as e:
            print(f"❌ Error inesperado al guardar en Firebase: {e}")


    # Cargar datos desde un archivo Excel y guardarlos en Firebase Realtime Database (Depuracion)
    def cargar_datos(self):
        try:
            df  = pd.read_excel('gral-escobedo.xlsx', sheet_name='Sheet1')
            fechas = df['Fecha']
            df['Fecha'] = pd.to_datetime(df['Fecha'], errors='coerce')
            dicc = {}
            for _, fila in df.iterrows():
                fecha = fila['Fecha']
                ts = str(int(fecha.timestamp()))
                datos_escobedo = fila.drop(labels=['Fecha']).to_dict()
                datos_escobedo = {k: float(v) for k, v in datos_escobedo.items() if pd.notna(v)}
                dicc[ts] = {
                "Escobedo": datos_escobedo
                }
            # Guardar en Firebase Realtime Database
            self.db.child('airq').update(dicc)     
        except FileNotFoundError:
            print("❌ El archivo gral-escobedo.xlsx no se encontró.")
            return
        
        # print(df)
         
# a = fbadmin()
# a.cargar_datos()

