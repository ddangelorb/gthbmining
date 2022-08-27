import abc
from .gql_db import GQLdb


class GQLdbReleases(GQLdb):

    def __init__(self, logger, conn, function_name, token, idRepo, repoName, owner, set_query_limit=True):
        super().__init__(logger, function_name, token, set_query_limit)
        self.conn = conn
        self.function_name = function_name
        self.idRepo = idRepo
        self.repoName = repoName
        self.owner = owner

    def _get_query(self):
        fQuery = open("gql/query/GetReleases.gql", mode='r')
        query = fQuery.read()
        fQuery.close()
        return query

    def _get_variables(self, initial_date, final_date, after_cursor):
        variables = {"repoName": self.repoName, "owner": self.owner, "cursor": after_cursor}
        return variables

    def _get_total_count_value(self, data):
        return -1

    def _preprocess_data(self, data):
        for node in data["data"]["repository"]["releases"]["nodes"]:
            release_CodeId = node["id"]
            release_TagName = node["tagName"]
            release_Description = node["description"]
            if release_Description is None:
                release_Description = ""
            release_IsPrerelease = node["isPrerelease"]
            release_CreatedAt = node["createdAt"]
            release_updatedAt = node["updatedAt"]
            cursor_conn_ins = self.conn.cursor()
            sql_ins = "INSERT INTO Releases(IdRepository, CodeId, TagName, Description, IsPrerelease, CreatedAt, UpdatedAt) VALUES (?, ?, ?, ?, ?, ?, ?);"
            args_ins = (
            self.idRepo, release_CodeId, release_TagName, release_Description, release_IsPrerelease, release_CreatedAt,
            release_updatedAt)
            cursor_conn_ins.execute(sql_ins, args_ins)
            self.conn.commit()

    def _get_has_next_page(self, data):
        return data["data"]["repository"]["releases"]["pageInfo"]["hasNextPage"]

    def _get_after_cursor(self, data):
        return data["data"]["repository"]["releases"]["pageInfo"]["endCursor"]

    def list_by_repo_id(self, repo_id):
        cursor_conn = self.conn.cursor()
        sql = "SELECT Id, CodeId, TagName, Description, IsPrerelease, CreatedAt, UpdatedAt FROM Releases WHERE IdRepository = ? ORDER BY UpdatedAt ASC;"
        cursor_conn.execute(sql, [repo_id])
        return cursor_conn.fetchall()

    def get_min_max_date_by_repo_id(self, repo_id):
        cursor_conn = self.conn.cursor()
        sql = "SELECT MIN(UpdatedAt) AS MinReleaseDate, MAX(UpdatedAt) AS MaxReleaseDate FROM Releases WHERE IdRepository = ?;"
        cursor_conn.execute(sql, [repo_id])
        return cursor_conn.fetchone()

    def get_counts_by_repo_id_and_date(self, repo_id, date_release):
        cursor_conn = self.conn.cursor()
        sql = """
            SELECT 
                (
                    SELECT 
                        COUNT(*) 
                    FROM
                        Repositories repo
                        INNER JOIN Releases release ON repo.Id = release.IdRepository
                    WHERE 
                        repo.Id = ?
                        AND release.UpdatedAt <= ?
                ) AS CountReleasesBeforeDate,
                (
                    SELECT 
                        COUNT(*) 
                    FROM
                        Repositories repo
                        INNER JOIN Releases release ON repo.Id = release.IdRepository
                    WHERE 
                        repo.Id = ?
                        AND release.UpdatedAt > ?
                ) AS CountReleasesAfterDate;        
            """
        cursor_conn.execute(sql, (repo_id, date_release, repo_id, date_release))
        return cursor_conn.fetchone()
