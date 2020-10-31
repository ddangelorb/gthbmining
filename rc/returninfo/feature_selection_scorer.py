from scipy.stats import entropy
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import sqlite3
from datetime import datetime, time
from sqlite3 import Error
import logging
from six.moves.configparser import ConfigParser
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_selection import f_classif, mutual_info_classif
import warnings
warnings.filterwarnings('ignore')  # ignore warnings to print values properly

db_path = "../db/rc.db"
path_plot_file = "../output/fssplot"
repo_user = ""
repo_name = ""


def get_info_scorer():
    conn = None
    try:
        print("sqlite3.version: {}".format(sqlite3.version))
        logging.info("sqlite3.version: {}".format(sqlite3.version))

        dburi = 'file:{}?mode=rw'.format(db_path)
        conn = sqlite3.connect(dburi)
        print("Database found and ready to operate at '{}'".format(db_path))
        logging.info(
            "Database found and ready to operate at '{}'".format(db_path))

        datalabels = ['AuthorInfluencer', 'ClosedIssues', 'ClosedPullRequests',
                      'ClosedIssuesInfluencer', 'ClosedPullRequestsInfluencer']
        # Get X, y arrays for classification, normalized data
        sql = "SELECT rd.AuthorInfluencer, rd.ClosedIssues, rd.ClosedPullRequests, rd.ClosedIssuesInfluencer, rd.ClosedPullRequestsInfluencer, rd.PrereleaseClass FROM ReleasesData rd INNER JOIN Repositories r ON rd.IdRepository = r.Id WHERE r.Name = ?;"
        dataset = pd.read_sql_query(
            sql, conn, params=["{}/{}".format(repo_user, repo_name)])
        X = dataset[datalabels].values
        # contains the values from the "Class" column
        y = dataset['PrereleaseClass'].values

        count_datalabels = len(datalabels)
        mi = mutual_info_classif(X, y, discrete_features=True)
        mi /= np.max(mi)

        for i in range(count_datalabels):
            plt.figure(figsize=(16, 8))
            plt.scatter(X[:, i], y, edgecolor='black', s=20)
            plt.xlabel(datalabels[i])
            plt.ylabel("PrereleaseClass")
            plt.title("Mutual Information={:.2f}".format(mi[i]), fontsize=20)
            plt.savefig("{}_{}.png".format(path_plot_file, datalabels[i]))

    except Error as e:
        print("Error. classify_db: '{}'".format(e))
        logging.info("Error. classify_db: '{}'".format(e))
        conn = None
    finally:
        if conn is not None:
            conn.close()


if __name__ == '__main__':
    try:
        logging.basicConfig(
            filename="../output/classification_scorer.log", level=logging.INFO)

        print("{} ** returninfo/classification_scorer.py **".format(
            datetime.today().strftime('%Y-%m-%d-%H:%M:%S')))
        logging.info(
            "{} ** returninfo/classification_scorer **".format(datetime.today().strftime('%Y-%m-%d-%H:%M:%S')))

        # if you want some cache here, fill the file 'config.ini' with information you want
        config = ConfigParser()
        config.read('config.ini')
        repo_user = config.get("GitHubRepository", "user") if config.get(
            "GitHubRepository", "user") else raw_input("GitHub Repository user: ")
        repo_name = config.get("GitHubRepository", "projectname") if config.get(
            "GitHubRepository", "projectname") else raw_input("GitHub Repository project name: ")

        conn = None
        get_info_scorer()
        print(" ** returninfo/classification_scorer.py finished successfully ** ")
        logging.info(
            " ** returninfo/classification_scorer.py finished successfully ** ")
    except Exception as e:
        print("Error. __main__: '{}'".format(e))
        logging.info("Error. __main__: '{}'".format(e))
