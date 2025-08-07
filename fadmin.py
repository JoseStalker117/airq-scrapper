import firebase_admin, os, json, time
from firebase_admin import credentials, db, firestore
from dotenv import load_dotenv
from datetime import datetime

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

