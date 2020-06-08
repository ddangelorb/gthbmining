from github3 import login, authorize
from datetime import datetime
import logging

class Loader:
    # constructor
    def __init__(self, conn, github_user, github_pwd, repo_user, repo_name):
        logging.basicConfig(filename="../output/loaddata.log", level=logging.INFO)
        self.repository_id = 0
        self.conn = conn
        self.github_user = github_user
        self.github_pwd = github_pwd
        self.repo_user = repo_user
        self.repo_name = repo_name
        self.__set_repository_id()
        
    def __set_repository_id(self):
        cursor_conn = self.conn.cursor()
        self.repository_id = 1 #TODO, fix that! Should be dynamic!

    def _load_repository(self, repository):
        if repository is not None:
            cursor_conn = self.conn.cursor()
            sql = "INSERT INTO Repositories(Code, Url, Name) VALUES (?, ?, ?);"
            args = (repository.id, repository.url, repository.full_name)
            cursor_conn.execute(sql, args)
            self.repository_id = cursor_conn.lastrowid
            self.conn.commit()

    def _load_contributors(self, gh, contributors):
        if contributors is not None:
            cursor_conn = self.conn.cursor()
            for contributor in contributors:
                contributor_login = gh.user(contributor.login)
                contributor_login_name = contributor_login.name if contributor_login.name is not None else contributor.login
                contributor_followers = contributor_login.followers_count
                contributor_following = contributor_login.following_count

                sql = "INSERT INTO Contributors(Name, Login, Url, Followers, Following) VALUES (?, ?, ?, ?, ?);"
                args = (contributor_login_name, contributor.login, contributor.url, contributor_followers, contributor_following)
                cursor_conn.execute(sql, args)

                contributor_id = cursor_conn.lastrowid
                contributions = contributor.contributions
                self.conn.commit()
                self._load_respositories_contributors(contributor_id, contributions)

    def _load_respositories_contributors(self, contributor_id, contributions):
        cursor_conn = self.conn.cursor()
        sql = "INSERT INTO RepositoriesContributors(IdRepository, IdContributor, Contributions, Active) VALUES (?, ?, ?, 1);"
        args = (self.repository_id, contributor_id, contributions)
        cursor_conn.execute(sql, args)
        self.conn.commit()

    def _load_issues(self, issues):
        cursor_conn = self.conn.cursor()
        for issue in issues:
            sql = "INSERT INTO Issues(IdRepository, Login, Code, Description, DtOpened, DtClosed) VALUES (?, ?, ?, ?, ?, ?);"
            args = (self.repository_id, issue.user.login, issue.id, issue.title, issue.created_at, issue.closed_at)
            cursor_conn.execute(sql, args)
            self.conn.commit()

    def _load_pull_requests(self, pull_requests):
        cursor_conn = self.conn.cursor()
        for pull_request in pull_requests:
            sql = "INSERT INTO PullRequests(IdRepository, IdContributor, Code, IssueCode, DtOpened, State, DtClosed) SELECT ?, c.Id, ?, ?, ?, ?, ? FROM Contributors c WHERE c.Login = ?;"
            args = (self.repository_id, str(pull_request.id),  str(pull_request.issue().id), pull_request.created_at, pull_request.state, pull_request.closed_at, str(pull_request.user))
            cursor_conn.execute(sql, args)
            self.conn.commit()

    def _load_releases(self, releases):
        cursor_conn = self.conn.cursor()
        for release in releases:
            pre_release = 1 if str(release.prerelease) == "True" else 0
            sql = "INSERT INTO Releases(IdRepository, Author, DtOpened, Code, Description, DtPublished, Tag, TargetCommitish, Prerelease) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);"
            args = (self.repository_id, str(release.author), release.created_at, str(release.id), str(release.name), release.published_at, str(release.tag_name), str(release.target_commitish), pre_release)
            cursor_conn.execute(sql, args)
            self.conn.commit()

    def _load_releases_data(self, insert_releasesdata_sql, standardize_releasesdata_sql):
        cursor_insert = self.conn.cursor()
        sql_insert = insert_releasesdata_sql.format(self.repository_id)
        cursor_insert.executescript(sql_insert)
        self.conn.commit()

        cursor_insert_rawdata = self.conn.cursor()
        sql_insert_rawdata = "INSERT INTO ReleasesRawData SELECT * FROM ReleasesData;"
        cursor_insert_rawdata.executescript(sql_insert_rawdata)
        self.conn.commit()        

        cursor_standardize = self.conn.cursor()
        sql_standardize = standardize_releasesdata_sql.format(self.repository_id, self.repository_id, self.repository_id, self.repository_id, self.repository_id)
        cursor_standardize.executescript(sql_standardize)
        self.conn.commit()

    def load(self, insert_releasesdata_sql, standardize_releasesdata_sql, load_type):
        #gh = login(self.github_user, password=self.github_pwd)
        ##scopes = ['user', 'repo']
        ##auth = authorize(self.github_user, self.github_pwd, scopes, 'gthbmining', 'https://github.com/ddangelorb/gthbmining')
        ##print("Token: {}".format(auth.token))
        ##gh = login(token=auth.token)
        #TODO: Fix that shit: https://github3py.readthedocs.io/en/latest/examples/oauth.html
        ###gh = login(token="2325784b94d9943098a367238cdf1beae33bcc93")
        #https://stackoverflow.com/questions/47660938/python-change-global-variable-from-within-another-file

        ##repository = gh.repository(self.repo_user, self.repo_name)
        gh = None
        repository = None

        #Load type (1 - All, 2 - Basic [All except issues and pullrequests], 3 - Issues only, 4 - PullRequests only, 5 - RelasesData only [Classification Entity, after all loads])

        #load_type [All, Basic]
        if (load_type == 1) or (load_type == 2):
            print("{} ::     *) load_repository".format(datetime.today().strftime('%Y-%m-%d-%H:%M:%S')))
            logging.info("{} ::     *) load_repository".format(datetime.today().strftime('%Y-%m-%d-%H:%M:%S')))
            self._load_repository(repository)

            print("{} ::     *) load_contributors".format(datetime.today().strftime('%Y-%m-%d-%H:%M:%S')))
            logging.info("{} ::     *) load_contributors".format(datetime.today().strftime('%Y-%m-%d-%H:%M:%S')))
            contributors = repository.contributors()
            self._load_contributors(gh, contributors)

            print("{} ::     *) load_releases".format(datetime.today().strftime('%Y-%m-%d-%H:%M:%S')))
            logging.info("{} ::     *) load_releases".format(datetime.today().strftime('%Y-%m-%d-%H:%M:%S')))
            releases = repository.releases()
            self._load_releases(releases)

        #load_type [All, Issues only]
        if (load_type == 1) or (load_type == 3):
            print("{} ::     *) load_issues".format(datetime.today().strftime('%Y-%m-%d-%H:%M:%S')))
            logging.info("{} ::     *) load_issues".format(datetime.today().strftime('%Y-%m-%d-%H:%M:%S')))
            #  issues = repository.issues()
            #issues = repository.issues(state='closed', number=6000)
            issues = repository.issues(state='closed')
            self._load_issues(issues)

        #load_type [All, PullRequests only]
        if (load_type == 1) or (load_type == 4):
            print("{} ::     *) load_pull_requests".format(datetime.today().strftime('%Y-%m-%d-%H:%M:%S')))
            logging.info("{} ::     *) load_pull_requests".format(datetime.today().strftime('%Y-%m-%d-%H:%M:%S')))
            pull_requests = repository.pull_requests(state='closed', number=30000)
            #pull_requests = repository.pull_requests(state='closed')
            self._load_pull_requests(pull_requests)

        #load_type [All, ReleasesData only]
        if (load_type == 1) or (load_type == 5):
            print("{} ::     *) load_releases_data".format(datetime.today().strftime('%Y-%m-%d-%H:%M:%S')))
            logging.info("{} ::     *) load_releases_data".format(datetime.today().strftime('%Y-%m-%d-%H:%M:%S')))
            self._load_releases_data(insert_releasesdata_sql, standardize_releasesdata_sql)


