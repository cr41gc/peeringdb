
CREATE TABLE IF NOT EXISTS ix (
    id INTEGER PRIMARY KEY, 
    name TEXT, 
    net_count INTEGER, 
    region_continent TEXT, 
    country TEXT
);

CREATE TABLE IF NOT EXISTS net (
    id INTEGER PRIMARY KEY, 
    name TEXT, 
    asn INTEGER
);

CREATE TABLE IF NOT EXISTS netixlan (
    id INTEGER PRIMARY KEY,
    net_id INTEGER, 
    ix_id INTEGER, 
    name TEXT, 
    speed INTEGER,
    ipaddr4 TEXT,
    ipaddr6 TEXT
);