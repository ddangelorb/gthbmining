# gthbmining.rc
gthbmining stands for "GitHub mining" and is a data mining approuch to discover trends from public GitHub database repositories.

Due to dependences factors, this project is still using Python 2. Future deploys will support Python 3.

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
	$ python loaddata/main.py
    $ python classification/main.py

Please note: There is a [GitHub API Rate limiting](https://developer.github.com/v3/#rate-limiting). Therefore, we strongly recommend partial loads, specially if the repository to be analysed has a big history and data.


License
------------
MIT [license](https://github.com/ddangelorb/gthbmining/blob/master/LICENSE)

Author
------

[Daniel D'Angelo R. Barros](https://github.com/ddangelorb)
