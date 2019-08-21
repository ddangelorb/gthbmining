import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn import metrics


class Classifier:
    # constructor
    def __init__(self, conn, repo_user, repo_name):
        self.conn = conn
        self.repository_id = self._get_repository_id(repo_user, repo_name)

    def _get_repository_id(self, repo_user, repo_name):
        return 1

    def _classify_by_decisiontree(self, X, y, test_size):
        # Split dataset into training set and test set
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=1)

        # Create Decision Tree classifer object
        classifier = DecisionTreeClassifier(criterion="entropy", max_depth=3)

        # Train Decision Tree Classifer
        classifier.fit(X_train, y_train)

        # Predict the response for test dataset
        y_pred = classifier.predict(X_test)

        # Model Accuracy, how often is the classifier correct?
        print("DecisionTreeClassifier Accuracy:", metrics.accuracy_score(y_test, y_pred))

    def _classify_by_naivebayes(self, X, y, test_size):
        # Split dataset into training set and test set
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=1)

        # Create a Gaussian Classifier
        classifier = GaussianNB()

        #Train the model using the training sets
        classifier.fit(X_train, y_train)

        # Predict the response for test dataset
        y_pred = classifier.predict(X_test)

        # Model Accuracy, how often is the classifier correct?
        print("NaiveBayesClassifier Accuracy:", metrics.accuracy_score(y_test, y_pred))

    def _classify_by_knn(self, X, y, test_size, neighbors):
        # Split dataset into training set and test set
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=1)

        # Create KNN Classifier
        classifier = KNeighborsClassifier(n_neighbors=neighbors)

        #Train the model using the training sets
        classifier.fit(X_train, y_train)

        # Predict the response for test dataset
        y_pred = classifier.predict(X_test)

        print("KNN3Classifier Accuracy:", metrics.accuracy_score(y_test, y_pred))

    def classify(self):
        sql = "SELECT AuthorInfluencer, ClosedIssues, ClosedPullRequests, ClosedIssuesInfluencer, ClosedPullRequestsInfluencer, PrereleaseClass FROM ReleasesData WHERE IdRepository = ?;"
        dataset = pd.read_sql_query(sql, self.conn, params=str(self.repository_id))

        X = dataset.drop('PrereleaseClass', axis=1)  # contains all the columns from the dataset, except the "Class" column
        y = dataset['PrereleaseClass']  # contains the values from the "Class" column
        test_size = 0.2

        self._classify_by_decisiontree(X, y, test_size)
        self._classify_by_naivebayes(X, y, test_size)
        self._classify_by_knn(X, y, test_size, 3)
