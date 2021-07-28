import sqlite3
from flask import Flask
from flask import g
from flask import render_template
from flask import url_for

DATABASE = 'peering.db'

app = Flask(__name__)

@app.route("/")
def index():
    """
    Show Information about Twitch
     - ASN
     - Number of IX's
     - Number of Peerings
     - Links to present IX's and number of peerings and total bandwidth
     - Total Bandwidth
    Links to all the IX's
    """
    cur = get_db().cursor()
    
    r = query_db("SELECT count(*) AS total_ixs FROM ix;", one=True)
    total_ixs = r['total_ixs']

    r = query_db("SELECT count(*) AS total_nets FROM net;", one=True)
    total_nets = r['total_nets']

    r = query_db("SELECT count(*) AS total_peerings FROM netixlan;", one=True)
    total_peerings = r['total_peerings']

    r = query_db("SELECT sum(speed) AS total_speed FROM netixlan;", one=True)
    total_speed = r['total_speed']

    r = query_db("SELECT sum(speed) AS total_speed FROM netixlan;", one=True)
    total_speed = r['total_speed']
    
    return render_template("index.html", total_ixs=total_ixs, 
                                         total_nets=total_nets, 
                                         total_peerings=total_peerings, 
                                         total_speed=total_speed)

@app.route("/ix/")
def ix():
    return render_template("ix.html")

@app.route("/net/")
def net():
    return render_template("net.html")

@app.route("/peering/")
def peering():
    return render_template("peering.html")


def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

