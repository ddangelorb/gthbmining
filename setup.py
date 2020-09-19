from distutils.core import setup
setup(
    name='gthbmining',         # How you named your package folder (MyLib)
    packages=['gthbmining'],   # Chose the same as "name"
    version='1.0',      # Start with a small number and increase it with every change you make
    # Chose a license from here: https://help.github.com/articles/licensing-a-repository
    license='MIT',
    # Give a short description about your library
    description='A data mining set of tools to discover DevOps trends from public repositories.',
    author='Daniel D R Barros',                   # Type in your name
    author_email='ddangelorb@outlook.com',      # Type in your E-Mail
    # Provide either the link to your github or to your website
    url='https://github.com/ddangelorb/gthbmining',
    # I explain this later on
    download_url='https://github.com/ddangelorb/gthbmining/archive/V_1.tar.gz',
    # Keywords that define your package best
    keywords=['GitHub Mining Tool', 'Data Mining',
              'Release Candidate', 'DevOps'],
    install_requires=[            # I get to this in a second
        'github3.py',
        'pandas',
        'numpy',
        'scipy',
        'scikit-learn'
    ],
    classifiers=[
        # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
        'Development Status :: 5 - Production/Stable',
        # Define that your audience are developers
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',   # Again, pick a license
        # Specify which pyhton versions that you want to support
        'Programming Language :: Python :: 2.7',
        #'Programming Language :: Python :: 3',
        #'Programming Language :: Python :: 3.4',
        #'Programming Language :: Python :: 3.5',
        #'Programming Language :: Python :: 3.6',
    ],
)
