from typing import Union
from dataclasses import dataclass
from itertools import chain
from abc import ABC

from django.conf import settings
from django.utils import translation
from pyyoutube import Api
import requests
from bs4 import BeautifulSoup
from transliterate import translit

from film_recommender.models import Movie
from portal.models import YoutubeChannel

STOPWORDS = ['трейлер', 'trailer', 'интервью', 'iterview', 'compilation', 'нарезка', 'scene', 'сцена']


@dataclass
class MovieUrl:
    source_name: str
    url: str
    subtitles: bool

    def __init__(self, source_name: str, url: str, subtitles: bool):
        self.source_name = source_name
        self.url = url
        self.subtitles = subtitles


class MovieSourceInterface:
    @classmethod
    def search(cls, movie: Movie) -> Union[list[MovieUrl], MovieUrl, None]:
        pass


class Youtube(MovieSourceInterface):
    _api = Api(api_key=settings.YOUTUBE_API_KEY)
    _long_duration_start = 20
    _video_url_template = 'https://www.youtube.com/watch?v={}'

    @classmethod
    def search(cls, movie: Movie) -> Union[list[MovieUrl], MovieUrl, None]:
        urls = []

        language = translation.get_language()

        channels = YoutubeChannel.objects.all()
        params = cls._prepare_params(movie.title, movie.duration)

        for channel in channels:
            video_id = cls._search_video_id_on_channel(channel.channel_id, movie.title, params)
            if video_id:
                source_name = channel.ru_name if language == 'ru' else channel.eng_name
                subtitles = False if language == channel.language_type else True
                url = cls._video_url_template.format(video_id)

                urls.append(MovieUrl(source_name, url, subtitles))

        return urls

    @classmethod
    def _prepare_params(cls, movie_name, duration) -> dict:
        params = {'q': movie_name, 'search_type': "video", }
        if duration > cls._long_duration_start:
            params['video_duration'] = 'long'

        return params

    @classmethod
    def _search_video_id_on_channel(cls, channel_id, title, params) -> Union[str, None]:
        search_result = cls._api.search(**params, channel_id=channel_id)

        if search_result.items:
            for item in search_result.items:
                if title in item.snippet.title and cls._check_video_title(item.snippet.title):
                    return item.id.videoId

    @staticmethod
    def _check_video_title(title):
        for stopword in STOPWORDS:
            if stopword in title or stopword.capitalize() in title:
                return False
        return True


class SourceWithGoogleSearch(ABC, MovieSourceInterface):
    _search_url_template: str
    _site_name: str
    _subtitles: bool

    @classmethod
    def search(cls, movie: Movie) -> Union[list[MovieUrl], MovieUrl, None]:
        response = requests.get(cls._search_url_template.format(title=movie.title))
        soup = BeautifulSoup(response.text, 'html.parser')
        movie = soup.find('a', attrs={'class': 'gs-title'})
        if movie:
            return MovieUrl(cls._site_name, movie.href, cls._subtitles)


class FMC(SourceWithGoogleSearch):
    _search_url_template = 'https://www.freemoviescinema.com/search?q={title}'
    _site_name = 'Free Movies Cinema'
    _subtitles = False


class TDF(SourceWithGoogleSearch):
    _search_url_template = 'https://topdocumentaryfilms.com/search/?results={title}'
    _site_name = 'Top Documentary Films'
    _subtitles = False


class Tvigle(MovieSourceInterface):
    url_template = 'https://www.tvigle.ru/video/{slug}/'

    @classmethod
    def search(cls, movie: Movie) -> Union[list[MovieUrl], MovieUrl, None]:
        translited_title = translit(movie.title, reversed=True)
        translited_title = translited_title.lower().replace(' ', '-')

        url = cls.url_template.format(slug=translited_title)
        response = requests.get(url)
        if response.status_code == '200':
            return MovieUrl('Tvigle', url, False)


class MovieUrlsManager:
    sources = {
        'ru': [Tvigle, ],
        'en-us': [FMC, TDF, ],
        'any': [Youtube, ]
    }

    @classmethod
    def get_urls(cls, movie: Movie) -> list[MovieUrl]:
        urls = []

        language = translation.get_language()

        for source in chain(cls.sources['any'], cls.sources[language]):
            source_data = source.search(movie)
            if isinstance(source_data, list):
                urls.extend(source.search(movie))
            elif isinstance(source_data, MovieUrl):
                urls.append(source_data)

        return urls
