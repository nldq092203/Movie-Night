from celery import shared_task
from movies import omdb_integration

@shared_task
def search_and_save(search):
    return omdb_integration.search_and_save(search)
