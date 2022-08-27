CREATE TABLE IF NOT EXISTS SDPClassifications (
    Id integer PRIMARY KEY autoincrement,
    Name text NOT NULL,
    Description text NOT NULL
);

CREATE TABLE IF NOT EXISTS ClassificationMetrics (
    Id integer PRIMARY KEY autoincrement,
    Name text NOT NULL,
    Description text NOT NULL,
    GettingMethod text NOT NULL
);


CREATE TABLE IF NOT EXISTS Repositories (
    Id integer PRIMARY KEY autoincrement,
    CodeId text NOT NULL,
    Name text NOT NULL,
    Owner text NOT NULL,
    Url text NOT NULL,
    StargazerCount integer NOT NULL,
    ForkCount integer NOT NULL,
    TotalReleasesCount integer NULL,
    MergedPullrequestsCount integer NULL,
    LoadCompleted integer DEFAULT 0 NOT NULL,
    UpdatedAt text DEFAULT (datetime('now')) NOT NULL,
    UNIQUE(Name, Owner) ON CONFLICT REPLACE
);


CREATE TABLE IF NOT EXISTS Releases (
    Id integer PRIMARY KEY autoincrement,
    IdRepository integer NOT NULL,
    CodeId text NOT NULL UNIQUE,
    TagName text NOT NULL,
    Description text NOT NULL,
    IsPrerelease integer NOT NULL,
    CreatedAt text NOT NULL,
    UpdatedAt text NOT NULL,
    FOREIGN KEY (IdRepository) REFERENCES Repositories (Id) ON DELETE CASCADE
);


CREATE TABLE IF NOT EXISTS SDPClassificationsReleases (
    Id integer PRIMARY KEY autoincrement,
    IdRelease integer NOT NULL,
    IdSDPClassification integer NOT NULL,
    FOREIGN KEY (IdRelease) REFERENCES Releases (Id) ON DELETE CASCADE,
    FOREIGN KEY (IdSDPClassification) REFERENCES SDPClassifications (Id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS ClassificationsMetricsReleases (
    Id integer PRIMARY KEY autoincrement,
    IdRelease integer NOT NULL,
    IdClassificationMetric integer NOT NULL,
    Value text NOT NULL,
    FOREIGN KEY (IdRelease) REFERENCES Releases (Id) ON DELETE CASCADE,
    FOREIGN KEY (IdClassificationMetric) REFERENCES ClassificationMetrics (Id) ON DELETE CASCADE
);


CREATE TABLE IF NOT EXISTS RepositoriesFiles (
    Id integer PRIMARY KEY autoincrement,
    IdRepository integer NOT NULL,
    Path text NOT NULL,
    Mode text NOT NULL,
    Type text NOT NULL,
    Sha text NOT NULL,
    Url text NULL,
    Size integer NULL,
    Content text NULL,
    FOREIGN KEY (IdRepository) REFERENCES Repositories (Id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS RepositoriesFilesVersions (
    Id integer PRIMARY KEY autoincrement,
    IdRepositoriesFiles integer NOT NULL,
    AuthorLogin text NULL,
    Message text NOT NULL,
    PushedDate text NULL,
    CommittedDate text NOT NULL,
    AuthoredDate text NOT NULL,
    FOREIGN KEY (IdRepositoriesFiles) REFERENCES RepositoriesFiles (Id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS RepositoriesBranches (
    Id integer PRIMARY KEY autoincrement,
    IdRepository integer NOT NULL,
    CodeId text NOT NULL,
    Name text NOT NULL,
    FOREIGN KEY (IdRepository) REFERENCES Repositories (Id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Commits (
    Id integer PRIMARY KEY autoincrement,
    CodeId text NOT NULL UNIQUE,
    Message text NOT NULL,
    Url text NOT NULL,
    CommittedDate text NOT NULL
);


CREATE TABLE IF NOT EXISTS MergedPullrequests (
    Id integer PRIMARY KEY autoincrement,
    IdRepository integer NOT NULL,
    CodeId text NOT NULL,
    AuthorLogin text NULL,
    Title text NOT NULL,
    Url text NOT NULL,
    Body text NOT NULL,
    CreatedAt text NOT NULL,
    ClosedAt text NULL,
    UpdatedAt text NOT NULL,
    MergedAt text NULL,
    FOREIGN KEY (IdRepository) REFERENCES Repositories (Id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS MergedPullrequestsCommits (
    Id integer PRIMARY KEY autoincrement,
    IdMergedPullrequest integer NOT NULL,
    IdCommit integer NOT NULL,
    FOREIGN KEY (IdMergedPullrequest) REFERENCES MergedPullrequests (Id) ON DELETE CASCADE,
    FOREIGN KEY (IdCommit) REFERENCES Commits (Id) ON DELETE CASCADE
);


CREATE TABLE IF NOT EXISTS RepositoriesLanguages (
    Id integer PRIMARY KEY autoincrement,
    IdRepository integer NOT NULL,
    Language text NOT NULL,
    Value integer NOT NULL,
    FOREIGN KEY (IdRepository) REFERENCES Repositories (Id) ON DELETE CASCADE
);
