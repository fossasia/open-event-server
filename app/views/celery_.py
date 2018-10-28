from celery import Celery
from config import Config

celery = Celery(__name__, broker=Config.REDIS_URL, backend=Config.CELERY_BACKKEND)
