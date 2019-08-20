import sqlite3
from datetime import datetime
from sqlite3 import Error
from loaddata.loader import Loader

db_path = "db/gthbmining.db"
create_tables_path = "db/create_tables.sql"
insert_releasesdata_path = "db/insert_releasesdata.sql"
standardize_releasesdata_path = "db/standardize_releasesdata.sql"
github_user = ""
github_pwd = ""
repo_user = ""
repo_name = ""


def load_db_from_github(create_tables_sql, insert_releasesdata_sql, standardize_releasesdata_sql):
    try:
        print(f"sqlite3.version: {sqlite3.version}")

        conn = sqlite3.connect(db_path)  # if not exists, create a db to a SQLite database
        print("Database ready to operate")

        cursor_conn = conn.cursor()
        cursor_conn.executescript(create_tables_sql)
        conn.commit()
        print("Database tables ready to operate")

        loader = Loader(conn, github_user, github_pwd, repo_user, repo_name)
        print(f"{datetime.today().strftime('%Y-%m-%d-%H:%M:%S')} :: Starting Loader.load()...")
        loader.load(insert_releasesdata_sql, standardize_releasesdata_sql)
        print(f"{datetime.today().strftime('%Y-%m-%d-%H:%M:%S')} :: Loader.load() finished...")
    except Error as e:
        print(f"Error. load_db_from_github: '{e}'")
        conn = None
    finally:
        if conn is not None:
            conn.close()


if __name__ == '__main__':
    try:
        print(f"{datetime.today().strftime('%Y-%m-%d-%H:%M:%S')} ** loaddata/main.py **")
        github_user = input("GitHub user:")
        github_pwd = input("GitHub password: ")
        repo_user = input("Repository user: ")
        repo_name = input("Repository name: ")

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
    except Exception as e:
        print(f"Error. __main__: '{e}'")
