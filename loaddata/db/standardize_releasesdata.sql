UPDATE ReleasesData
    SET
        ClosedIssues = ClosedIssues / (SELECT MAX(ClosedIssues) FROM ReleasesData WHERE IdRepository = {}),
        ClosedPullRequests = ClosedPullRequests / (SELECT MAX(ClosedPullRequests) FROM ReleasesData WHERE IdRepository = {}),
        ClosedIssuesInfluencer = ClosedIssuesInfluencer / (SELECT MAX(ClosedIssuesInfluencer) FROM ReleasesData WHERE IdRepository = {}),
        ClosedPullRequestsInfluencer = ClosedPullRequestsInfluencer / (SELECT MAX(ClosedPullRequestsInfluencer) FROM ReleasesData WHERE IdRepository = {})
WHERE
    IdRepository = {}
;
