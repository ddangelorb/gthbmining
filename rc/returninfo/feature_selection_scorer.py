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


def autolabel(rects, ax, xpos='center'):
    """
    Attach a text label above each bar in *rects*, displaying its height.

    *xpos* indicates which side to place the text w.r.t. the center of
    the bar. It can be one of the following {'center', 'right', 'left'}.
    """

    ha = {'center': 'center', 'right': 'left', 'left': 'right'}
    offset = {'center': 0, 'right': 1, 'left': -1}

    for rect in rects:
        # print("{0:.0f}%".format(rect.get_height()*100))
        height = rect.get_height()
        ax.annotate('{}'.format("{0:.0f}%".format(height*100)),
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(offset[xpos]*3, 3),  # use 3 points offset
                    textcoords="offset points",  # in both directions
                    ha=ha[xpos], va='bottom')


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

        x_pos = np.arange(len(datalabels))
        mi = mutual_info_classif(X, y, discrete_features=True)

        fig, ax = plt.subplots(figsize=(16, 8))
        bars = ax.bar(x_pos, mi, color='grey')
        ax.set_ylabel('Mutual Information Score')
        ax.set_title('Release candidates based on ReleasesData fields')
        ax.set_xticks(x_pos)
        ax.set_xticklabels(datalabels)
        ax.legend()

        autolabel(bars, ax, "left")

        fig.tight_layout()
        plt.savefig("{}.png".format(path_plot_file))
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
