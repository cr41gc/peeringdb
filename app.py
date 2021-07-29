import sqlite3
import requests
from datetime import datetime
from flask import Flask
from flask import g
from flask import render_template
from flask import url_for

DATABASE = 'peering.db'
DB_SCHEMA = 'schema.sql'
API_URL = 'https://www.peeringdb.com/api/'

app = Flask(__name__)


@app.route("/")
def index():
    
    r = query_db("SELECT count(*) AS total_ixs FROM ix", one=True)
    total_ixs = r['total_ixs']

    r = query_db("SELECT count(*) AS total_nets FROM net", one=True)
    total_nets = r['total_nets']

    r = query_db("SELECT count(*) AS total_peerings FROM netixlan", one=True)
    total_peerings = r['total_peerings']

    r = query_db("SELECT sum(speed) AS total_speed FROM netixlan", one=True)
    total_speed = format_speed(r['total_speed'])

    top_nets = query_db("""
        SELECT net.name AS name, 
               net.asn AS asn, 
               count(netixlan.id) AS peer_count 
        FROM net
        LEFT JOIN netixlan ON netixlan.net_id=net.id
        GROUP BY net.name, net.asn
        ORDER BY peer_count DESC
        LIMIT 20
    """)

    top_ixs = query_db("""
        SELECT ix.name AS name, 
               ix.id AS id, 
               count(netixlan.id) AS peer_count 
        FROM ix
        LEFT JOIN netixlan ON netixlan.ix_id=ix.id
        GROUP BY ix.name, ix.id
        ORDER BY peer_count DESC
        LIMIT 20
    """)

    dbtime = query_db("SELECT lastmodified from dbdate", one=True)['lastmodified']
    
    return render_template("index.html", total_ixs=total_ixs, 
                                         total_nets=total_nets, 
                                         total_peerings=total_peerings, 
                                         total_speed=total_speed,
                                         top_nets=top_nets,
                                         top_ixs=top_ixs,
                                         dbtime=dbtime)

@app.route("/ix/")
def ix():

    # num ix
    r = query_db("SELECT count(*) AS total_ixs FROM ix", one=True)
    total_ixs = r['total_ixs']

    # table of all ixs - # peerings, # nets, total speed, name
    all_ixs = query_db("""
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
    """)
    for row in all_ixs:
        row['total_speed']=format_speed(row['total_speed'])

    dbtime = query_db("SELECT lastmodified from dbdate", one=True)['lastmodified']

    return render_template("ix.html", total_ixs=total_ixs,
                                      all_ixs=all_ixs,
                                      dbtime=dbtime)

@app.route("/ix/<int:ix_id>")
def ix_id(ix_id):

    ix_info = query_db(f"""
        SELECT ix.name,
               net_count,
               region_continent,
               country,
               sum(speed) AS total_speed,
               count(netixlan.id) AS total_peerings
        FROM ix
        LEFT JOIN netixlan on netixlan.ix_id=ix.id
        WHERE ix.id={ix_id};
    """, one=True)
    ix_info['total_speed']=format_speed(ix_info['total_speed'])

    ix_peerings = query_db(f"""
        SELECT net.name,
               asn,
               speed,
               ipaddr4,
               ipaddr6
        FROM netixlan 
        LEFT JOIN net ON net.id=netixlan.net_id
        WHERE ix_id={ix_id}
        ORDER BY net.name COLLATE NOCASE;
    """)
    for row in ix_peerings:
        row['speed']=format_speed(row['speed'])

    dbtime = query_db("SELECT lastmodified from dbdate", one=True)['lastmodified']

    return render_template("ix_id.html", ix_info=ix_info,
                                         ix_peerings=ix_peerings,
                                         dbtime=dbtime) 

@app.route("/net/")
def net():

    # num net
    r = query_db("SELECT count(*) AS total_nets FROM net", one=True)
    total_nets = r['total_nets']

    # table of all nets - # peerings, # ixs, total speed, name
    all_nets = query_db("""
        SELECT net.name,
               asn,
               count(DISTINCT netixlan.ix_id) AS ix_count,
               count(netixlan.id) AS peer_count, 
               sum(speed) AS total_speed,
               count(DISTINCT country) AS total_countries
        FROM net
        LEFT JOIN netixlan ON net.id=netixlan.net_id
        LEFT JOIN ix on netixlan.ix_id=ix.id
        GROUP BY net.name
        ORDER BY peer_count DESC LIMIT 500;
    """)
    for row in all_nets:
        row['total_speed']=format_speed(row['total_speed'])

    dbtime = query_db("SELECT lastmodified from dbdate", one=True)['lastmodified']

    return render_template("net.html", total_nets=total_nets,
                                       all_nets=all_nets,
                                       dbtime=dbtime)

@app.route("/net/<int:asn>")
def net_asn(asn):

    net_info = query_db(f"""
        SELECT net.name AS name,
               COUNT(DISTINCT netixlan.ix_id) AS ix_num,
               COUNT(DISTINCT netixlan.id) AS peering_num,
               SUM(speed) AS total_speed,
               COUNT(DISTINCT country) AS country_count,
               COUNT(DISTINCT region_continent) AS reg_count
        FROM net
        LEFT JOIN netixlan ON net.id=netixlan.net_id
        LEFT JOIN ix ON netixlan.ix_id=ix.id
        WHERE asn={asn};
    """, one=True)
    net_info['total_speed']=format_speed(net_info['total_speed'])

    net_region = query_db(f"""
        SELECT COUNT(netixlan.id) AS peering_count, 
               country, 
               region_continent
        FROM ix
        LEFT JOIN netixlan ON ix.id=netixlan.ix_id
        LEFT JOIN net ON net.id=netixlan.net_id
        WHERE asn={asn} 
        GROUP BY country
        ORDER BY peering_count DESC;
    """)

    net_peers = query_db(f"""
        SELECT netixlan.name AS ix_name,
               ix_id,
               speed,
               ipaddr4,
               ipaddr6
        FROM net
        LEFT JOIN netixlan ON net.id=netixlan.net_id
        WHERE asn={asn}
        ORDER BY ix_name COLLATE NOCASE;
    """)
    for row in net_peers:
        row['speed']=format_speed(row['speed'])

    dbtime = query_db("SELECT lastmodified from dbdate", one=True)['lastmodified']

    return render_template("net_asn.html", net_info=net_info,
                                           net_region=net_region,
                                           net_peers=net_peers,
                                           dbtime=dbtime)


@app.route('/refresh')
def populate_db():
    init_db()

    # Get all internet exchanges
    ix_r = requests.get(API_URL+"ix").json()
    query_db("DELETE FROM ix")
    for ix in ix_r['data']:
        query_db(f"""
            INSERT INTO ix VALUES (
                {ix['id']},
                '{ix['name'].replace("'","")}',
                {ix['net_count']},
                '{ix['region_continent'].replace("'","")}',
                '{ix['country'].replace("'","")}'
            )
        """)

    # Get all NETs (ASNs)
    net_r = requests.get("https://www.peeringdb.com/api/net").json()
    query_db("DELETE FROM net")
    for net in net_r['data']:
        query_db(f"""
            INSERT INTO net VALUES (
                {net['id']}, 
               '{net['name'].replace("'","")}', 
                {net['asn']}
            )
        """)

    # Get all IX Peers
    peer_r = requests.get("https://www.peeringdb.com/api/netixlan").json()
    query_db("DELETE FROM netixlan")
    for netixlan in peer_r['data']:
        query_db(f"""
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

    query_db(f"INSERT INTO dbdate VALUES ('{datetime.now()}')")


    db = get_db()
    db.commit()
    db.close()

    stats = {
        "ix": len(ix_r['data']),
        "net": len(net_r['data']),
        "peer": len(peer_r['data']),
    }

    return render_template("refresh.html", stats=stats, dbtime=datetime.now())


def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = dict_factory
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource(DB_SCHEMA, mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

def format_speed(speed):
    if not speed:
        return speed
    n = 0
    label = {0: 'M', 1: 'G', 2: 'T', 3: 'P'}
    while speed >= 1000:
        speed /= 1000
        n += 1
    if speed == int(speed):
        speed = int(speed)
    else:
        speed=round(speed,1)
    return f"{speed}{label[n]}"


