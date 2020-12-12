from cachetools.func import lru_cache

from src import firebase_app
from datetime import datetime
from firebase_admin import firestore
from lxml import html as lh
from imdbpie import Imdb
import httpx

BROWSER_USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0"
reqXSession = httpx.AsyncClient()
imdb = Imdb()

db = firestore.client()

userIDdoc = db.collection(u'favs').stream()


@lru_cache(maxsize=512)
def get_media_next_episodes(media_id: str) -> dict or None:
    episodes = httpx.get(f'https://www.imdb.com/title/{media_id}/episodes', headers={'User-Agent': BROWSER_USER_AGENT})
    doc = lh.document_fromstring(episodes.text)
    ep_list = doc.find_class('eplist')[0].find_class('list_item')
    for ep in ep_list:
        title = ep.cssselect('a[itemprop="name"]')[0].text
        description = ep.find_class('item_description')[0].text.strip()
        unparsed_date = ep.find_class('airdate')[0].text.strip()
        try:
            air_date = datetime.strptime(unparsed_date, '%d %b %Y')
        except ValueError:
            if unparsed_date == '':
                continue
            air_date = datetime.strptime(unparsed_date, '%d %b. %Y')

        date_diff = (air_date - datetime.today()).days

        if 0 < date_diff < 3:
            return {
                "title": title,
                "description": description,
                "air_date": air_date
            }
    return None


for userID in userIDdoc:
    print(f'Favourites for user {userID.id}')
    user_fav_dict = userID.to_dict()
    for user_fav in userID.to_dict().values():
        if user_fav['titleType'] in ('TV series', 'tvSeries'):
            episode_data = get_media_next_episodes(user_fav['id'])
            if episode_data is not None:
                print(user_fav.get('title'))
                print(episode_data)
