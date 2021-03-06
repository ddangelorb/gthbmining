import sqlite3
from datetime import datetime
from sqlite3 import Error
from classifier import Classifier
import logging
from six.moves.configparser import ConfigParser

db_path = "../db/rc.db"
repo_user = ""
repo_name = ""

def classify_db():
    conn = None
    try:
        print("sqlite3.version: {}".format(sqlite3.version))
        logging.info("sqlite3.version: {}".format(sqlite3.version))

        dburi = 'file:{}?mode=rw'.format(db_path)
        conn = sqlite3.connect(dburi)
        print("Database found and ready to operate at '{}'".format(db_path))
        logging.info("Database found and ready to operate at '{}'".format(db_path))

        classifier = Classifier(conn, repo_user, repo_name)
        print("{} :: Starting Classification and Plotting ('decisiontree')...".format(datetime.today().strftime('%Y-%m-%d-%H:%M:%S')))
        logging.info("{} :: Starting Classification and Plotting ('decisiontree')...".format(datetime.today().strftime('%Y-%m-%d-%H:%M:%S')))
        classifier.classify('decisiontree')
        print("{} :: Classification and Plotting ('decisiontree') finished...".format(datetime.today().strftime('%Y-%m-%d-%H:%M:%S')))
        logging.info("{} :: Classification and Plotting ('decisiontree') finished...".format(datetime.today().strftime('%Y-%m-%d-%H:%M:%S')))

        print("{} :: Starting Classification and Plotting ('naivebayes')...".format(datetime.today().strftime('%Y-%m-%d-%H:%M:%S')))
        logging.info("{} :: Starting Classification and Plotting ('naivebayes')...".format(datetime.today().strftime('%Y-%m-%d-%H:%M:%S')))
        classifier.classify('naivebayes')
        print("{} :: Classification and Plotting ('naivebayes') finished...".format(datetime.today().strftime('%Y-%m-%d-%H:%M:%S')))
        logging.info("{} :: Classification and Plotting ('naivebayes') finished...".format(datetime.today().strftime('%Y-%m-%d-%H:%M:%S')))

        print("{} :: Starting Classification and Plotting ('knn')...".format(datetime.today().strftime('%Y-%m-%d-%H:%M:%S')))
        logging.info("{} :: Starting Classification and Plotting ('knn')...".format(datetime.today().strftime('%Y-%m-%d-%H:%M:%S')))
        classifier.classify('knn')
        print("{} :: Classification and Plotting ('knn') finished...".format(datetime.today().strftime('%Y-%m-%d-%H:%M:%S')))
        logging.info("{} :: Classification and Plotting ('knn') finished...".format(datetime.today().strftime('%Y-%m-%d-%H:%M:%S')))
    except Error as e:
        print("Error. classify_db: '{}'".format(e))
        logging.info("Error. classify_db: '{}'".format(e))
        conn = None
    finally:
        if conn is not None:
            conn.close()


if __name__ == '__main__':
    try:
        logging.basicConfig(filename="../output/returninfo.log", level=logging.INFO)
        
        print("{} ** returninfo/main.py **".format(datetime.today().strftime('%Y-%m-%d-%H:%M:%S')))
        logging.info("{} ** returninfo/main.py **".format(datetime.today().strftime('%Y-%m-%d-%H:%M:%S')))

        #if you want some cache here, fill the file 'config.ini' with information you want
        config = ConfigParser()
        config.read('config.ini')
        repo_user = config.get("GitHubRepository", "user") if config.get("GitHubRepository", "user") else raw_input("GitHub Repository user: ")
        repo_name = config.get("GitHubRepository", "projectname") if config.get("GitHubRepository", "projectname") else raw_input("GitHub Repository project name: ")

        conn = None
        classify_db()
        print(" ** returninfo/main.py finished successfully ** ")
        logging.info(" ** returninfo/main.py finished successfully ** ")
    except Exception as e:
        print("Error. __main__: '{}'".format(e))
        logging.info("Error. __main__: '{}'".format(e))
