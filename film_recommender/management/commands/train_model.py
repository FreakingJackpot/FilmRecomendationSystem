from pathlib import Path

from django.core.management.base import BaseCommand
import os

from film_recommender.services.training import TrainingData, ModelTrainer

APP_DIR = Path(__file__).resolve().parent.parent.parent


class Command(BaseCommand):

    def handle(self, *args, **options):
        training_data = TrainingData()
        trainer = ModelTrainer(training_data)
        trainer.train()
