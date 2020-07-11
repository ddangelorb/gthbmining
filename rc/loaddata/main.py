import sys
import sqlite3
from datetime import datetime
from sqlite3 import Error
from loader import Loader
import logging
from six.moves.configparser import ConfigParser

db_path = "../db/rc.db"
create_tables_path = "sql/create_tables.sql"
insert_releasesdata_path = "sql/insert_releasesdata.sql"
standardize_releasesdata_path = "sql/standardize_releasesdata.sql"
token = ""
repo_user = ""
repo_name = ""
max_rows_load_issues = 0
max_rows_load_pullrequests = 0
load_type = 0


def load_db_from_github(create_tables_sql, insert_releasesdata_sql, standardize_releasesdata_sql):
    try:
        print("sqlite3.version: {}".format(sqlite3.version))
        logging.info("sqlite3.version: {}".format(sqlite3.version))

        conn = sqlite3.connect(db_path)  # if not exists, create a db to a SQLite database
        print("Database ready to operate")
        logging.info("Database ready to operate")

        cursor_conn = conn.cursor()
        cursor_conn.executescript(create_tables_sql)
        conn.commit()
        print("Database tables ready to operate")
        logging.info("Database tables ready to operate")

        loader = Loader(conn, token, repo_user, repo_name, max_rows_load_issues, max_rows_load_pullrequests)
        print("{} :: Starting Loader.load()...".format(datetime.today().strftime('%Y-%m-%d-%H:%M:%S')))
        logging.info("{} :: Starting Loader.load()...".format(datetime.today().strftime('%Y-%m-%d-%H:%M:%S')))
        loader.load(insert_releasesdata_sql, standardize_releasesdata_sql, load_type)
        print("{} :: Loader.load() finished...".format(datetime.today().strftime('%Y-%m-%d-%H:%M:%S')))
        logging.info("{} :: Loader.load() finished...".format(datetime.today().strftime('%Y-%m-%d-%H:%M:%S')))
    except Error as e:
        print("Error. load_db_from_github: '{}'".format(e))
        logging.error("Error. load_db_from_github: '{}'".format(e))
        conn = None
    finally:
        if conn is not None:
            conn.close()


if __name__ == '__main__':
    try:
        logging.basicConfig(filename="../output/loaddata.log", level=logging.INFO)

        print("{} ** loaddata/main.py **".format(datetime.today().strftime('%Y-%m-%d-%H:%M:%S')))
        logging.info("{} ** loaddata/main.py **".format(datetime.today().strftime('%Y-%m-%d-%H:%M:%S')))

        #if you want some cache here, fill the file 'config.ini' with information you want
        config = ConfigParser()
        config.read('config.ini')

        if not config.get("GitHubConnection", "token") :
            print("Connection Error: Token not provided at config.ini file. \nPlease get your token accessing GitHub User's Settings / Developer settings / Personal access tokens. \nFurther details at 'https://developer.github.com/v3/auth/#basic-authentication'")
            logging.error("Connection Error: Token not provided at config.ini file. \nPlease get your token accessing GitHub User's Settings / Developer settings / Personal access tokens. \nFurther details at 'https://developer.github.com/v3/auth/#basic-authentication'")
        else:
            token = config.get("GitHubConnection", "token")
            repo_user = config.get("GitHubRepository", "user") if config.get("GitHubRepository", "user") else raw_input("GitHub Repository user: ")
            repo_name = config.get("GitHubRepository", "projectname") if config.get("GitHubRepository", "projectname") else raw_input("GitHub Repository project name: ")
            max_rows_load_issues = config.get("DEFAULT", "maxrowsloadissues") if config.get("DEFAULT", "maxrowsloadissues") else 0
            max_rows_load_pullrequests = config.get("DEFAULT", "maxrowsloadpullrequests") if config.get("DEFAULT", "maxrowsloadpullrequests") else 0
            load_type = int(raw_input("Load type \n(\n1 - All, \n2 - Basic [All except issues and pullrequests], \n3 - Issues only, \n4 - PullRequests only, \n5 - RelasesData only [Classification Entity, after all loads]\n): "))

            if 1 <= load_type <= 5:
                f = open(create_tables_path, mode='r')
                create_tables_sql = f.read()
                f.close()

                fi = open(insert_releasesdata_path, mode='r')
                insert_releasesdata_sql = fi.read()
                fi.close()

                fs = open(standardize_releasesdata_path, mode='r')
                standardize_releasesdata_sql = fs.read()
                fs.close()

                load_db_from_github(create_tables_sql, insert_releasesdata_sql, standardize_releasesdata_sql)
                print(" ** loaddata/main.py finished successfully ** ")
                logging.info(" ** loaddata/main.py finished successfully ** ")
            else:
                print(" Error. Wrong Load type informed. It should be between 1 and 4.")
                logging.error(" Error. Wrong Load type informed. It should be between 1 and 4.")
    except Exception as e:
        print("Error. __main__: '{}'".format(e))
        logging.error("Error. __main__: '{}'".format(e))