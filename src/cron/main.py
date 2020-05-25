from cachetools.func import lru_cache

from src import firebase_app
from firebase_admin import firestore
from src import imdb


@lru_cache(maxsize=512)
def get_media_next_episodes(media_id: str) -> dict:
    next_ep_id = imdb.get_title_episodes(media_id)['base']['nextEpisode'].split('/')[2]
    date = imdb.get_title_auxiliary(next_ep_id)
    return date['releaseDetails']['date']


db = firestore.client()

userIDdoc = db.collection(u'favs').stream()

for userID in userIDdoc:
    print(f'Favourites for user {userID.id}')
    user_fav_dict = userID.to_dict()
    for user_fav in userID.to_dict().values():
        if user_fav['titleType'] in ('TV series', 'tvSeries'):
            episode_data = get_media_next_episodes(user_fav['id'])
            print(episode_data)
        else:
            print('#--> ')
            print(user_fav)
