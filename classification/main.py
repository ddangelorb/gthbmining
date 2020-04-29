import sqlite3
from datetime import datetime
from sqlite3 import Error
from classifier import Classifier

db_path = "../loaddata/db/gthbmining.db"
repo_user = ""
repo_name = ""

def classify_db():
    conn = None
    try:
        print("sqlite3.version: {}".format(sqlite3.version))

        dburi = 'file:{}?mode=rw'.format(db_path)
        conn = sqlite3.connect(dburi)
        print("Database found and ready to operate")

        classifier = Classifier(conn, repo_user, repo_name)
        print("{} :: Starting Classifier.classify()...".format(datetime.today().strftime('%Y-%m-%d-%H:%M:%S')))
        classifier.classify()
        print("{} :: Classifier.classify() finished...".format(datetime.today().strftime('%Y-%m-%d-%H:%M:%S')))
    except Error as e:
        print("Error. classify_db: '{}'".format(e))
        conn = None
    finally:
        if conn is not None:
            conn.close()


if __name__ == '__main__':
    try:
        print("{} ** classification/main.py **".format(datetime.today().strftime('%Y-%m-%d-%H:%M:%S')))
        repo_user = raw_input("Repository user: ")
        repo_name = raw_input("Repository name: ")
        conn = None
        classify_db()
        print(" ** classification/main.py finished successfully ** ")
    except Exception as e:
        print("Error. __main__: '{}'".format(e))
