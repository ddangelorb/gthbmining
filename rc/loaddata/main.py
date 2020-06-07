import sys
import sqlite3
from datetime import datetime
from sqlite3 import Error
from loader import Loader
import logging
from api.githubclient import GitHubClient

db_path = "../db/rc.db"
create_tables_path = "sql/create_tables.sql"
insert_releasesdata_path = "sql/insert_releasesdata.sql"
standardize_releasesdata_path = "sql/standardize_releasesdata.sql"
github_user = ""
github_pwd = ""
repo_user = ""
repo_name = ""
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

        loader = Loader(conn, github_user, github_pwd, repo_user, repo_name)
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

        if len(sys.argv) == 2 and sys.argv[1] == 'C':
            print("Loading cache data...")
            logging.info("Loading cache data...")
            #TODO implement the cache!
            #https://stackoverflow.com/questions/47660938/python-change-global-variable-from-within-another-file
        
        github_user = raw_input("GitHub user:")
        github_pwd = raw_input("GitHub password: ")
        repo_user = raw_input("Repository user: ")
        repo_name = raw_input("Repository name: ")
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
            gAPI = GitHubClient("facebook/react-native", "")
            repo = gAPI.get_repository()
            print(repo.id)
            print(repo.node_id)
            print(repo.url)
            print(repo.full_name)
            print(" Error. Wrong Load type informed. It should be between 1 and 4.")
            logging.info(" Error. Wrong Load type informed. It should be between 1 and 4.")
    except Exception as e:
        print("Error. __main__: '{}'".format(e))
        logging.error("Error. __main__: '{}'".format(e))