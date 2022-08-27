import abc
from .gql_db import GQLdb
from .db_repofiles import DbRepoFiles


class GQLdbRepoFilesVersions(GQLdb):
    def __init__(self, logger, conn, function_name, token, idRepo, repoName, owner, repoFileId, repoFilePath,
                 branch_name):
        super().__init__(logger, function_name, token)
        self.conn = conn
        self.function_name = function_name
        self.idRepo = idRepo
        self.repoName = repoName
        self.owner = owner
        self.repoFileId = repoFileId
        self.repoFilePath = repoFilePath
        self.branch_name = branch_name
        self.inserterRepoFiles = DbRepoFiles(conn, token, idRepo, repoName, owner, branch_name)

    def _get_query(self):
        fQuery = open("gql/query/GetFileContent.gql", mode='r')
        query = fQuery.read()
        fQuery.close()
        return query

    def _get_variables(self, initial_date, final_date, after_cursor):
        variables = {
            "name": self.repoName,
            "owner": self.owner,
            "expression": "{}:{}".format(self.branch_name, self.repoFilePath),
            "qualifiedName": self.branch_name,
            "path": self.repoFilePath,
            "cursor": after_cursor
        }
        return variables

    def _get_total_count_value(self, data):
        if data["data"]["repository"]["info"] is None or data["data"]["repository"]["info"]["target"]["history"]["totalCount"] is None:
            return -1

        return data["data"]["repository"]["info"]["target"]["history"]["totalCount"]

    def _preprocess_data(self, data):
        if data["data"]["repository"]["content"] is not None:
            if "text" in data["data"]["repository"]["content"]:
                repoFile_content = data["data"]["repository"]["content"]["text"]
                self.inserterRepoFiles.set_content(repoFile_content, self.repoFileId)

        if data["data"]["repository"]["info"] is not None:
            for node in data["data"]["repository"]["info"]["target"]["history"]["nodes"]:
                rfv_AuthorLogin = None
                if node["author"]["user"] is not None:
                    rfv_AuthorLogin = node["author"]["user"]["login"]
                rfv_Message = node["message"]
                rfv_PushedDate = node["pushedDate"]
                rfv_CommittedDate = node["committedDate"]
                rfv_AuthoredDate = node["authoredDate"]

                cursor_conn_ins = self.conn.cursor()
                sql_ins = "INSERT INTO RepositoriesFilesVersions(IdRepositoriesFiles, AuthorLogin, Message, PushedDate, CommittedDate, AuthoredDate) VALUES (?, ?, ?, ?, ?, ?);"
                args_ins = (
                self.repoFileId, rfv_AuthorLogin, rfv_Message, rfv_PushedDate, rfv_CommittedDate, rfv_AuthoredDate)
                cursor_conn_ins.execute(sql_ins, args_ins)
                self.conn.commit()

    def _get_has_next_page(self, data):
        return data["data"]["repository"]["info"]["target"]["history"]["pageInfo"]["hasNextPage"] if data["data"]["repository"]["info"] is not None else False

    def _get_after_cursor(self, data):
        return data["data"]["repository"]["info"]["target"]["history"]["pageInfo"]["endCursor"] if data["data"]["repository"]["info"] is not None else None
