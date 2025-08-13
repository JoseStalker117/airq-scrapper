from playwright.async_api import async_playwright
from datetime import datetime
from dotenv import load_dotenv
import asyncio, json, os
from fadmin import fbadmin
load_dotenv('config.env')

def cargar_estados():
    with open("estados.json", "r") as f:
        estados = json.load(f)
    return estados


def guardar_datos(dicc):
    try:
        ruta_archivo = os.getenv("dicc")
        if not ruta_archivo:
            print("⚠️ La variable de entorno 'dicc' no está definida.")
            return

        with open(ruta_archivo, "w", encoding="utf-8") as f:
            json.dump(dicc, f, indent=2, ensure_ascii=False)

        print(f"✅ Datos guardados en {ruta_archivo}")
    except Exception as e:
        print(f"❌ Error al guardar datos: {e}")
    

def normalizar_nombre(nombre):
    nombre = nombre.replace("\n", " ").strip()
    mapeo = {
        "PM2.5": "PM2,5",
        "PM10": "PM10",
        "O₃": "O3",
        "NO₂": "NO2",
        "SO₂": "SO2",
        "CO": "CO"
    }
    for clave in mapeo:
        if clave in nombre:
            return mapeo[clave]
    return None  # ignora si no está en el mapeo
    
async def extraer_contaminantes(estados):
    resultados = {}

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        for entrada in estados:
            estado = entrada.get("estado", "Desconocido")
            url = entrada.get("url", "")

            print(f"🌐 Procesando {estado}...")

            if not url:
                print(f"⚠️ No se proporcionó URL para {estado}")
                resultados[estado] = {}
                continue

            try:
                await page.goto(url, timeout=60000)
                await page.wait_for_selector('table[title="Contaminantes del aire"]', timeout=10000)

                filas = await page.locator('table[title="Contaminantes del aire"] tr').all()
                edo_res = {}

                for fila in filas:
                    try:
                        nombre = await fila.locator('div.font-body-s.text-gray-900').first.inner_text()
                        valor = await fila.locator('span.font-body-m-medium.text-gray-900').first.inner_text()
                        
                        clave = normalizar_nombre(nombre)
                        if clave:  # Solo si es una clave válida
                            edo_res[clave] = float(valor.strip())
                            
                    except Exception as fila_error:
                        print(f"⚠️ Error procesando fila en {estado}: {fila_error}")
                        continue

                resultados[estado] = edo_res

            except Exception as e:
                print(f"❌ Error cargando la página para {estado}: {e}")
                resultados[estado] = {}
                continue  # sigue con el siguiente estado

        await browser.close()

    guardar_datos(resultados)

def run():
    edos = cargar_estados()
    asyncio.run(extraer_contaminantes(edos))
    fb = fbadmin()
    fb.fb_guardar()
    
run()