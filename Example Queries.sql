Queries



######## IX LIST ########

SELECT * FROM ix 
ORDER BY name COLLATE NOCASE;


######## PEERING LISTS ########


## All Peerings by IX
SELECT * FROM netixlan 
LEFT JOIN net ON net.id=netixlan.net_id
WHERE netixlan.name='AMS-IX'
ORDER BY net.name COLLATE NOCASE;

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



## All Peerings by ASN
SELECT * FROM netixlan 
LEFT JOIN net on net.id=netixlan.net_id 
WHERE net.asn=46489;



######## PEERING COUNTS ########

## Exchanges with most peers
SELECT * FROM ix 
ORDER BY net_count DESC 
LIMIT 10;

## NET with most peers
SELECT net.name, count(netixlan.id) AS peer_count FROM net
LEFT JOIN netixlan ON netixlan.net_id=net.id
GROUP BY net.name
ORDER BY peer_count DESC
LIMIT 25;

## Total Peerings
SELECT count(*) FROM netixlan;

## Total Peerings by IX
SELECT count(*) FROM netixlan
WHERE name='AMS-IX';

## Total Peerings by Continent
SELECT region_continent, count(netixlan.id) AS peer_count FROM netixlan
LEFT JOIN ix ON netixlan.ix_id=ix.id
GROUP BY region_continent
ORDER BY peer_count DESC;

## Total Peerings by Country
SELECT country, count(netixlan.id) AS peer_count FROM netixlan
LEFT JOIN ix ON netixlan.ix_id=ix.id
GROUP BY country
ORDER BY peer_count DESC
LIMIT 60;


## Total Peerings by ASN
SELECT net.name, count(netixlan.id) AS peer_count FROM net
LEFT JOIN netixlan ON netixlan.net_id=net.id
WHERE net.asn=15224 or net.asn=46489
GROUP BY net.name;




######## SPEED ########

## Total Speed
SELECT sum(speed) from netixlan;

## Total Speed by ASN
SELECT sum(speed) FROM netixlan 
LEFT JOIN net on net.id=netixlan.net_id 
WHERE net.asn=46489;

## Total Speed by IX
SELECT sum(speed) FROM netixlan 
LEFT JOIN ix on ix.id=netixlan.ix_id 
WHERE ix.name='AMS-IX';

## Total Speed by Continent
SELECT region_continent, sum(speed) AS total_speed
FROM netixlan
LEFT JOIN ix ON netixlan.ix_id=ix.id
GROUP BY region_continent
ORDER BY total_speed DESC;

## Total Speed by Country
SELECT country, sum(speed) AS total_speed
FROM netixlan
LEFT JOIN ix ON netixlan.ix_id=ix.id
GROUP BY country
ORDER BY total_speed DESC;


