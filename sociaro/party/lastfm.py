# обработка запросов к LastFM
import requests


def lastfm_get(params):
    """
    Функция для отправки запросов, используя API LastFM.
    В параметре передается метод запроса.
    Возвращает данные по запросу
    """
    API_KEY = '49dd14857c57f60951c53e6a2c93071e'
    USER_AGENT = 'Dataquest'

    # подключаем headers и URL
    headers = {'user-agent': USER_AGENT}
    url = 'https://ws.audioscrobbler.com/2.0/'

    # Добавить API ключ и формат данных
    params['api_key'] = API_KEY
    params['format'] = 'json'

    response = requests.get(url, headers=headers, params=params)
    return response
