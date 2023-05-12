from celery import shared_task


@shared_task
def import_movies():
    from film_recommender.management.commands.import_movies import Command
    Command().handle()



@shared_task
def import_genres():
    from film_recommender.management.commands.import_genres import Command
    Command().handle()


@shared_task
def predict_daily_recommends():
    from film_recommender.management.commands.predict_daily_recommends import Command
    Command().handle()


@shared_task
def import_dataset():
    from film_recommender.management.commands.import_dataset import Command
    Command().handle()


@shared_task
def quack():
    print('quack')