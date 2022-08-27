import os
import sys
import sqlite3
import logging
from sqlite3 import Error
from loader import Loader
from configparser import ConfigParser

DEBUG = True #Production should be False
logger = logging.getLogger()

db_path = "../db/sdp4ossp.db"
ddl_sql_path = "sql/ddl.sql"
setup_sql_path = "sql/setup.sql"
delete_cache_loaded_path = "sql/delete_cache_loaded.sql"

min_stars = 0
min_forks = 0
token = ""
complementary_load = 0
buffer_size = 0


def set_logger():
    logging.basicConfig(
        filename="../output/loaddata.log",
        format='%(asctime)s.%(msecs)03d [%(levelname)s] {%(module)s - %(funcName)s}: %(message)s',
        level=logging.INFO
    )
    logger = logging.getLogger()
    if DEBUG:
        logger.addHandler(logging.StreamHandler(sys.stdout))


def load_db(ddl_sql, setup_sql, delete_cache_loaded, min_stars, min_forks, token, complementary_load, buffer_size):
    try:
        logger.info("sqlite3.version: {}".format(sqlite3.version))

        if complementary_load == 0:
            if os.path.exists(db_path):
                logger.info("Removing Database file for a new run, sqlite3 is creating a brand new one...")
                os.remove(db_path)
            else:
                logger.info("No previous Database file found, sqlite3 is creating a brand new one...")

            conn = sqlite3.connect(db_path)  # if not exists, create a db to a SQLite database
            logger.info("Database new ready to operate")

            cursor_ddl = conn.cursor()
            cursor_ddl.executescript(ddl_sql)
            conn.commit()
            logger.info("Database tables were properly created")

            cursor_setup = conn.cursor()
            cursor_setup.executescript(setup_sql)
            conn.commit()
            logger.info("Database config entities are up to date for starting a new load")
        else:
            conn = sqlite3.connect(db_path)  # if not exists, create a db to a SQLite database

            cursor_cache_loaded = conn.cursor()
            cursor_cache_loaded.executescript(delete_cache_loaded)
            conn.commit()

            logger.info("Database cached ready to operate")

        loader = Loader(logger, conn, token)
        logger.info(":: Starting Loader.load()...")
        loader.load(min_stars, min_forks, complementary_load, buffer_size)
        logger.info(":: Loader.load() finished...")
    except Error as e:
        logging.exception("Error. load_db_from_github")
        conn = None
        raise e
    except Exception as e:
        logging.exception("Exception. load_db_from_github")
        conn = None
        raise e
    finally:
        if conn is not None:
            conn.close()


if __name__ == '__main__':
    try:
        set_logger()
        logger.info("** loaddata/main.py **")

        # if you want some cache here, fill the file 'config.ini' with information you want
        config = ConfigParser()
        config.read('config.ini')

        if not config.get("GitHubConnection", "token"):
            logger.error(
                "Connection Error: Token not provided at config.ini file. \nPlease get your token accessing GitHub User's Settings / Developer settings / Personal access tokens. \nFurther details at 'https://developer.github.com/v3/auth/#basic-authentication'")
        else:
            min_stars = config.get("DEFAULT", "min_stars")
            min_forks = config.get("DEFAULT", "min_forks")
            token = config.get("GitHubConnection", "token")
            complementary_load = int(config.get("Load", "complementary_load"))
            buffer_size = int(config.get("Load", "buffer_size"))

            fDdl = open(ddl_sql_path, mode='r')
            ddl_sql = fDdl.read()
            fDdl.close()

            fSetup = open(setup_sql_path, mode='r')
            setup_sql = fSetup.read()
            fSetup.close()

            fDeleteCache = open(delete_cache_loaded_path, mode='r')
            delete_cache_loaded = fDeleteCache.read()
            fDeleteCache.close()

            load_db(ddl_sql, setup_sql, delete_cache_loaded, min_stars, min_forks, token, complementary_load, buffer_size)
            logger.info(" ** loaddata/main.py finished successfully ** ")
    except Exception as e:
        logger.error("Exception. __main__: '{}'".format(e))
