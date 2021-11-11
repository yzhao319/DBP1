from sqlalchemy import *
from sqlalchemy.pool import NullPool

import click
from flask import current_app, g
from flask.cli import with_appcontext

DATABASEURI = "postgresql://yz4027:5063@35.196.73.133/proj1part2"
engine = create_engine(DATABASEURI)    

def get_db():
    if "db" not in g:
         g.db = engine.connect()
    
    return g.db
def close_db(e=None):
    try:
        g.conn.close()
    except Exception as e:
        pass

def init_db():
    try:
        g.conn = engine.connect()
    except:
        print ("uh oh, problem connecting to database")
        import traceback; traceback.print_exc()
        g.conn = None


@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)