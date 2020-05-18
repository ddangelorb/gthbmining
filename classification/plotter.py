import warnings
warnings.filterwarnings('ignore') #ignore warnings to print values properly
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.datasets import make_moons, make_circles, make_classification
from sklearn.neural_network import MLPClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.gaussian_process import GaussianProcessClassifier
from sklearn.gaussian_process.kernels import RBF
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.discriminant_analysis import QuadraticDiscriminantAnalysis

class Plotter:
    # constructor
    def __init__(self, name, classifier, X, y):
        self.h = .02  # step size in the mesh
        # self.names = ["K-Nearest Neighbors (3)", "Linear SVM", "RBF SVM", "Gaussian Process",
        #         "Decision Tree", "Random Forest", "Neural Net", "AdaBoost",
        #         "Naive Bayes", "QDA"]
        # self.classifiers = [
        #     KNeighborsClassifier(3),
        #     SVC(kernel="linear", C=0.025),
        #     SVC(gamma=2, C=1),
        #     GaussianProcessClassifier(1.0 * RBF(1.0)),
        #     DecisionTreeClassifier(max_depth=5),
        #     RandomForestClassifier(max_depth=5, n_estimators=10, max_features=1),
        #     MLPClassifier(alpha=1, max_iter=1000),
        #     AdaBoostClassifier(),
        #     GaussianNB(),
        #     QuadraticDiscriminantAnalysis()]
        self.name = name
        self.classifier = classifier
        self.X = X
        self.y = y
        

    def plot(self):
        figure = plt.figure(figsize=(27, 9))

        # preprocess dataset, split into training and test part
        self.X = StandardScaler().fit_transform(self.X)
        X_train, X_test, y_train, y_test = \
            train_test_split(self.X, self.y, test_size=.2, random_state=1)

        x_min, x_max = self.X[:, 0].min() - .5, self.X[:, 0].max() + .5
        y_min, y_max = self.X[:, 1].min() - .5, self.X[:, 1].max() + .5
        xx, yy = np.meshgrid(np.arange(x_min, x_max, self.h),
                            np.arange(y_min, y_max, self.h))

        # just plot the dataset first
        cm = plt.cm.RdBu
        #cm = plt.cm.gray
        cm_bright = ListedColormap(['#FF0000', '#0000FF'])
        #cm_bright = plt.cm.gray

        ax = plt.subplot(1, 2, 1)
        ax.set_title("Normalized Input data")
        # Plot the training points
        ax.scatter(X_train[:, 0], X_train[:, 1], c=y_train, cmap=cm_bright,
                edgecolors='k')
        # Plot the testing points
        ax.scatter(X_test[:, 0], X_test[:, 1], c=y_test, cmap=cm_bright, alpha=0.6,
                edgecolors='k')
        ax.set_xlim(xx.min(), xx.max())
        ax.set_ylim(yy.min(), yy.max())
        ax.set_xticks(())
        ax.set_yticks(())
        ax.set_xlabel('Closed Issues Influencers', fontsize=15)
        ax.set_ylabel('Closed PullRequests Influencers', fontsize=15)

        ax = plt.subplot(1, 2, 2)
        self.classifier.fit(X_train, y_train)
        score = self.classifier.score(X_test, y_test)

        # Plot the decision boundary. For that, we will assign a color to each
        # point in the mesh [x_min, x_max]x[y_min, y_max].
        if hasattr(self.classifier, "decision_function"):
            Z = self.classifier.decision_function(np.c_[xx.ravel(), yy.ravel()])
        else:
            Z = self.classifier.predict_proba(np.c_[xx.ravel(), yy.ravel()])[:, 1]

        # Put the result into a color plot
        Z = Z.reshape(xx.shape)
        ax.contourf(xx, yy, Z, cmap=cm, alpha=.8)

        # Plot the training points
        ax.scatter(X_train[:, 0], X_train[:, 1], c=y_train, cmap=cm_bright,
                edgecolors='k')
        # Plot the testing points
        ax.scatter(X_test[:, 0], X_test[:, 1], c=y_test, cmap=cm_bright,
                edgecolors='k', alpha=0.6)

        ax.set_xlim(xx.min(), xx.max())
        ax.set_ylim(yy.min(), yy.max())
        ax.set_xticks(())
        ax.set_yticks(())
        ax.set_title(self.name)

        plt.tight_layout()
        plt.show()
