DELETE FROM RepositoriesLanguages WHERE IdRepository IN (SELECT Id FROM Repositories WHERE LoadCompleted = 0);
DELETE FROM MergedPullrequests WHERE IdRepository IN (SELECT Id FROM Repositories WHERE LoadCompleted = 0);
DELETE FROM RepositoriesBranches WHERE IdRepository IN (SELECT Id FROM Repositories WHERE LoadCompleted = 0);
DELETE FROM RepositoriesFiles WHERE IdRepository IN (SELECT Id FROM Repositories WHERE LoadCompleted = 0);
DELETE FROM Releases WHERE IdRepository IN (SELECT Id FROM Repositories WHERE LoadCompleted = 0);
