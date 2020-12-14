import ssl
from datetime import datetime
from os import environ as os_environ
from smtplib import SMTP_SSL

from cachetools.func import lru_cache
from src import firebase_app  # lgtm [py/unused-import]
from firebase_admin import auth
from firebase_admin import firestore
from httpx import AsyncClient, get as httpx_get
from imdbpie import Imdb
from lxml import html as lh
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

BROWSER_USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 11.0; rv:83.0) Gecko/20100101 Firefox/83.0"
reqXSession = AsyncClient()
imdb = Imdb()

db = firestore.client()

userIDdoc = db.collection(u'favs').stream()

# Email settings
port = 465
smtp_server = os_environ.get('sendgrid_smtp_server')
sender_email = os_environ.get('sendgrid_sender_email')
password = os_environ.get('sendgrid_password')
email_context = ssl.create_default_context()
email_smtp = SMTP_SSL(smtp_server, port=port, context=email_context)
email_smtp.connect(smtp_server, port)
email_smtp.login('apikey', password)


def parse_date(release_data) -> str:
    return release_data['air_date'].strftime('%A %B, %d, %Y')


def get_html_content(release_data, release_name) -> str:
    return f"""
            <p><img src="{release_data["img"]}" /></p>
            <h1>{release_name}</h1>
            <h3>{release_data["title"]}</h3>
            <p>{release_data["description"]}</p>
            <small>Release Date: <i>{parse_date(release_data)}</i></small>
        """


def send_email(email_to: str, display_name: str, release_name: str, release_data: dict) -> None:
    message = Mail(
        from_email=(sender_email, 'Movie Star'),
        to_emails=(email_to, display_name),
        subject=f'Movie Star Alert for {display_name}',
        html_content=get_html_content(release_data, release_name)
    )
    try:
        sg = SendGridAPIClient(password)
        sg.send(message)
    except Exception as e:
        print(e)


def get_episode_list(media_id):
    episodes = httpx_get(f'https://www.imdb.com/title/{media_id}/episodes', headers={'User-Agent': BROWSER_USER_AGENT})
    doc = lh.document_fromstring(episodes.text)
    ep_list = doc.find_class('eplist')[0].find_class('list_item')
    return doc, ep_list


def parse_episode(ep, doc):
    title = ep.cssselect('a[itemprop="name"]')[0].text
    description = ep.find_class('item_description')[0].text.strip()
    unparsed_date = ep.find_class('airdate')[0].text.strip()
    episode_image = ep.find_class('zero-z-index')
    if len(episode_image) > 1:
        ep_img = ep.find_class('zero-z-index')[1].attrib.get('src')
    else:
        ep_img = doc.find_class('poster')[0].attrib.get('src')
    return description, episode_image, title, unparsed_date, ep_img


@lru_cache(maxsize=512)
def get_media_next_episodes(media_id: str) -> dict or None:
    doc, ep_list = get_episode_list(media_id)
    for ep in ep_list:
        description, episode_image, title, unparsed_date, ep_img = parse_episode(ep, doc)
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
                "air_date": air_date,
                "img": ep_img
            }
    return None


for userID in userIDdoc:
    print(f'Favourites for user {userID.id}')
    user_fav_dict = userID.to_dict()
    for user_fav in userID.to_dict().values():
        if user_fav['titleType'] in ('TV series', 'tvSeries'):
            episode_data = get_media_next_episodes(user_fav['id'])
            if episode_data is not None:
                user = auth.get_user(userID.id)
                print(user_fav.get('title'))
                print(episode_data)
                send_email(user.email, user.display_name, user_fav.get('title'), episode_data)
