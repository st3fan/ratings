#!/usr/bin/env python3


import datetime
import json
import logging
import re

import bs4
import requests

from cache import SimpleMemoryCache
from database import Database, Rating


PLAY_STORE_APPS = [
    "org.mozilla.fenix",
    "org.mozilla.focus",
    "org.mozilla.klar"
]


APP_STORE_APPS = {
    "org.mozilla.ios.Focus": {
        "id": 1055677337,
        "countries": ["us", "ca", "fr", "es", "jp"]
    },
    "org.mozilla.ios.Klar": {
        "id": 1073435754,
        "countries": ["de"]
    },
    "org.mozilla.ios.Firefox": {
        "id": 989804926,
        "countries": ["us", "ca", "fr", "es", "de", "jp"]
    }
}


APP_STORE = "AppStore"
PLAY_STORE = "PlayStore"


STORE_URL_TTL = (7 * 86400)
FETCH_DELAY = 5


logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)

logger = logging.getLogger()


def resolve_app_store_url(app_id, country, cache):
    """Take an App Store app_id and country and lookup the user facing page for
    it. Throws an exception if an error ocurred and None if the url could not
    be found on the page."""

    cache_key = f"app_store_url/{app_id}/{country}"
    if url := cache.get(cache_key):
        return url

    url = f"https://tools.applemediaservices.com/app/{app_id}?country={country}"
    logger.info("Fetching %s", url)
    r = requests.get(url)
    r.raise_for_status()

    if matches := re.findall(r'"url":"([^"]*)"', r.text):
        url = matches[0]
        cache.set(cache_key, url, STORE_URL_TTL)
        return url


def fetch_app_store_page(app_id, country, cache):
    url = resolve_app_store_url(app_id, country, cache)
    logger.info("Fetching %s", url)
    r = requests.get(url)
    r.raise_for_status()
    return r.text


def fetch_app_store_rating_info(app_id, country, cache):
    page = fetch_app_store_page(app_id, country, cache)
    soup = bs4.BeautifulSoup(page, 'html.parser')
    if script := soup.find("script",{"id":"shoebox-ember-data-store"}):
        data = json.loads(script.text)
        user_rating = data[str(app_id)]['data']['attributes']['userRating']
        return {"rating": user_rating["value"], "stars": user_rating["ratingCountList"]}


def main():
    cache = SimpleMemoryCache()
    database = Database("ratings.sqlite3")

    date = datetime.date.today().isoformat()

    for identifier, app in APP_STORE_APPS.items():
        for country in app["countries"]:
            if database.fetch_rating(date, APP_STORE, identifier, country) is None:
                if rating_info := fetch_app_store_rating_info(app["id"], country, cache):
                    rating = {"identifier": identifier, "id": app["id"], "country": country, "rating_info": rating_info}
                    print(rating)
                    database.insert_rating(Rating(date, APP_STORE, identifier, country, rating_info['rating']))


if __name__ == "__main__":
    main()
