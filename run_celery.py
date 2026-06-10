"""
Run Celery worker with filesystem transport (no Redis needed).
Usage: python run_celery.py worker
       python run_celery.py beat
"""
import sys
import os
import json

# Override broker to use filesystem
BROKER_DIR = os.path.join(os.path.dirname(__file__), '.celery_broker')
os.makedirs(BROKER_DIR, exist_ok=True)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
# Use filesystem transport
os.environ.setdefault('CELERY_BROKER_URL', f'filesystem://')
os.environ.setdefault('CELERY_FILESYSTEM_BROKER_DIR', BROKER_DIR)
os.environ.setdefault('CELERY_BROKER_TRANSPORT_OPTIONS', json.dumps({
    'data_folder_in': os.path.join(BROKER_DIR, 'in'),
    'data_folder_out': os.path.join(BROKER_DIR, 'out'),
    'store_processed': True,
    'processed_folder': os.path.join(BROKER_DIR, 'processed'),
}))

from config.celery import app

if __name__ == '__main__':
    from celery.bin import celery
    celery.main()
