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
def import_dataset():
    from film_recommender.management.commands.import_dataset import Command
    Command().handle()
