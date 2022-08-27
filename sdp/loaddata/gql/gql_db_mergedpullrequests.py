import abc
from .gql_db import GQLdb
from .db_commits import DbCommits


class GQLdbMergedPullrequests(GQLdb):
    def __init__(self, logger, conn, function_name, token, idRepo, repoName, owner, set_query_limit=True):
        super().__init__(logger, function_name, token, set_query_limit)
        self.conn = conn
        self.function_name = function_name
        self.idRepo = idRepo
        self.repoName = repoName
        self.owner = owner
        self.mpr_id = 0
        self.inserterCommit = DbCommits(self.conn, "{}.{}".format(self.function_name, "insert_commits"))

    def _get_query(self):
        fQuery = open("gql/query/GetMergedPullrequests.gql", mode='r')
        query = fQuery.read()
        fQuery.close()
        return query

    def _get_variables(self, initial_date, final_date, after_cursor):
        query_param = "repo:{}/{} is:pr merged:{}..{}".format(self.owner, self.repoName, initial_date, final_date)
        variables = {"queryParam": query_param, "cursor": after_cursor}
        return variables

    def _get_total_count_value(self, data):
        return data["data"]["search"]["issueCount"]

    def _preprocess_data(self, data):
        for edge in data["data"]["search"]["edges"]:
            mpr_CodeId = edge["node"]["id"]
            mpr_AuthorLogin = None
            if edge["node"]["author"] is not None:
                mpr_AuthorLogin = edge["node"]["author"]["login"]
            mpr_Title = edge["node"]["title"]
            mpr_Url = edge["node"]["url"]
            mpr_Body = edge["node"]["body"]
            mpr_CreatedAt = edge["node"]["createdAt"]
            mpr_ClosedAt = edge["node"]["closedAt"]
            mpr_UpdatedAt = edge["node"]["updatedAt"]
            mpr_MergedAt = edge["node"]["mergedAt"]
            cursor_conn_ins = self.conn.cursor()
            sql_ins = "INSERT INTO MergedPullrequests(IdRepository, CodeId, AuthorLogin, Title, Url, Body, CreatedAt, ClosedAt, UpdatedAt, MergedAt) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);"
            args_ins = (
            self.idRepo, mpr_CodeId, mpr_AuthorLogin, mpr_Title, mpr_Url, mpr_Body, mpr_CreatedAt, mpr_ClosedAt,
            mpr_UpdatedAt, mpr_MergedAt)
            cursor_conn_ins.execute(sql_ins, args_ins)
            self.mpr_id = cursor_conn_ins.lastrowid
            self.conn.commit()

            if len(edge["node"]["commits"]["nodes"]) > 0:
                current_commit = edge["node"]["commits"]["nodes"][0]["commit"]
                commit_CodeId = current_commit["id"]
                commit_Message = current_commit["message"]
                commit_Url = current_commit["url"]
                commit_CommittedDate = current_commit["committedDate"]
                commit_Id = self.inserterCommit.get_id_by_codeid(commit_CodeId)
                if commit_Id == 0:
                    commit_Id = self.inserterCommit.insert(commit_CodeId, commit_Message, commit_Url,
                                                           commit_CommittedDate)

                cursor_conn_ins_mpr_commit = self.conn.cursor()
                sql_ins_mpr_commit = "INSERT INTO MergedPullrequestsCommits(IdMergedPullrequest, IdCommit) VALUES (? , ?);"
                cursor_conn_ins_mpr_commit.execute(sql_ins_mpr_commit, (self.mpr_id, commit_Id))
                self.conn.commit()

    def _get_has_next_page(self, data):
        return data["data"]["search"]["pageInfo"]["hasNextPage"]

    def _get_after_cursor(self, data):
        return data["data"]["search"]["pageInfo"]["endCursor"]

    def get_id_by_url_and_repo_id(self, url, repo_id):
        cursor_conn = self.conn.cursor()
        sql = "SELECT Id FROM MergedPullrequests WHERE Url = ? AND IdRepository = ?"
        cursor_conn.execute(sql, (url, repo_id))
        cursor_fetch = cursor_conn.fetchone()
        if cursor_fetch:
            return cursor_fetch[0]
        return 0

    def get_id_by_codeid(self, codeId):
        cursor_conn = self.conn.cursor()
        sql = "SELECT Id FROM MergedPullrequests WHERE CodeId = ?"
        cursor_conn.execute(sql, [codeId])
        cursor_fetch = cursor_conn.fetchone()
        if cursor_fetch:
            return cursor_fetch[0]
        return 0

    def list_with_latest_commit_by_repo_and_dates(self, repo_id, first_date, final_date):
        cursor_conn = self.conn.cursor()
        # latest commit is already filtered by in GQL insert
        sql = """   
                SELECT 
                    m.Id AS IdMergedPullrequest, c.Id AS IdCommit, c.CommittedDate
                FROM MergedPullrequests m 
                    INNER JOIN MergedPullrequestsCommits mc 
                        ON m.Id = mc.IdMergedPullrequest 
                    INNER JOIN Commits c 
                        ON mc.IdCommit = c.Id
                WHERE 
                    m.IdRepository = ? 
                    AND c.CommittedDate > ? 
                    AND c.CommittedDate < ?
                ORDER BY c.CommittedDate
            """
        cursor_conn.execute(sql, [repo_id, first_date, final_date])
        return cursor_conn.fetchall()

    def list_by_repo_id_and_closedissue_id(self, repo_id, ci_id):
        cursor_conn = self.conn.cursor()
        # latest commit is already filtered by in GQL insert
        sql = """   SELECT m.Id AS IdMergedPullrequest, c.Id AS IdCommit, c.CommittedDate
                    FROM MergedPullrequests m 
                        INNER JOIN MergedPullrequestsClosedIssues mci
                            ON m.Id = mci.IdMergedPullrequest
                        INNER JOIN MergedPullrequestsCommits mc 
                            ON m.Id = mc.IdMergedPullrequest 
                        INNER JOIN Commits c 
                            ON mc.IdCommit = c.Id
                    WHERE 
                        m.IdRepository = ?
                        AND mci.IdClosedIssue = ?
                    """
        cursor_conn.execute(sql, (repo_id, ci_id))
        return cursor_conn.fetchall()
