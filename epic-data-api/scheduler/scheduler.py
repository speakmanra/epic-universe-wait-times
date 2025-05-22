import logging
import sys
from datetime import datetime
from django.conf import settings
from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore
from django.core.management import call_command
from apscheduler.triggers.cron import CronTrigger

logger = logging.getLogger(__name__)

def fetch_live_data_job():
    """Job to fetch live data from the API"""
    logger.info(f"Running fetch_live_data job at {datetime.now()}")
    call_command('fetch_live_data')


def start():
    """Start the scheduler"""
    # Don't run scheduler when running management commands (like migrations)
    if any('manage.py' in arg for arg in sys.argv):
        # Only start scheduler if it's the runserver command
        if 'runserver' not in sys.argv:
            return

    scheduler = BackgroundScheduler()
    scheduler.add_jobstore(DjangoJobStore(), "default")
    
    # Run every minute
    scheduler.add_job(
        fetch_live_data_job,
        trigger=CronTrigger(minute="*"),  # Every minute
        id="fetch_live_data",
        max_instances=1,
        replace_existing=True,
    )
    
    # Run once at startup as well
    scheduler.add_job(
        fetch_live_data_job,
        id="fetch_live_data_startup",
        max_instances=1,
        replace_existing=True,
        next_run_time=datetime.now()
    )
    
    logger.info("Starting scheduler...")
    scheduler.start() 