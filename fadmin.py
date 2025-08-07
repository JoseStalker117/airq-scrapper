import firebase_admin
from firebase_admin import credentials, db
from datetime import datetime

cred = credentials.Certificate('Firebase-admin.json')

# Inicializar Firebase Admin SDK
try:
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://bioinsight23-default-rtdb.firebaseio.com/'
    })
    print("[Firebase] Conexión inicializada correctamente")
except ValueError:
    print("[Firebase] Firebase ya está inicializado")
except Exception as e:
    print(f"[Firebase] Error al inicializar: {e}")
    
    
class fbadmin:
    def __init__(self):
        self.ref = db.reference('airq')
    
    def guardar_datos(self, datos, fecha):
        try:
            self.ref.child(fecha).set(datos)
            print(f"✅ Datos guardados en contaminantes_{fecha}.json")
        except Exception as e:
            print(f"❌ Error al guardar datos: {e}")