import abc
from .gql_db import GQLdb


class GQLdbRepos(GQLdb):
    def __init__(self, logger, conn, function_name, token, min_stars, min_forks, set_query_limit=True):
        super().__init__(logger, function_name, token, set_query_limit)
        self.conn = conn
        self.function_name = function_name
        self.min_stars = min_stars
        self.min_forks = min_forks

    def _get_query(self):
        fQuery = open("gql/query/GetRepos.gql", mode='r')
        query = fQuery.read()
        fQuery.close()
        return query

    def _get_variables(self, initial_date, final_date, after_cursor):
        query_param = "stars:>{} forks:>{} created:{}..{}".format(self.min_stars, self.min_forks, initial_date, final_date)
        variables = {"queryParam": query_param, "cursor": after_cursor}
        return variables

    def _get_total_count_value(self, data):
        return data["data"]["search"]["repositoryCount"]

    def _preprocess_data(self, data):
        for edge in data["data"]["search"]["edges"]:
            all_releases = edge["repo"]["allReleases"]["totalCount"]
            merged_pullrequests = edge["repo"]["mergedPullRequests"]["totalCount"]
            repo_id = edge["repo"].get('id')
            repo_name = edge["repo"].get('name')
            repo_owner = edge["repo"]["owner"].get('login')
            repo_url = edge["repo"].get('url')
            repo_stargazer_count = edge["repo"].get('stargazerCount')
            repo_fork_count = edge["repo"].get('forkCount')
            cursor_conn = self.conn.cursor()
            sql = "INSERT INTO Repositories(CodeId, Name, Owner, Url, StargazerCount, ForkCount, TotalReleasesCount, MergedPullrequestsCount) VALUES (?, ?, ?, ?, ?, ?, ?, ?);"
            args = (repo_id, repo_name, repo_owner, repo_url, repo_stargazer_count, repo_fork_count, all_releases, merged_pullrequests)
            cursor_conn.execute(sql, args)
            self.conn.commit()

    def _get_has_next_page(self, data):
        return data["data"]["search"]["repos"]["hasNextPage"]

    def _get_after_cursor(self, data):
        return data["data"]["search"]["repos"]["endCursor"]

    def list_by_owner_and_name(self, owner, name):
        cursor_conn = self.conn.cursor()
        sql = "SELECT Id, Name, Owner FROM Repositories WHERE Name = ? AND Owner = ?"
        cursor_conn.execute(sql, (name, owner))
        return cursor_conn.fetchall()

    def list_all_with_data(self):
        cursor_conn = self.conn.cursor()
        sql = """   SELECT 
                        repo.Id, repo.Name, repo.Owner 
                    FROM 
                        Repositories repo
                    WHERE
                        repo.TotalReleasesCount > 50
                        AND repo.MergedPullrequestsCount > 50
                    GROUP BY 
                        repo.Id, repo.Name, repo.Owner
                    ORDER BY repo.Id; """
        cursor_conn.execute(sql)
        return cursor_conn.fetchall()

    def list_complementary_with_data(self, buffer_size):
        cursor_conn = self.conn.cursor()
        sql = """   SELECT 
                        repo.Id, repo.Name, repo.Owner 
                    FROM 
                        Repositories repo
                    WHERE
                        repo.TotalReleasesCount > 50
                        AND repo.MergedPullrequestsCount > 50
                        AND repo.LoadCompleted = 0
                    GROUP BY 
                        repo.Id, repo.Name, repo.Owner
                    ORDER BY repo.Id
                    LIMIT ?; """
        cursor_conn.execute(sql, [buffer_size])
        return cursor_conn.fetchall()

    def list_all(self):
        cursor_conn = self.conn.cursor()
        sql = "SELECT Id, Name, Owner FROM Repositories"
        cursor_conn.execute(sql)
        return cursor_conn.fetchall()

    def list_returninfo_data_by_repo_id_and_release_date(self, repo_id, release_date):
        cursor_conn = self.conn.cursor()
        sql = """   
            SELECT
                0 AS OrderId,
                Count(*) AS Total,
                sdpC.Name,
                release.IdRepository
            FROM
                SDPClassifications sdpC
                INNER JOIN SDPClassificationsReleases sdp ON sdp.IdSDPClassification = sdpC.Id
                INNER JOIN Releases release ON 
                    release.Id = sdp.IdRelease
                    AND release.UpdatedAt <= ?
                    AND release.IdRepository = ?
            GROUP BY sdpC.Name, release.IdRepository
            UNION ALL
            SELECT
                1 AS OrderId,
                Count(*) AS Total,
                sdpC.Name,
                release.IdRepository
            FROM
                SDPClassifications sdpC
                INNER JOIN SDPClassificationsReleases sdp ON sdp.IdSDPClassification = sdpC.Id
                INNER JOIN Releases release ON 
                    release.Id = sdp.IdRelease
                    AND release.UpdatedAt > ?
                    AND release.IdRepository = ?
            GROUP BY sdpC.Name, release.IdRepository
            ORDER BY OrderId, sdpC.Name;
              """
        cursor_conn.execute(sql, (release_date, repo_id, release_date, repo_id))
        return cursor_conn.fetchall()

    def list_returninfo_data(self):
        #sqlite> .mode csv
        #sqlite> .output poc.csv
        #sqlite> select * from tbl1;
        #sqlite> .output stdout
        cursor_conn = self.conn.cursor()
        sql = """   
              SELECT
                repo.Name AS RepoName,
                repo.Owner AS RepoOwner,
                release.Id AS ReleaseId,
                release.TagName AS ReleaseTagName,
                sdpC.Name AS SDPName,
                metricsC.Name AS MetricsName,
                metrics.Value as MetricsValue
              FROM
                Repositories repo
                INNER JOIN Releases release ON repo.Id = release.IdRepository
                INNER JOIN SDPClassificationsReleases sdp ON release.Id = sdp.IdRelease
                INNER JOIN SDPClassifications sdpC ON sdp.IdSDPClassification = sdpC.Id
                INNER JOIN ClassificationsMetricsReleases metrics ON metrics.IdRelease = release.Id
                INNER JOIN ClassificationMetrics metricsC ON metrics.IdClassificationMetric = metricsC.Id
              ORDER BY
                repo.Id,
                release.UpdatedAt
              ;
              """
        cursor_conn.execute(sql)
        return cursor_conn.fetchall()

    def list_returninfo_stats(self, repo_id, date_continuous):
        cursor_conn = self.conn.cursor()
        sql = """
            SELECT 
                AVG(metrics.Value),
                metricsC.Name AS MetricsName,
                'BEFORE Date' AS Period
            FROM 
                Repositories repo 
                INNER JOIN Releases release ON repo.Id = release.IdRepository
                INNER JOIN SDPClassificationsReleases sdp ON release.Id = sdp.IdRelease
                INNER JOIN SDPClassifications sdpC ON sdp.IdSDPClassification = sdpC.Id
                INNER JOIN ClassificationsMetricsReleases metrics ON metrics.IdRelease = release.Id
                INNER JOIN ClassificationMetrics metricsC ON metrics.IdClassificationMetric = metricsC.Id
            WHERE 
                repo.Id = ?
                AND release.UpdatedAt <= ?
            GROUP BY 
                metricsC.Name
            UNION ALL
            SELECT 
                AVG(metrics.Value),
                metricsC.Name AS MetricsName,
                'AFTER Date' AS Period
            FROM 
                Repositories repo 
                INNER JOIN Releases release ON repo.Id = release.IdRepository
                INNER JOIN SDPClassificationsReleases sdp ON release.Id = sdp.IdRelease
                INNER JOIN SDPClassifications sdpC ON sdp.IdSDPClassification = sdpC.Id
                INNER JOIN ClassificationsMetricsReleases metrics ON metrics.IdRelease = release.Id
                INNER JOIN ClassificationMetrics metricsC ON metrics.IdClassificationMetric = metricsC.Id
            WHERE 
                repo.Id = ?
                AND release.UpdatedAt > ?
            GROUP BY 
                metricsC.Name
            ;        
            """
        cursor_conn.execute(sql, (repo_id, date_continuous, repo_id, date_continuous))
        return cursor_conn.fetchall()

    def update_completed_load(self, repo_id):
        cursor_conn = self.conn.cursor()
        sql_upd = "UPDATE Repositories SET LoadCompleted = 1, UpdatedAt = datetime('now') WHERE Id = ?;"
        cursor_conn.execute(sql_upd, [repo_id])
        self.conn.commit()
