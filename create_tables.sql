CREATE TABLE IF NOT EXISTS top100 (
    repo TEXT NOT NULL,
    owner TEXT NOT NULL,
    position_cur INT NOT NULL,
    position_prev INT NOT NULL,
    stars INT NOT NULL,
    watchers INT NOT NULL,
    forks INT NOT NULL,
    open_issues INT NOT NULL,
    language TEXT,
    PRIMARY KEY (repo, owner)
);

CREATE TABLE IF NOT EXISTS activity (
    date DATE NOT NULL,
    commits INT NOT NULL,
    authors TEXT[] NOT NULL,
    repo TEXT NOT NULL,
    owner TEXT NOT NULL,
    PRIMARY KEY (date, repo, owner)
);
