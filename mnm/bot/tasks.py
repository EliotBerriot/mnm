from mnm.taskapp import celery
from . import bot


@celery.app.task(bind=True)
def reply(self, status):
    b = bot.Bot()
    response = b.handle(status)

    return response
