import firebase_admin, os, json, time, pytz
from firebase_admin import credentials, db, firestore
from dotenv import load_dotenv
from datetime import datetime
import pandas as pd

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
        self.db = db.reference('/airq')
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
            data = self.db.get()
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

    def pronostico(self, municipio_filtrar=None, dias=7):
        try:
            from sklearn.linear_model import LinearRegression
            from datetime import datetime, timedelta
            import pytz

            tz_mx = pytz.timezone("America/Monterrey")

            # Extraer todos los datos en bruto (sin promediar)
            registros = []
            for timestamp, municipios in self.data.items():
                try:
                    ts = int(timestamp)
                    fecha = datetime.fromtimestamp(ts, tz=tz_mx)
                except Exception:
                    continue

                for municipio, contaminantes in municipios.items():
                    if not isinstance(contaminantes, dict):
                        continue

                    if municipio_filtrar and municipio != municipio_filtrar:
                        continue

                    registro = {
                        'fecha': fecha,
                        'timestamp': ts,
                        'municipio': municipio
                    }
                    registro.update(contaminantes)
                    registros.append(registro)

            df = pd.DataFrame(registros)
            

            if df.empty:
                print("⚠️ No hay datos suficientes para generar el pronóstico.")
                return None
            
            df.fillna(0, inplace=True)
            df['days_since_start'] = (df['fecha'] - df['fecha'].min()).dt.total_seconds() / 86400  # convertir a días

            # Crear fechas futuras
            max_fecha = df['fecha'].max()
            future_dates = [max_fecha + timedelta(days=i) for i in range(1, dias + 1)]
            future_df = pd.DataFrame({'fecha': future_dates})
            future_df['days_since_start'] = (future_df['fecha'] - df['fecha'].min()).dt.total_seconds() / 86400

            # Identificar contaminantes numéricos
            contaminantes = [col for col in df.columns if col not in ['fecha', 'timestamp', 'municipio', 'days_since_start']]

            for contaminante in contaminantes:
                model = LinearRegression()
                x = df[['days_since_start']]
                y = df[contaminante]
                model.fit(x, y)
                future_df[contaminante] = model.predict(future_df[['days_since_start']])

            self.df_forecast = future_df
            print("✅ Pronóstico generado exitosamente.")
            return future_df

        except Exception as e:
            print(f"❌ Error al generar el pronóstico: {e}")
            return None

    def dataframe(self):
        try:
            from datetime import datetime
            import pytz
            tz_mx = pytz.timezone("America/Monterrey")

            records = []
            for timestamp, municipios in self.data.items():
                try:
                    ts_int = int(timestamp)
                    fecha = datetime.fromtimestamp(ts_int, tz=tz_mx).strftime('%Y-%m-%d')
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

                    record = {'municipio': municipio, 'fecha': fecha}
                    record.update(contaminantes)
                    records.append(record)

            if not records:
                print("⚠️ No se encontraron datos válidos para generar el DataFrame.")
                return None

            df = pd.DataFrame(records)

            if 'fecha' not in df.columns:
                print("❌ La columna 'fecha' no se generó correctamente.")
                return None

            df['fecha'] = pd.to_datetime(df['fecha'])
            df.fillna(0, inplace=True)
            self.df_promedios = df.groupby(['municipio', 'fecha'], as_index=False).mean(numeric_only=True)
            print("✅ DataFrame generado exitosamente.")
            return self.df_promedios

        except Exception as e:
            print(f"❌ Error al generar el DataFrame: {e}")
            return None

    def graficar_dataframe(self, df, titulo="Gráfica de contaminantes (barras)"):
        import matplotlib.pyplot as plt
        try:
            if df is None or df.empty:
                print("⚠️ El DataFrame está vacío o no es válido.")
                return

            if 'fecha' not in df.columns:
                print("❌ La columna 'fecha' no existe en el DataFrame.")
                return

            df['fecha'] = pd.to_datetime(df['fecha'])
            columnas_numericas = df.select_dtypes(include='number').columns.tolist()

            if not columnas_numericas:
                print("⚠️ No hay columnas numéricas para graficar.")
                return

            # Graficar cada columna como un subplot de barras
            for columna in columnas_numericas:
                plt.figure(figsize=(12, 6))
                plt.bar(df['fecha'], df[columna])
                plt.title(f"{titulo} - {columna}")
                plt.xlabel("Fecha")
                plt.ylabel(columna)
                plt.xticks(rotation=45)
                plt.grid(True)
                plt.tight_layout()
                plt.show()

        except Exception as e:
            print(f"❌ Error al graficar el DataFrame: {e}")

a = fbadmin()
a.consultar()
a.graficar_dataframe(a.dataframe())

