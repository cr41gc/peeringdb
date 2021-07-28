import requests
import sqlite3
from sqlite3 import OperationalError
from pprint import pprint


print("\nDB Init")
conn = sqlite3.connect('peering.db')
cursor = conn.cursor()
print(" - peering.db open")


cursor.execute("""
    CREATE TABLE IF NOT EXISTS ix (
        id INTEGER PRIMARY KEY, 
        name TEXT, 
        net_count INTEGER, 
        region_continent TEXT, 
        country TEXT
    )
""")
print(" - ix table present")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS net (
        id INTEGER PRIMARY KEY, 
        name TEXT, 
        asn INTEGER
    )
""")
print(" - net table present")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS netixlan (
        id INTEGER PRIMARY KEY,
        net_id INTEGER, 
        ix_id INTEGER, 
        name TEXT, 
        speed INTEGER,
        ipaddr4 TEXT,
        ipaddr6 TEXT
    )
""")
print(" - netixlan table present")


print("\nDB Update")
# Get all internet exchanges
print(" - Downloading ix data")
r = requests.get("https://www.peeringdb.com/api/ix").json()
print("   - done")
# Don't proceed when request fails
if r:
    # Empty table before reloading data
    cursor.execute("DELETE FROM ix")
    # Add fresh data into ix
    print(" - Loading ix data")
    for ix in r['data']:
        cursor.execute(f"""
            INSERT INTO ix VALUES (
                {ix['id']},
                '{ix['name'].replace("'","")}',
                {ix['net_count']},
                '{ix['region_continent'].replace("'","")}',
                '{ix['country'].replace("'","")}'
            )
        """)
    conn.commit()
    print("   - done")
    print(f" - {len(r['data'])} entries in ix")
else:
    print(f"FAILED REQUESTING ix DATA")
    print(r)
    print(r.text)


# Get all NETs (ASNs)
print(" - Downloading net data")
r = requests.get("https://www.peeringdb.com/api/net").json()
print("   - done")
# Don't proceed when request fails
if r:
    # Empty table before reloading data
    cursor.execute("DELETE FROM net")
    # Add new data into net
    print(" - Loading net data")
    for net in r['data']:
        cursor.execute(f"""
            INSERT INTO net VALUES (
                {net['id']}, 
               '{net['name'].replace("'","")}', 
                {net['asn']}
            )
        """)
    conn.commit()
    print("   - done")
    print(f" - {len(r['data'])} entries in net")
else:
    print(f"FAILED REQUESTING net DATA")
    print(r)
    print(r.text)


# Get all IX Peers
print(" - Downloading netixlan data")
r = requests.get("https://www.peeringdb.com/api/netixlan").json()
print("   - done")
# Don't proceed when request fails
if r:
    # Empty table before reloading data
    cursor.execute("DELETE FROM netixlan")
    # Add new data into net
    print(" - Loading netixlan data")
    for netixlan in r['data']:
        cursor.execute(f"""
            INSERT INTO netixlan VALUES (
                {netixlan['id']},
                {netixlan['net_id']},
                {netixlan['ix_id']},
                '{netixlan['name'].replace("'","")}',
                {netixlan['speed']},
                '{netixlan['ipaddr4']}',
                '{netixlan['ipaddr6']}'
            )
        """)
    conn.commit()
    print("   - done")
    print(f" - {len(r['data'])} entries in netixlan")
else:
    print(f"FAILED REQUESTING netixlan DATA")
    print(r)
    print(r.text)


conn.close()
