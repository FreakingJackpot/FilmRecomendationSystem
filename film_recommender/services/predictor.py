import glob
import os
from datetime import datetime
import pandas as pd
import sklearn.preprocessing
import tensorflow as tf
from django.conf import settings
from recommenders.utils.tf_utils import pandas_input_fn_for_saved_model

tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.INFO)

from recommenders.utils.constants import (
    DEFAULT_USER_COL as USER_COL,
    DEFAULT_ITEM_COL as ITEM_COL,
    DEFAULT_GENRE_COL as ITEM_FEAT_COL,
)

from film_recommender.models import Genre


class Predictor(object):
    update_model_rate = 70  # minutes

    def __init__(self):
        list_of_files = glob.glob(settings.MODEL_DIR + '/*')
        latest_file = max(list_of_files, key=os.path.getctime)

        self.model = tf.saved_model.load(latest_file + '/', tags=['serve', ])

        self.classes = list(Genre.objects.values_list('name', flat=True))
        self.classes.append('unknown')

        self.last_model_upload = datetime.now()

    def _init_model(self):
        list_of_files = glob.glob(settings.MODEL_DIR + '/*')
        latest_file = max(list_of_files, key=os.path.getctime)

        self.model = tf.saved_model.load(latest_file + '/', tags=['serve', ])

        self.classes = list(Genre.objects.values_list('name', flat=True))
        self.classes.append('unknown')

    def get_top_k(self, movies, user_id, top_k):
        predictions = self.predict(movies, user_id)

        movie_ids_with_ratings = []
        for prediction, movie in zip(predictions, movies):
            movie_ids_with_ratings.append((movie.id, prediction))

        movie_ids_with_ratings.sort(key=lambda x: x[1], reverse=True)

        return movie_ids_with_ratings[:top_k]

    def predict(self, movies, user_id):
        self._check_upload_time()
        data = self._prepare_data_from_movies(movies, user_id)

        predictions = self.model.signatures["predict"](
            examples=pandas_input_fn_for_saved_model(
                df=data,
                feat_name_type={
                    USER_COL: int,
                    ITEM_COL: int,
                    ITEM_FEAT_COL: list
                }
            )()["inputs"]
        )

        return [float(prediction) * 2 for prediction in predictions['predictions']]

    def _prepare_data_from_movies(self, movies, user_id):
        genres_encoder = sklearn.preprocessing.MultiLabelBinarizer(classes=self.classes)

        movies_to_predict = []
        for movie in movies:
            genres = [genre.name for genre in movie.genres.all() if genre.name in self.classes] or ['unknown', ]
            movies_to_predict.append((user_id, movie.id, genres))

        data = pd.DataFrame(data=movies_to_predict, columns=[USER_COL, ITEM_COL, ITEM_FEAT_COL])

        data[ITEM_FEAT_COL] = genres_encoder.fit_transform(data[ITEM_FEAT_COL]).tolist()
        data.reset_index(drop=True, inplace=True)

        return data

    def _check_upload_time(self):
        minutes_diff = (datetime.now() - self.last_model_upload).total_seconds() / 60.0
        if minutes_diff >= self.update_model_rate:
            self.__init__()
