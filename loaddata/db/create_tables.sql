CREATE TABLE IF NOT EXISTS Repositories (
 Id integer PRIMARY KEY autoincrement,
 Code text NOT NULL,
 Url text NOT NULL,
 Name text NOT NULL
);

CREATE TABLE IF NOT EXISTS Contributors (
 Id integer PRIMARY KEY autoincrement,
 Name text NOT NULL,
 Login text NOT NULL,
 Url text NOT NULL,
 Followers integer NOT NULL,
 Following integer NOT NULL
);

CREATE TABLE IF NOT EXISTS RepositoriesContributors (
 Id integer PRIMARY KEY autoincrement,
 IdRepository integer NOT NULL,
 IdContributor integer NOT NULL,
 Contributions integer NOT NULL,
 Active integer NOT NULL,
 FOREIGN KEY (IdRepository) REFERENCES Repositories (Id),
 FOREIGN KEY (IdContributor) REFERENCES Contributors (Id)
);

CREATE TABLE IF NOT EXISTS Issues (
 Id integer PRIMARY KEY autoincrement,
 IdRepository integer NOT NULL,
 Login text NOT NULL,
 Code text NOT NULL,
 Description text NOT NULL,
 DtOpened text NOT NULL,
 DtClosed text NULL,
 FOREIGN KEY (IdRepository) REFERENCES Repositories (Id)
);

CREATE TABLE IF NOT EXISTS PullRequests (
 Id integer PRIMARY KEY autoincrement,
 IdRepository integer NOT NULL,
 IdContributor integer NOT NULL,
 Code text NOT NULL,
 IssueCode text NOT NULL,
 DtOpened text NOT NULL,
 State text NOT NULL,
 DtClosed text NULL,
 FOREIGN KEY (IdRepository) REFERENCES Repositories (Id),
 FOREIGN KEY (IdContributor) REFERENCES Contributors (Id)
);

CREATE TABLE IF NOT EXISTS Releases (
 Id integer PRIMARY KEY autoincrement,
 IdRepository integer NOT NULL,
 Author text NOT NULL,
 DtOpened text NOT NULL,
 Code text NOT NULL,
 Description text NOT NULL,
 DtPublished text NOT NULL,
 Tag text NOT NULL,
 TargetCommitish text NOT NULL,
 Prerelease integer NOT NULL,
 FOREIGN KEY (IdRepository) REFERENCES Repositories (Id)
);

CREATE TABLE IF NOT EXISTS ReleasesRawData (
 Id integer PRIMARY KEY autoincrement,
 IdRelease integer NOT NULL,
 IdRepository integer NOT NULL,
 AuthorInfluencer integer NULL,
 ClosedIssues real NULL,
 ClosedPullRequests real NULL,
 ClosedIssuesInfluencer real NULL,
 ClosedPullRequestsInfluencer real NULL,
 PrereleaseClass integer NOT NULL,
 DtTimeStamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS ReleasesData (
 Id integer PRIMARY KEY autoincrement,
 IdRelease integer NOT NULL,
 IdRepository integer NOT NULL,
 AuthorInfluencer integer NULL,
 ClosedIssues real NULL,
 ClosedPullRequests real NULL,
 ClosedIssuesInfluencer real NULL,
 ClosedPullRequestsInfluencer real NULL,
 PrereleaseClass integer NOT NULL,
 DtTimeStamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);