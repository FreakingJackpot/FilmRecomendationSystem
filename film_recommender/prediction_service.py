from requests import get, post, RequestException
from django.conf import settings

from film_recommender.services import chunks


class Predictor:
    _batch_size = 1000

    @classmethod
    def predict(cls, user_id, movies_ids):
        predictions = []
        for chunk in chunks(movies_ids, cls._batch_size):
            predictions.extend(PredictionService.predict(user_id, chunk))

        return predictions

    @classmethod
    def get_top_k(cls, user_id, movies_ids, k):
        predictions = cls.predict(user_id, movies_ids)
        top_k = sorted(predictions, key=lambda x: x['rating'], reverse=True)[:k]
        return top_k


class PredictionService:
    _login_url = settings.PREDICTOR_SERVICE_LOGIN_URL
    _predictor_url = settings.PREDICTOR_SERVICE_PREDICT_URL
    _token = None

    @classmethod
    def _login(cls):
        try:
            response = post(cls._login_url,
                            json={
                                'username': settings.PREDICT_SERVICE_USERNAME,
                                'password': settings.PREDICT_SERVICE_PASSWORD
                            })
            data = response.json()
            cls._token = data['token']
        except RequestException as e:
            print(e)

    @classmethod
    def predict(cls, user_id, movies_ids):
        if not cls._token:
            cls._login()

        data = {'predictions': []}
        if cls._token:

            try:
                response = get(cls._predictor_url,
                               params={
                                   'user_id': user_id,
                                   'movie_ids': ','.join(map(str, movies_ids)),
                               },
                               headers={'Authorization': 'Token ' + cls._token})
                data = response.json()

            except RequestException as e:
                print(e)

        return data['predictions']
