Для запуска проекта нужно 
* скачать python3.9
* Ввести команду в консоли pip install -r requirementx.txt, тем самым установив требуемые пакеты
* В файле FilmRecommendationSystem/settings прописать в databases параметры базы POSTGRESQL
* В файле film_recommender/apps.py в функции ready поставить pass перед операциями, перейти в главную директорию и ввести в консоль ./manage.py migrate portal film_recommender. после выполения комманд убрать pass из apps
* Заполения базы готовыми пользователями введите ./manage.py import_dataset
* Для генерации ежедневной подборки ввести ./manage.py predict_daily_recommends