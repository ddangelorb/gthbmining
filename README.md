# gthbmining
A data mining set of tools to discover DevOps trends from public repositories. The name gthbmining stands for "GitHub mining", and this initiative has modules that apply data mining techniques to get strategical information from GitHub database repositories.

As a set of data mining tools, the construction of gthbmining operates with a single LICENSE file covering everything, one README.md file inside the root folder for the general project, and  a README.md file for each module. 

There are two components for each module inside gthbmining. The first one relates to loading and creating a relational and labeled database to receive all data available from source (in our case, all data available from the repository chosen). The second component aims at collecting data and applying data mining techniques in order to return relevant information. Data mining techniques can be supervisioned (like gthbmining.rc module uses Naïve Bayes, Decision Tree and K-Nearest Neighbors), or unsupervised.

The interactions with components inside gthbmining's modules are performed by terminal commands. When necessary, plots and logs from modules are provided in order to explain results and execution flow.

The gthbmining structure can be seen as a directory tree. The root folder (gthbmining) contains the files README.md and LICENSE, as well as several folders meaning many modules the set of tools provides. In the next level below the root folder, there are folders representing modules. These modules describe themselves through their own README.md file and have two components as folders as well: "loaddata" and "returninfo". Still at the modules' level, apart from "loaddata" and "returninfo" folders, there is one folder called "db" which contains the database file the module is working with, and finally there is a folder named "output" where logs and relevant outcomes are stored. 

All modules' interfaces through components are provided by command line. Looking at the next level underneath modules folder, individually all components have a main.py file that triggers the startup job the module's component is supposed to do. Under each module and its components there are unique constructions with files and directories.

The development language chosen by gthbmining and its modules is Python, an interpreted high-level programming language. The main reason to choose Python, as the main coding language for gthbmining modules, was the ability Python has to deal with data processing and analysis.

Due to dependences factors, this set of tools is still using Python 2. Future deploys will support Python 3.

Modules
------------
* [gthbmining.rc] (https://github.com/ddangelorb/gthbmining/tree/master/rc/) : The main contribution here is predicting Release Candidates, a pertinent information in a DevOps cycle.


License
------------
MIT [license](https://github.com/ddangelorb/gthbmining/blob/master/LICENSE)


Author
------
[Daniel D'Angelo R. Barros](https://github.com/ddangelorb)