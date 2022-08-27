import requests
import json

class DbRepoFiles():
    def __init__(self, conn, token, idRepo, repoName, owner, branch_name):
        self.conn = conn
        self.query_url = f"https://api.github.com/repos/{owner}/{repoName}/git/trees/{branch_name}?recursive=1"
        self.headers = {'Authorization': f'token {token}'}
        self.idRepo = idRepo

    def insert(self):
        get_return = requests.get(self.query_url, headers=self.headers)
        if (get_return.status_code != 200):
            get_return.raise_for_status()

        data = json.loads(get_return.text)
        for tree in data["tree"]:
            rf_Path = tree["path"]
            rf_Mode = tree["mode"]
            rf_Type = tree["type"]
            rf_Sha = tree["sha"]
            rf_Size = None if "size" not in tree else tree["size"]
            rf_Url = None if "url" not in tree else tree["url"]

            cursor_conn_ins = self.conn.cursor()
            sql_ins = "INSERT INTO RepositoriesFiles(IdRepository, Path, Mode, Type, Sha, Size, Url) VALUES (?, ?, ?, ?, ?, ?, ?);"
            args_ins = (self.idRepo, rf_Path, rf_Mode, rf_Type, rf_Sha, rf_Size, rf_Url)
            cursor_conn_ins.execute(sql_ins, args_ins)
            self.conn.commit()

    def list_by_id_repo_with_continuous_delivery(self, id_repo):
        cursor_conn = self.conn.cursor()
        sql = """
            SELECT 
                Id, Path 
            FROM 
                RepositoriesFiles 
            WHERE 
                IdRepository = ?
                    AND (
                        Path LIKE '%pom.xml%'
                        OR Path LIKE '%build.xml%'
                        OR Path LIKE '%build.gradle%'
                        OR Path LIKE '%/Jenkinsfile%'
                        OR Path Like '%buddy.yml%'
                        OR Path LIKE '%.teamcity.%'
                        OR Path LIKE '%.circleci%'
                        OR Path LIKE '%.travis.yml%' 
                        OR Path LIKE '%config.xml%'
                        OR Path LIKE '%hydra.conf%'
                        OR Path LIKE '%makefile%'
                        OR Path LIKE '%pkgconfig%'
                        OR Path LIKE '%github/workflows/%.yml%'
                        OR Path LIKE '%github/workflows/%.yaml%'
                        
                        OR Path LIKE '%Dockerfile%'
                        OR Path LIKE '%ansible.cfg%'
                        OR Path LIKE '%puppet.conf%'
                        OR Path LIKE '%config.rb%'
                        OR Path LIKE '%salt/%.conf%'
                        OR Path LIKE '%hiera.yaml%'
                        OR Path LIKE '%yum.conf%'
                    );        
            """
        cursor_conn.execute(sql, [id_repo])
        return cursor_conn.fetchall()

    def get_date_cicd_by_id_repo(self, id_repo):
        cursor_conn = self.conn.cursor()
        sql = """
            SELECT 
                    MIN(rfv.PushedDate) AS CiCDdate
            FROM 
                RepositoriesFiles rf
                INNER JOIN RepositoriesFilesVersions rfv 
                    ON rf.Id = rfv.IdRepositoriesFiles
            WHERE 
                rf.IdRepository = ?
                    AND (
                        rf.Path LIKE '%pom.xml%'
                        OR rf.Path LIKE '%build.xml%'
                        OR rf.Path LIKE '%build.gradle%'
                        OR rf.Path LIKE '%/Jenkinsfile%'
                        OR rf.Path Like '%buddy.yml%'
                        OR rf.Path LIKE '%.teamcity.%'
                        OR rf.Path LIKE '%.circleci%'
                        OR rf.Path LIKE '%.travis.yml%' 
                        OR rf.Path LIKE '%config.xml%'
                        OR rf.Path LIKE '%hydra.conf%'
                        OR rf.Path LIKE '%makefile%'
                        OR rf.Path LIKE '%pkgconfig%'
                        OR rf.Path LIKE '%github/workflows/%.yml%'
                        OR rf.Path LIKE '%github/workflows/%.yaml%'

                        OR rf.Path LIKE '%Dockerfile%'
                        OR rf.Path LIKE '%ansible.cfg%'
                        OR rf.Path LIKE '%puppet.conf%'
                        OR rf.Path LIKE '%config.rb%'
                        OR rf.Path LIKE '%salt/%.conf%'
                        OR rf.Path LIKE '%hiera.yaml%'
                        OR rf.Path LIKE '%yum.conf%'
                    )
            """
        cursor_conn.execute(sql, [id_repo])
        cursor_fetch = cursor_conn.fetchone()
        if cursor_fetch:
            return cursor_fetch[0]
        return ""

    def set_content(self, content, id):
        cursor_conn_upd = self.conn.cursor()
        sql_upd = "UPDATE RepositoriesFiles SET Content = ? WHERE Id = ?;"
        cursor_conn_upd.execute(sql_upd, (content, id))
        self.conn.commit()

    def has_ci_tool(self, file_pushed_date):
        cursor_conn = self.conn.cursor()
        sql = """
                SELECT 
                    COUNT(*) AS Total 
                FROM 
                    RepositoriesFiles rf
                    INNER JOIN RepositoriesFilesVersions rfv 
                        ON rf.Id = rfv.IdRepositoriesFiles
                WHERE 
                    rf.IdRepository = ?
                    AND rfv.PushedDate <= ?
                    AND (
                        rf.Path LIKE '%pom.xml%'
                        OR rf.Path LIKE '%build.xml%'
                        OR rf.Path LIKE '%build.gradle%'
                        OR rf.Path LIKE '%/Jenkinsfile%'
                        OR rf.Path Like '%buddy.yml%'
                        OR rf.Path LIKE '%.teamcity.%'
                        OR rf.Path LIKE '%.circleci%'
                        OR rf.Path LIKE '%.travis.yml%' 
                        OR rf.Path LIKE '%config.xml%'
                        OR rf.Path LIKE '%hydra.conf%'
                        OR rf.Path LIKE '%makefile%'
                        OR rf.Path LIKE '%pkgconfig%'
                        OR (rf.Path LIKE '%github/workflows/%.yml%' AND rf.Content LIKE '%jobs:%build%:%')
                        OR (rf.Path LIKE '%github/workflows/%.yaml%' AND rf.Content LIKE '%jobs:%build%:%')
                    );        
                """
        args = (self.idRepo, file_pushed_date)
        cursor_conn.execute(sql, args)
        cursor_fetch = cursor_conn.fetchone()
        if cursor_fetch:
            return cursor_fetch[0] > 0
        return False

    def has_cd_tool(self, file_pushed_date):
        # 	Docker, Ansiable, Puppet, Chef, SaltStack, Hiera, Yum, GitHubActions
        cursor_conn = self.conn.cursor()
        sql = """
                SELECT 
                    COUNT(*) AS Total 
                FROM 
                    RepositoriesFiles rf
                    INNER JOIN RepositoriesFilesVersions rfv 
                        ON rf.Id = rfv.IdRepositoriesFiles
                WHERE 
                    rf.IdRepository = ?
                    AND rfv.PushedDate <= ?
                    AND (
                        rf.Path LIKE '%Dockerfile%'
                        OR rf.Path LIKE '%ansible.cfg%'
                        OR rf.Path LIKE '%puppet.conf%'
                        OR rf.Path LIKE '%config.rb%'
                        OR rf.Path LIKE '%salt/%.conf%'
                        OR rf.Path LIKE '%hiera.yaml%'
                        OR rf.Path LIKE '%yum.conf%'
                        OR (rf.Path LIKE '%github/workflows/%.yml%' AND rf.Content LIKE '%jobs:%deploy%:%')
                        OR (rf.Path LIKE '%github/workflows/%.yaml%' AND rf.Content LIKE '%jobs:%deploy%:%')
                        OR (rf.Path LIKE '%github/workflows/%.yml%' AND rf.Content LIKE '%jobs:%release%:%')
                        OR (rf.Path LIKE '%github/workflows/%.yaml%' AND rf.Content LIKE '%jobs:%release%:%')
                    );        
                """
        args = (self.idRepo, file_pushed_date)
        cursor_conn.execute(sql, args)
        cursor_fetch = cursor_conn.fetchone()
        if cursor_fetch:
            return cursor_fetch[0] > 0
        return False




