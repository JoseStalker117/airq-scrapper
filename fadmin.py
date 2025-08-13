import firebase_admin, os, json, time, pytz
from firebase_admin import credentials, db, firestore
from sklearn.linear_model import LinearRegression
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import pytz
from dotenv import load_dotenv
import matplotlib.pyplot as plt

load_dotenv('config.env')
cred = credentials.Certificate('Firebase-admin.json')
tz_mx = pytz.timezone("America/Monterrey")

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
        self.data = None

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

    def consultar(self):
        try:
            data = self.db.child('airq').get()
            self.data = data
        except Exception as e:
            print(f"Error al consultar datos: {e}")

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

    def diagnostico_lineal(self, df, municipio, dias=30, pronostico_dias=7):
        """
        Filtra el DataFrame por municipio y rango de días, calcula la regresión lineal para cada contaminante
        y pronostica los próximos pronostico_dias días.
        """
        try:
            if 'fecha' not in df.columns or 'municipio' not in df.columns:
                raise ValueError("El DataFrame debe contener las columnas 'fecha' y 'municipio'.")

            df['fecha'] = pd.to_datetime(df['fecha'])
            columnas_numericas = df.select_dtypes(include='number').columns.tolist()
            columnas_numericas = [c for c in columnas_numericas if c != 'municipio']

            # Filtrar por municipio y rango de días históricos
            fecha_max = df['fecha'].max()
            fecha_inicio = fecha_max - pd.Timedelta(days=dias)
            df_hist = df[(df['municipio'] == municipio) & (df['fecha'] >= fecha_inicio)].sort_values('fecha')

            if df_hist.empty:
                print(f"⚠️ No hay datos para {municipio} en los últimos {dias} días.")
                return None

            diagnostico = df_hist.copy()
            modelos = {}

            # Ajustar modelo por cada contaminante y generar predicciones históricas
            for columna in columnas_numericas:
                x = np.arange(len(df_hist)).reshape(-1, 1)
                y = df_hist[columna].values.reshape(-1, 1)

                model = LinearRegression()
                model.fit(x, y)
                diagnostico[f"{columna}_tendencia"] = model.predict(x).flatten()
                modelos[columna] = model

            # Crear fechas futuras para el pronóstico
            fechas_futuras = [fecha_max + pd.Timedelta(days=i) for i in range(1, pronostico_dias + 1)]

            # Construir DataFrame para pronóstico
            df_pronostico = pd.DataFrame({
                'fecha': fechas_futuras,
                'municipio': municipio
            })

            # Predecir valores futuros con los modelos ajustados
            x_future = np.arange(len(df_hist), len(df_hist) + pronostico_dias).reshape(-1, 1)
            for columna, model in modelos.items():
                predicciones = model.predict(x_future).flatten()
                df_pronostico[columna] = predicciones
                df_pronostico[f"{columna}_tendencia"] = predicciones  # La tendencia futura es la predicción misma

            return diagnostico, df_pronostico

        except Exception as e:
            print(f"❌ Error en diagnostico_lineal: {e}")
            return None, None

    def dataframe(self):
        try:
            if not self.data or not isinstance(self.data, dict):
                print("⚠️ No hay datos válidos en self.data para generar el DataFrame.")
                return None

            tz_mx = pytz.timezone("America/Monterrey")
            records = []

            for timestamp, municipios in self.data.items():
                # Convertir timestamp a datetime
                try:
                    ts_int = int(timestamp)
                    fecha = datetime.fromtimestamp(ts_int, tz=tz_mx)
                except Exception as e:
                    print(f"⏱ Timestamp inválido: {timestamp} ({e})")
                    continue

                if not isinstance(municipios, dict):
                    print(f"⚠️ Estructura inesperada en {timestamp}: {municipios}")
                    continue

                for municipio, contaminantes in municipios.items():
                    if not isinstance(contaminantes, dict):
                        print(f"⚠️ Datos no válidos para {municipio} en {timestamp}")
                        continue

                    # Normalizar clave "PM2,5"
                    cont_normalizado = {
                        (k.replace(",", "_") if isinstance(k, str) else k): v
                        for k, v in contaminantes.items()
                    }

                    record = {"municipio": municipio, "fecha": fecha}
                    record.update(cont_normalizado)
                    records.append(record)

            if not records:
                print("⚠️ No se encontraron datos válidos para generar el DataFrame.")
                return None

            df = pd.DataFrame(records)

            if "fecha" not in df.columns:
                print("❌ La columna 'fecha' no se generó correctamente.")
                return None

            df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")
            df.fillna(0, inplace=True)

            # Calcular promedios por municipio y fecha
            self.df_promedios = df.groupby(["municipio", "fecha"], as_index=False).mean(numeric_only=True)

            print("✅ DataFrame generado exitosamente.")
            return self.df_promedios

        except Exception as e:
            print(f"❌ Error al generar el DataFrame: {e}")
            return None

    def graficar_dataframe(self, df, municipio=None, titulo="Tendencia de contaminantes"):
        try:
            if df is None or df.empty:
                print("⚠️ El DataFrame está vacío o no es válido.")
                return

            # Filtro por municipio si se indica
            if municipio and 'municipio' in df.columns:
                df = df[df['municipio'] == municipio]
                if df.empty:
                    print(f"⚠️ No hay datos para el municipio '{municipio}'.")
                    return

            columnas_numericas = df.select_dtypes(include='number').columns.tolist()
            if not columnas_numericas:
                print("⚠️ No hay columnas numéricas para graficar.")
                return

            plt.figure(figsize=(14, 7))

            for columna in columnas_numericas:
                plt.plot(df['fecha'], df[columna], label=columna)

            plt.title(f"{titulo} - {municipio if municipio else 'Municipio actual'}")
            plt.xlabel("Fecha")
            plt.ylabel("Valores")
            plt.legend()
            plt.grid(True)
            plt.tight_layout()
            plt.show()

        except Exception as e:
            print(f"❌ Error al graficar_dataframe: {e}")



