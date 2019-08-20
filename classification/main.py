import sqlite3
from datetime import datetime
from sqlite3 import Error
from classification.classifier import Classifier

db_path = "../loaddata/db/gthbmining.db"
repo_user = ""
repo_name = ""

def classify_db():
    try:
        print(f"sqlite3.version: {sqlite3.version}")

        dburi = 'file:{}?mode=rw'.format(db_path)
        conn = sqlite3.connect(dburi, uri=True)
        print("Database found and ready to operate")

        classifier = Classifier(conn, repo_user, repo_name)
        print(f"{datetime.today().strftime('%Y-%m-%d-%H:%M:%S')} :: Starting Classifier.classify()...")
        classifier.classify()
        print(f"{datetime.today().strftime('%Y-%m-%d-%H:%M:%S')} :: Classifier.classify() finished...")
    except Error as e:
        print(f"Error. classify_db: '{e}'")
        conn = None
    finally:
        if conn is not None:
            conn.close()


if __name__ == '__main__':
    try:
        print(f"{datetime.today().strftime('%Y-%m-%d-%H:%M:%S')} ** classification/main.py **")
        repo_user = input("Repository user: ")
        repo_name = input("Repository name: ")
        classify_db()
        print(" ** classification/main.py finished successfully ** ")
    except Exception as e:
        print(f"Error. __main__: '{e}'")
