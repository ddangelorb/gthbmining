INSERT INTO ReleasesData (
 IdRelease,
 IdRepository,
 AuthorInfluencer,
 ClosedIssues,
 ClosedPullRequests,
 ClosedIssuesInfluencer,
 ClosedPullRequestsInfluencer,
 PrereleaseClass
)
SELECT
    r.Id,
    r.IdRepository,
    --r.TargetCommitish,
    --r.Tag,
    --r.Description,
    --CASE WHEN r.TargetCommitish LIKE '%stable' THEN 1 ELSE 0 END AS StableCommitish,
    CASE WHEN infl.Login IS NULL THEN 0 ELSE 1 END AS AuthorInfluencer,
    CASE WHEN ic.ClosedIssues IS NULL THEN 0 ELSE ic.ClosedIssues END AS ClosedIssues,
    CASE WHEN pc.ClosedPullRequests IS NULL THEN 0 ELSE pc.ClosedPullRequests END AS ClosedPullRequests,
    CASE WHEN icinfl.ClosedIssuesInfluencer IS NULL THEN 0 ELSE icinfl.ClosedIssuesInfluencer END AS ClosedIssuesInfluencer,
    CASE WHEN pcinfl.ClosedPullRequestsInfluencer IS NULL THEN 0 ELSE pcinfl.ClosedPullRequestsInfluencer END AS ClosedPullRequestsInfluencer,
    r.Prerelease
FROM
    Releases r
    INNER JOIN (SELECT MIN(Dt) as Dt FROM (SELECT MIN(DtOpened) AS Dt FROM Issues UNION SELECT MIN(DtOpened) AS Dt FROM PullRequests)) AS dtmin
        ON r.DtOpened >= dtmin.Dt
    LEFT JOIN (SELECT rc.IdRepository, rc.IdContributor, rc.Contributions, c.Id as IdContributor, c.Login, c.Followers from RepositoriesContributors rc  INNER JOIN Contributors c ON rc.IdContributor = c.Id ORDER BY c.Followers DESC, rc.Contributions DESC limit 100) AS infl
        ON r.Author = infl.Login
    LEFT JOIN (SELECT Count(i.Id) as ClosedIssues, (SELECT r.Id FROM Releases r WHERE r.DtOpened > i.DtClosed ORDER BY r.DtOpened ASC LIMIT 1) AS IdRelease FROM Issues i GROUP BY IdRelease) ic
        ON r.Id = ic.IdRelease
    LEFT JOIN (SELECT Count(p.Id) as ClosedPullRequests, (SELECT r.Id FROM Releases r WHERE r.DtOpened > p.DtClosed ORDER BY r.DtOpened ASC LIMIT 1) AS IdRelease FROM PullRequests p GROUP BY IdRelease) pc
        ON r.Id = pc.IdRelease
    LEFT JOIN (SELECT Count(i.Id) as ClosedIssuesInfluencer, (SELECT r.Id FROM Releases r WHERE r.DtOpened > i.DtClosed ORDER BY r.DtOpened ASC LIMIT 1) AS IdRelease FROM  Issues i INNER JOIN (select rc.IdRepository, rc.IdContributor, rc.Contributions, c.Id as IdContributor, c.Login, c.Followers from RepositoriesContributors rc  INNER JOIN Contributors c ON rc.IdContributor = c.Id ORDER BY c.Followers DESC, rc.Contributions DESC limit 100) AS infl ON i.Login = infl.Login GROUP BY IdRelease) icinfl
        ON r.Id = icinfl.IdRelease
    LEFT JOIN (SELECT Count(p.Id) as ClosedPullRequestsInfluencer, (SELECT r.Id FROM Releases r WHERE r.DtOpened > p.DtClosed ORDER BY r.DtOpened ASC LIMIT 1) AS IdRelease FROM  PullRequests p INNER JOIN (select rc.IdRepository, rc.IdContributor, rc.Contributions, c.Id as IdContributor, c.Login, c.Followers from RepositoriesContributors rc  INNER JOIN Contributors c ON rc.IdContributor = c.Id ORDER BY c.Followers DESC, rc.Contributions DESC limit 100) AS infl ON p.IdContributor = infl.IdContributor GROUP BY IdRelease) pcinfl
        ON r.Id = pcinfl.IdRelease
WHERE
    r.IdRepository = {}
;
