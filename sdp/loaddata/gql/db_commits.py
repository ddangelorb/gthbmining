class DbCommits():
    def __init__(self, conn, function_name):
        self.conn = conn
        self.function_name = function_name

    def get_id_by_codeid(self, codeId):
        cursor_conn = self.conn.cursor()
        sql = "SELECT Id FROM Commits WHERE CodeId = ?"
        cursor_conn.execute(sql, [codeId])
        cursor_fetch = cursor_conn.fetchone()
        if cursor_fetch:
            return cursor_fetch[0]
        return 0

    def insert(self, codeId, message, url, committedDate):
        cursor_conn_ins_commit = self.conn.cursor()
        sql_ins_commit = "INSERT INTO Commits(CodeId, Message, Url, CommittedDate) VALUES (?, ?, ?, ?);"
        args_ins_commit = (codeId, message, url, committedDate)
        cursor_conn_ins_commit.execute(sql_ins_commit, args_ins_commit)
        commit_Id = cursor_conn_ins_commit.lastrowid
        self.conn.commit()
        return commit_Id
