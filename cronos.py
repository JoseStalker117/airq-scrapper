from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, timedelta, time
import main

def mi_rutina():
    main.run()

# Crear el programador
scheduler = BlockingScheduler()
# Programar la tarea usando cron (cada 6 horas a minuto 0)
# scheduler.add_job(mi_rutina, 'cron', minute=0, hour='*/6')
trigger = CronTrigger(hour='*/6', minute=0, second=0, timezone='America/Mexico_City')
scheduler.add_job(mi_rutina, trigger)
scheduler.start()

try:
    while True:
        time.sleep(1)  # Mantener el script en ejecución
except (KeyboardInterrupt, SystemExit):
    scheduler.shutdown()
    print("Scheduler detenido.")