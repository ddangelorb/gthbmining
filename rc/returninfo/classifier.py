import warnings
warnings.filterwarnings('ignore') #ignore warnings to print values properly
import logging
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn import metrics
from datetime import datetime
from plotter import Plotter


class Classifier:
    # constructor
    def __init__(self, conn, repo_user, repo_name):
        self.conn = conn
        self.repository_id = self._get_repository_id(repo_user, repo_name)
        self.dic_classifier = {
            'decisiontree': ["../output/decisiontreeplot.png", "Decision Tree", DecisionTreeClassifier(criterion="entropy", max_depth=3)],
            'naivebayes': ["../output/nbplot.png", "Naive Bayes", GaussianNB()],
            'knn': ["../output/knnplot.png", "K-Nearest Neighbors (3)", KNeighborsClassifier(n_neighbors=3)]
        }
        logging.basicConfig(filename="../output/returninfo.log", level=logging.INFO)

    def _get_repository_id(self, repo_user, repo_name):
        #TODO: Implement that!
        return 1

    def _print_scores(self, classifier, X, y, test_size):
        # Split dataset into training set and test set
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=1)

        # Train Decision Tree Classifer
        classifier.fit(X_train, y_train)

        # Predict the response for test dataset
        y_pred = classifier.predict(X_test)

        print("   Accuracy:", metrics.accuracy_score(y_test, y_pred))
        logging.info("   Accuracy: {}".format(metrics.accuracy_score(y_test, y_pred)))

        print("   F1-Score:", metrics.f1_score(y_test, y_pred))
        logging.info("   F1-Score: {}".format(metrics.f1_score(y_test, y_pred)))

        print("   Precision:", metrics.precision_score(y_test, y_pred))
        logging.info("   Precision: {}".format(metrics.precision_score(y_test, y_pred)))

        print("   Recall:", metrics.recall_score(y_test, y_pred))
        logging.info("   Recall: {}".format(metrics.recall_score(y_test, y_pred)))

        #print("   Confusion Matrix:", metrics.confusion_matrix(y_test, y_pred))

    def classify(self, classifier_key):
        if classifier_key in self.dic_classifier:
            dic_item = self.dic_classifier[classifier_key]
            classifier_path_plot_file = dic_item[0]
            classifier_name = dic_item[1]
            classifier_obj = dic_item[2]

            #Get X, y arrays for classification, normalized data
            sql = "SELECT AuthorInfluencer, ClosedIssues, ClosedPullRequests, ClosedIssuesInfluencer, ClosedPullRequestsInfluencer, PrereleaseClass FROM ReleasesData WHERE IdRepository = ?;"
            dataset = pd.read_sql_query(sql, self.conn, params=str(self.repository_id))
            X = dataset[['ClosedIssuesInfluencer', 'ClosedPullRequestsInfluencer']]
            y = dataset['PrereleaseClass']  # contains the values from the "Class" column
            self._print_scores(classifier_obj, X, y, test_size = 0.2)

            #Get XRaw, yRaw arrays for plotting, raw data
            sqlRaw = "SELECT AuthorInfluencer, ClosedIssues, ClosedPullRequests, ClosedIssuesInfluencer, ClosedPullRequestsInfluencer, PrereleaseClass FROM ReleasesRawData WHERE IdRepository = ?;"
            datasetRaw = pd.read_sql_query(sqlRaw, self.conn, params=str(self.repository_id))
            XRaw = dataset[['ClosedIssuesInfluencer', 'ClosedPullRequestsInfluencer']]
            yRaw = dataset['PrereleaseClass']  # contains the values from the "Class" column
            plotter = Plotter(classifier_name, classifier_obj, XRaw, yRaw)
            plotter.plot(classifier_path_plot_file)
            print("File '{}' plotted from current data and classifier '{}'".format(classifier_path_plot_file, classifier_name))
            logging.info("File '{}' plotted from current data and classifier '{}'".format(classifier_path_plot_file, classifier_name))
        else:
            print("{} :: classifier_key{} not found. Supported ones are: 'decisiontree', 'naivebayes', 'knn'".format(datetime.today().strftime('%Y-%m-%d-%H:%M:%S'), classifier_key))
            logging.info("{} :: classifier_key{} not found. Supported ones are: 'decisiontree', 'naivebayes', 'knn'".format(datetime.today().strftime('%Y-%m-%d-%H:%M:%S'), classifier_key))

