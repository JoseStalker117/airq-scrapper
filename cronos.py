from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime, timedelta
import main

def mi_rutina():
    main.run()

# Crear el programador
scheduler = BlockingScheduler()
# Programar la tarea usando cron (cada 6 horas a minuto 0)
scheduler.add_job(mi_rutina, 'cron', minute=0, hour='*/6')

print("🕒 Scheduler iniciado. Ejecutará la rutina cada 6 horas.")
try:
    scheduler.start()
except (KeyboardInterrupt, SystemExit):
    print("🛑 Scheduler detenido manualmente.")