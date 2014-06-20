'''
Heroku scheduler will invoke this script every 10 minutes.
This is necessary to start cron jobs created at Tron CI.
'''
from scheduler import scheduler
import logging
import time


logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)s]: %(levelname)s : %(message)s'
)
logger = logging.getLogger(__name__)

logger.info('Reloading Tron CI scheduler')
scheduler.start()

# Giving enough time to restore and execute all jobs.
time.sleep(30)

# Shutdown scheduler after all jobs has finished.
scheduler.shutdown()
while scheduler.running:
    pass

logger.info('Reload process finished')
