# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/


from dataclasses import dataclass
from datetime import date
import sqlite3


@dataclass
class Rating:
    created_at: date
    store: str
    identifier: str
    country: str
    rating: float
    reviews: int
    stars: [int] # = [0, 0, 0, 0, 0]


RATINGS_TABLE_SQL = """
create table if not exists ratings (
  created_at text not null,
  store text not null,
  identifier text not null,
  country text not null,
  rating real not null,
  reviews int not null,
  stars1 int default 0,
  stars2 int default 0,
  stars3 int default 0,
  stars4 int default 0,
  stars5 int default 0,
  primary key (created_at, identifier, country)
);
"""

class Database:

    def __init__(self, path):
        self.path = path
        self.db = sqlite3.connect(path)
        self.db.execute(RATINGS_TABLE_SQL)

    def insert_rating(self, rating):
        sql = "insert into ratings (created_at, store, identifier, country, rating, reviews, stars1, stars2, stars3, stars4, stars5) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
        cur = self.db.cursor()
        try:
            cur.execute(sql, (rating.created_at, rating.store, rating.identifier, rating.country, rating.rating, rating.reviews, rating.stars[0], rating.stars[1], rating.stars[2], rating.stars[3], rating.stars[4]))
            self.db.commit()
        finally:
            cur.close()

    def fetch_rating(self, created_at, store, identifier, country):
        sql = "select created_at, store, identifier, country, rating, reviews, stars1, stars2, stars3, stars4, stars5 from ratings where created_at = ? and store = ? and identifier = ? and country = ?"
        if row := self.db.execute(sql, (created_at, store, identifier, country)).fetchone():
            return Rating(date.fromisoformat(row[0]), row[1], row[2], row[3], row[4], row[5], [row[6], row[7], row[8], row[9], row[10]])
