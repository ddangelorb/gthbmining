import time
from gql.gql_db_repos import GQLdbRepos
from gql.gql_db_releases import GQLdbReleases
from gql.gql_db_mergedpullrequests import GQLdbMergedPullrequests
from gql.db_repofiles import DbRepoFiles
from gql.gql_db_repofilesversions import GQLdbRepoFilesVersions
from loaddata.gql.db_repolanguages import DbRepoLanguages
from loaddata.gql.gql_db_repobranches import GQLdbRepoBranches


class Loader:
    def __init__(self, logger, conn, token):
        self.logger = logger
        self.conn = conn
        self.token = token

    def _log_run(self, function_name):
        self.logger.info("     *) {}".format(function_name))

    def load(self, min_stars, min_forks, complementary_load, buffer_size):
        function_name = "insert_repos" if complementary_load == 0 else "complementary_load_repos"
        gql_db_repos = GQLdbRepos(self.logger, self.conn, function_name, self.token, min_stars, min_forks)
        self._log_run(function_name)

        repos = None
        if complementary_load == 0:
            gql_db_repos.insert()
            repos = gql_db_repos.list_all_with_data()
        else:
            repos = gql_db_repos.list_complementary_with_data(buffer_size)

        for repo in repos:
            repo_id = str(repo[0])
            repo_name = repo[1]
            repo_owner = repo[2]
            self._log_run(f"id:{repo_id}, repo:{repo_owner}/{repo_name}")

            gql_db_releases = GQLdbReleases(self.logger, self.conn, "insert_releases", self.token, repo_id, repo_name, repo_owner)
            self._log_run("     insert_releases")
            gql_db_releases.insert()

            gql_db_mergedprs = GQLdbMergedPullrequests(self.logger, self.conn, "insert_mergedpullrequests", self.token, repo_id, repo_name, repo_owner)
            self._log_run("     insert_mergedpullrequests")
            gql_db_mergedprs.insert()

            db_repolanguages = DbRepoLanguages(self.conn, self.token, repo_id, repo_name, repo_owner)
            self._log_run("     inserter_repolanguages")
            db_repolanguages.insert()

            gql_db_repobranches = GQLdbRepoBranches(self.logger, self.conn, "inserter_repobranches", self.token, repo_id, repo_name, repo_owner)
            self._log_run("     inserter_repobranches")
            gql_db_repobranches.insert()

            branch_name = gql_db_repobranches.get_default_name_repository_branch()
            db_repofiles = DbRepoFiles(self.conn, self.token, repo_id, repo_name, repo_owner, branch_name)
            self._log_run("     inserter_repofiles")
            db_repofiles.insert()

            gql_db_repobranches = GQLdbRepoBranches(self.logger, self.conn, "inserter_repobranches", self.token, repo_id, repo_name, repo_owner)
            branch_name = gql_db_repobranches.get_default_name_repository_branch()
            db_repofiles = DbRepoFiles(self.conn, self.token, repo_id, repo_name, repo_owner, branch_name)

            repo_files = db_repofiles.list_by_id_repo_with_continuous_delivery(repo_id)
            if len(repo_files) > 0:
                self._log_run("         about to start inserter_repofilesversions...")
                for repo_file in repo_files:
                    repo_file_id = str(repo_file[0])
                    repo_file_path = repo_file[1]
                    gql_db_repofilesversions = GQLdbRepoFilesVersions(self.logger, self.conn, "inserter_repofilesversions", self.token, repo_id, repo_name, repo_owner, repo_file_id, repo_file_path, branch_name)
                    gql_db_repofilesversions.insert()
            else:
                self._log_run("         no file with continuous delivery found, so no run for inserter_repofilesversions...")

            gql_db_repos.update_completed_load(repo_id)
            self.logger.info("          Sleeping for 5 seconds before the next repo...")
            time.sleep(5)
