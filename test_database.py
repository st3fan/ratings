# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/


from datetime import date
from tempfile import TemporaryDirectory

from database import Database, Rating


def test_create():
    with TemporaryDirectory() as path:
        db = Database(path + "/ratings.sqlite3")
        assert db is not None


def test_insert_rating():
    with TemporaryDirectory() as path:
        db = Database(path + "/ratings.sqlite3")
        today = date.today()
        r1 = Rating(today, "com.example.Example", 'us', 4.8)
        db.insert_rating(r1)
        r2 = db.fetch_rating(today, "com.example.Example", 'us',)
        assert r1 == r2
