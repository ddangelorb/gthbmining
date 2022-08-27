import requests
import json


class DbRepoLanguages:
    def __init__(self, conn, token, id_repo, repo_name, owner):
        self.conn = conn
        self.query_url = f"https://api.github.com/repos/{owner}/{repo_name}/languages"
        self.headers = {'Authorization': f'token {token}'}
        self.id_repo = id_repo

    def insert(self):
        get_return = requests.get(self.query_url, headers=self.headers)
        if get_return.status_code != 200:
            get_return.raise_for_status()

        data = json.loads(get_return.text)
        for key, value in data.items():
            rl_language = key
            rl_value = value

            cursor_conn_ins = self.conn.cursor()
            sql_ins = "INSERT INTO RepositoriesLanguages(IdRepository, Language, Value) VALUES (?, ?, ?);"
            args_ins = (self.id_repo, rl_language, rl_value)
            cursor_conn_ins.execute(sql_ins, args_ins)
            self.conn.commit()


    def list_by_id_repo(self, id_repo):
        cursor_conn = self.conn.cursor()
        sql = "SELECT Id, Language, Value FROM RepositoriesLanguages WHERE IdRepository = ?"
        cursor_conn.execute(sql, [id_repo])
        return cursor_conn.fetchall()


    def get_main_language_by_id_repo(self, id_repo):
        cursor_conn = self.conn.cursor()
        sql = "SELECT Language FROM RepositoriesLanguages WHERE IdRepository = ? ORDER BY Value DESC LIMIT 1;"
        cursor_conn.execute(sql, [id_repo])
        return cursor_conn.fetchone()
