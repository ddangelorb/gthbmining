import abc
from .gql_db import GQLdb


class GQLdbRepoBranches(GQLdb):

    def __init__(self, logger, conn, function_name, token, idRepo, repoName, owner):
        super().__init__(logger, function_name, token)
        self.conn = conn
        self.function_name = function_name
        self.idRepo = idRepo
        self.repoName = repoName
        self.owner = owner

    def _get_query(self):
        fQuery = open("gql/query/GetBranchNames.gql", mode='r')
        query = fQuery.read()
        fQuery.close()
        return query

    def _get_variables(self, initial_date, final_date, after_cursor):
        variables = {"name": self.repoName, "owner": self.owner, "cursor": after_cursor}
        return variables

    def _get_total_count_value(self, data):
        return -1

    def _preprocess_data(self, data):
        for node in data["data"]["repository"]["refs"]["nodes"]:
            branch_CodeId = node["id"]
            branch_Name = node["name"]

            cursor_conn_ins = self.conn.cursor()
            sql_ins = "INSERT INTO RepositoriesBranches(IdRepository, CodeId, Name) VALUES (?, ?, ?);"
            args_ins = (self.idRepo, branch_CodeId, branch_Name)
            cursor_conn_ins.execute(sql_ins, args_ins)
            self.conn.commit()

    def _get_has_next_page(self, data):
        return data["data"]["repository"]["refs"]["pageInfo"]["hasNextPage"]

    def _get_after_cursor(self, data):
        return data["data"]["repository"]["refs"]["pageInfo"]["endCursor"]

    def get_default_name_repository_branch(self):
        cursor_conn = self.conn.cursor()
        sql = """   SELECT Id, Name,
                        MAX(CASE Name
                                WHEN 'master' THEN 2
                                WHEN 'main' THEN 1
                                ELSE 0
                                END) AS Priority
                    FROM RepositoriesBranches
                    WHERE IdRepository = ?
                    GROUP BY Id
                    ORDER BY Priority DESC LIMIT 1 """
        cursor_conn.execute(sql, [self.idRepo])
        cursor_fetch = cursor_conn.fetchone()
        if cursor_fetch:
            return cursor_fetch[1]
        return "master"

    def list_by_id_repo(self):
        cursor_conn = self.conn.cursor()
        sql = "SELECT Id, Name FROM RepositoriesBranches WHERE IdRepository = ?;"
        cursor_conn.execute(sql, [self.idRepo])
        return cursor_conn.fetchall()

    def list_fix_branches_by_id_repo(self):
        cursor_conn = self.conn.cursor()
        sql = "SELECT Id, Name FROM RepositoriesBranches WHERE IdRepository = ? AND (Name LIKE '%fix%' OR Name LIKE '%patch%' OR Name LIKE '%error%');"
        cursor_conn.execute(sql, [self.idRepo])
        return cursor_conn.fetchall()
