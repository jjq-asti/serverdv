import logging
import time
from functools import partial, wraps, lru_cache
import sqlite3 as sql
import sys
import pandas as pd
import geopy
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from geopy.exc import GeocoderServiceError
#import tqdm
#from tqdm._tqdm_notebook import tqdm_notebook
DBNAME = 'addresses.db'
db = sql.connect(DBNAME)
cur = db.cursor()
query = """CREATE TABLE IF NOT EXISTS locations(
        id INT RIMARY KEY AUTO INCRIMENT,
        lat REAL NOT NULL,
        lon REAL NOT NULL,
        description TEXT NOT NULL,
        PRIMARY KEY(id))"""
cur.execute(query)
db.commit()
db.close()
def retry(func=None, exception=Exception, n_tries=5, delay=5, backoff=1, logger=True): # From SO by Redowan Delowar, Thanks!
    """Retry decorator with exponential backoff.

    Parameters
    ----------
    func : typing.Callable, optional
        Callable on which the decorator is applied, by default None
    exception : Exception or tuple of Exceptions, optional
        Exception(s) that invoke retry, by default Exception
    n_tries : int, optional
        Number of tries before giving up, by default 5
    delay : int, optional
        Initial delay between retries in seconds, by default 5
    backoff : int, optional
        Backoff multiplier e.g. value of 2 will double the delay, by default 1
    logger : bool, optional
        Option to log or print, by default False

    Returns
    -------
    typing.Callable
        Decorated callable that calls itself when exception(s) occur.

    Examples
    --------
    >>> import random
    >>> @retry(exception=Exception, n_tries=4)
    ... def test_random(text):
    ...    x = random.random()
    ...    if x < 0.5:
    ...        raise Exception("Fail")
    ...    else:
    ...        print("Success: ", text)
    >>> test_random("It works!")
    """

    if func is None:
        return partial(
            retry,
            exception=exception,
            n_tries=n_tries,
            delay=delay,
            backoff=backoff,
            logger=logger,
        )

    @wraps(func)
    def wrapper(*args, **kwargs):
        ntries, ndelay = n_tries, delay

        while ntries > 1:
            try:
                return func(*args, **kwargs)
            except exception as e:
                msg = f"{str(e)}, Retrying in {ndelay} seconds..."
                if logger:
                    logging.warning(msg)
                else:
                    print(msg)
                time.sleep(ndelay)
                ntries -= 1
                ndelay *= backoff

        return func(*args, **kwargs)

    return wrapper
def check_db(lat, lon):
    try:
        db = sql.connect(DBNAME)
        cur = db.cursor()
        query = """SELECT description FROM locations WHERE lat=? AND lon=?"""
        cur.execute(query,(lat,lon,))
        description = cur.fetchone()
        db.close()
        logging.info(description[0])
        return description
    except:
        return None

def save_location(lat, lon, location):
    db = sql.connect(DBNAME)
    query = '''INSERT INTO locations(lat, lon, description) VALUES(?,?,?)'''
    cur = db.cursor()
    cur.execute(query, (lat, lon, location.address))
    db.commit()
    db.close()


@retry(exception=Exception, n_tries=4)
@lru_cache
def get_location(geom):
    """ acquire location address by reverse geocoding.
        searches are stored in local db for caching. 
        return address on success, 0 if None.
    """
    lat = geom[0]
    lon = geom[1]
    #coordinates = "14.505025, 124.851131" 
    #coordinates = "14.647179, 121.072005"
    location = check_db(lat, lon)
    if not location:
        locator = Nominatim(user_agent="test")
        location = locator.reverse("{}, {}".format(lat, lon))

        if not location:
            return 0
        else:
            save_location(lat, lon, location)
            return location.address
    else:
        return location[0]

if __name__ == "__main__":
    coordinates = (14.647179, 121.072005)
    ret = get_location(coordinates)
    if not ret:
        print("location not found.")
    else:
        print(ret)
