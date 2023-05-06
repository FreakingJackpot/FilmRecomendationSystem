from requests import get, post
from django.conf import settings


def chunks(iterable, size):
    for i in range(0, len(iterable), size):
        yield iterable[i:i + size]


class Predictor:
    _batch_size = 1000

    @classmethod
    def predict(cls, user_id, movies_ids):
        for chunk in chunks(movies_ids, cls._batch_size):
            return PredictionService.predict(user_id, chunk)

    @classmethod
    def get_top_k(cls, user_id, movies_ids, k):
        predictions = PredictionService.predict(user_id, movies_ids)
        top_k = sorted(zip(movies_ids, predictions), key=lambda x: x[1], reverse=True)[:k]
        return top_k


class PredictionService:
    _login_url = settings.PREDICTOR_SERVICE_LOGIN_URL
    _predictor_url = settings.PREDICTOR_SERVICE_PREDICT_URL
    _token = None

    @classmethod
    def _login(cls):
        response = post(cls._login_url,
                        json={
                            'username': settings.PREDICT_SERVICE_USERNAME,
                            'password': settings.PREDICT_SERVICE_PASSWORD
                        })
        data = response.json()
        cls._token = data['token']

    @classmethod
    def predict(cls, user_id, movies_ids):
        if not cls._token:
            cls._login()

        data = {'predictions': []}

        try:
            response = get(cls._predictor_url,
                           params={
                               'user_id': user_id,
                               'movie_ids': ','.join(map(str, movies_ids)),
                           },
                           headers={'Authorization': 'Token ' + cls._token})
            data = response.json()
        except:
            pass

        return data['predictions']
