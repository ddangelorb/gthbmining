# gthbmining.rc
Predicting DevOps trends from data in public repositories database can be useful and strategical. Getting to know when a software will be available on Production is pertinent in a DevOps cycle, as this information can drive team planning or even a release strategy behind a software-as-a-service (SaaS) product.

One of the stages of development called as Release Candidates corresponds to versions that have already had all changes (bugs and enhancements) specified, developed and tested, therefore, unless a critical bug appears, this version is probably going to Production very soon. 

The main contribution here is predicting Release Candidates. This module contains a load component responsible for collecting data from a public repository, and a classification component that uses data loaded and applies three data mining supervised techniques (Naïve Bayes, Decision Tree and K-Nearest Neighbors) in order to classify Release Candidates or not.

Dependencies
------------
* Python 2
* scikit-learn
* [github3.py](https://github.com/github3py/github3py) by Ian Cordasco

Setting up
------------
Assuming you already have Python 2 installed follow the steps bellow. Otherwise, go to [Python download page](https://www.python.org/downloads/release/python-2716/) and install Python 2.

PS: The Python download link above redirects to Python 2.7.16, which was the last version tested.

	$ python --version
    $ pip install github3.py
    $ pip install pandas
    $ pip install numpy scipy scikit-learn

Running
------------
Before you run: After the project local cloning, bare in mind that you should at least provide your GitHub user Token in config.ini file (step two bellow).

	$ git clone https://github.com/ddangelorb/gthbmining.git
	$ vi gthbmining/rc/loaddata/config.ini
	$ cd gthbmining/rc
	$ cd loaddata
	$ python main.py
    $ cd ..
    $ cd returninfo
    $ python main.py

Please note: There is a [GitHub API Rate limiting](https://developer.github.com/v3/#rate-limiting). Therefore, we strongly recommend partial loads, specially if the repository to be analysed has a big history and data.


License
------------
MIT [license](https://github.com/ddangelorb/gthbmining/blob/master/LICENSE)

Author
------

[Daniel D'Angelo R. Barros](https://github.com/ddangelorb)
