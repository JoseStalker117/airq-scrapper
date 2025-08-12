from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
import main

def mi_rutina():
    print(f"Ejecutando {datetime.now()}")
    main.run()

scheduler = BlockingScheduler()

trigger = CronTrigger(
    hour='*/4',
    # minute='*/10',
    timezone='America/Mexico_City'
)

scheduler.add_job(
    mi_rutina,
    trigger,
    coalesce=True,              # Si se pierden ejecuciones, ejecuta solo una
    misfire_grace_time=3600     # Hasta 1 hora de tolerancia
)

scheduler.start()