# PeeringDB Dashboard

This project is a simple exercise in displaying information from peeringdb.org/api.

It was my attempt to practice flask, python, sqlite, html, css, etc. It's been awhile since I built a web app!


## Anatomy Of This App

The app is running on flask, backed by a local sqlite3 database. The database gets populated by the python requests library pulling data down from the peeringdb API. The webpage doesn't pull from the peeringdb API directly in order to increase response time.

## Goals Of This App

list of all the public peerings grouped by peering exchange point name
total peering's
total unique organization peering's
total aggregate speed
other useful information

database backend
web frontend
automated code testing
AWS or cloud

## Building the Environment

```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
flask run
```

## Example DB Queries

### IX LIST 
```sql
SELECT * FROM ix 
ORDER BY name COLLATE NOCASE;
```

```sql
SELECT ix.id,
       ix.name,
       net_count,
       region_continent,
       country,
       sum(speed) AS total_speed,
       count(netixlan.id) AS total_peerings
FROM ix
LEFT JOIN netixlan on netixlan.ix_id=ix.id
GROUP BY ix.id
ORDER BY total_peerings DESC;
```

### PEERING LISTS 


#### All Peerings by IX
```sql
SELECT * FROM netixlan 
LEFT JOIN net ON net.id=netixlan.net_id
WHERE ix_id=26
ORDER BY net.name COLLATE NOCASE;
```

```sql
SELECT netixlan.name AS ix_name,
       net.name AS net_name,
       asn,
       speed,
       ipaddr4,
       ipaddr6
FROM netixlan 
LEFT JOIN net ON net.id=netixlan.net_id
WHERE netixlan.name='AMS-IX'
ORDER BY net.name COLLATE NOCASE;
```


#### All Peerings by ASN
```sql
SELECT * FROM netixlan 
LEFT JOIN net on net.id=netixlan.net_id 
WHERE net.asn=46489;
```


### PEERING COUNTS 

#### Exchanges with most peers
```sql
SELECT * FROM ix 
ORDER BY net_count DESC 
LIMIT 20;
```

#### NET with most peers
```sql
SELECT net.name, count(netixlan.id) AS peer_count FROM net
LEFT JOIN netixlan ON netixlan.net_id=net.id
GROUP BY net.name
ORDER BY peer_count DESC
LIMIT 25;
```

#### Total Peerings
```sql
SELECT count(*) FROM netixlan;
```

#### Total Peerings by IX
```sql
SELECT count(*) FROM netixlan
WHERE name='AMS-IX';
```

#### Total Peerings by Continent
```sql
SELECT region_continent, count(netixlan.id) AS peer_count FROM netixlan
LEFT JOIN ix ON netixlan.ix_id=ix.id
GROUP BY region_continent
ORDER BY peer_count DESC;
```

#### Total Peerings by Country
```sql
SELECT country, count(netixlan.id) AS peer_count FROM netixlan
LEFT JOIN ix ON netixlan.ix_id=ix.id
GROUP BY country
ORDER BY peer_count DESC
LIMIT 60;
```

#### Total Peerings by ASN
```sql
SELECT net.name, count(netixlan.id) AS peer_count FROM net
LEFT JOIN netixlan ON netixlan.net_id=net.id
WHERE net.asn=15224 or net.asn=46489
GROUP BY net.name;
```



### SPEED 

#### Total Speed
```sql
SELECT sum(speed) from netixlan;
```

#### Total Speed by ASN
```sql
SELECT sum(speed) FROM netixlan 
LEFT JOIN net on net.id=netixlan.net_id 
WHERE net.asn=46489;
```

#### Total Speed by IX
```sql
SELECT sum(speed) FROM netixlan 
LEFT JOIN ix on ix.id=netixlan.ix_id 
WHERE ix.name='AMS-IX';
```

#### Total Speed by Continent
```sql
SELECT region_continent, sum(speed) AS total_speed
FROM netixlan
LEFT JOIN ix ON netixlan.ix_id=ix.id
GROUP BY region_continent
ORDER BY total_speed DESC;
```

#### Total Speed by Country
```sql
SELECT country, sum(speed) AS total_speed
FROM netixlan
LEFT JOIN ix ON netixlan.ix_id=ix.id
GROUP BY country
ORDER BY total_speed DESC;
```

