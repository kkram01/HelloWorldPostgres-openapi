# Please read for best practices https://cloud.google.com/sql/docs/postgres/manage-connections


import os
from flask import jsonify
from apiflask import APIFlask
import sqlalchemy
from sqlalchemy import text

def config() -> dict:
    """This will create a map of all database config read as environment variables"""
    params = {}
    params['DB_HOST'] = os.environ['DB_HOST']
    params['DB_USER'] = os.environ['DB_USER']
    params['DB_PASS'] = os.environ['DB_PASS']
    params['DB_NAME'] = os.environ['DB_NAME']
    params['DB_PORT'] = os.environ['DB_PORT']
    params['POOL_SIZE'] = int(os.environ['POOL_SIZE']) if os.getenv("POOL_SIZE") else 5
    params['MAX_OVERFLOW']= int(os.environ['MAX_OVERFLOW']) if os.getenv("MAX_OVERFLOW") else 2
    params['POOL_TIMEOUT']= int(os.environ['POOL_TIMEOUT']) if os.getenv("POOL_TIMEOUT") else 30
    params['POOL_RECYCLE']= int(os.environ['POOL_RECYCLE']) if os.getenv("POOL_RECYCLE") else 1800
    return params

def connect():
    """ Connect to the PostgreSQL database server """
    try:
        # Read connection parameters
        params = config()

        # Connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database...')
        pool = sqlalchemy.create_engine(
            # Equivalent URL:
            # postgresql+pg8000://<db_user>:<db_pass>@<db_host>:<db_port>/<db_name>
            sqlalchemy.engine.url.URL.create(
                drivername="postgresql+pg8000",
                username=params["DB_USER"],
                password=params["DB_PASS"],
                host=params["DB_HOST"],
                port=params["DB_PORT"],
                database=params["DB_NAME"],
            ),
        # [START cloud_sql_postgres_sqlalchemy_limit]
        # Pool size is the maximum number of permanent connections to keep.
        pool_size=params['POOL_SIZE'],
        # Temporarily exceeds the set pool_size if no connections are available.
        max_overflow=params['MAX_OVERFLOW'],
        # The total number of concurrent connections for your application will be
        # a total of pool_size and max_overflow.
        # [END cloud_sql_postgres_sqlalchemy_limit]
        # [START cloud_sql_postgres_sqlalchemy_backoff]
        # SQLAlchemy automatically uses delays between failed connection attempts,
        # but provides no arguments for configuration.
        # [END cloud_sql_postgres_sqlalchemy_backoff]
        # [START cloud_sql_postgres_sqlalchemy_timeout]
        # 'pool_timeout' is the maximum number of seconds to wait when retrieving a
        # new connection from the pool. After the specified amount of time, an
        # exception will be thrown.
        pool_timeout=params['POOL_TIMEOUT'],
        # [END cloud_sql_postgres_sqlalchemy_timeout]
        # [START cloud_sql_postgres_sqlalchemy_lifetime]
        # 'pool_recycle' is the maximum number of seconds a connection can persist.
        # Connections that live longer than the specified amount of time will be
        # re-established
        pool_recycle=params['POOL_RECYCLE'],
        # [END cloud_sql_postgres_sqlalchemy_lifetime]
        # [END_EXCLUDE]
        )

        return pool
    except Exception as error:
        print(f"error connecting to db {str(error)}")
        return(None)





app = APIFlask(__name__, title='HelloWorld API', version='1.0.0')

# openapi.info.description
app.config['DESCRIPTION'] = """
The description for this API. It can be very long and **Markdown** is supported.
"""

app.config['SERVERS'] = [
    {'name': 'Development Server', 'url': 'http://localhost:5000'}
]

conn=connect()


@app.get("/")
@app.doc(summary='Sample app that connects to postgres DB', responses={"200" : "Successful", "500" : "error connecting to Database"})
def hello_world():
    """ 
    Homepage route please note you will have to give the service account access to the tables
    using the Grant statement in postgresql as it only has access to public Schema. 
    """  
    if conn is not None:
        try:
            with conn.connect() as db_conn:
                result = db_conn.execute(text("select * from pg_catalog.pg_tables;")).fetchall()
                db_conn.close()
                print(f'Connected. result ={str(result)}')
                print("\n")
            
                conn.dispose()
            return jsonify({'status': 'healthy'}), 200
        except Exception as e:
            print(str(e))
            return jsonify({'status': 'error connecting to the database, please check logs'}), 500
    else:
        return "There is an issue connecting to the database, please check logs",500

@app.get("/healthcheck")
@app.doc(summary='Basic healthcheck that tests connectivity', responses={"200" : "Successful", "500" : "error connecting to database"})
def healthcheck():
    """ This should check if your application is healthy, but should be lightweight """
    if conn is not None:
        try:
            with conn.connect() as db_conn:
                result = db_conn.execute(text("select 1 from pg_catalog.pg_tables;")).fetchone()
                db_conn.close()
                print(f'Connected. result ={str(result)}')
                print("\n")
                
                conn.dispose()
                return jsonify({'status': 'healthy'}), 200
        except Exception as e:
            print(str(e))
            return jsonify({'status': 'error connecting to the database, please check logs'}), 500
    else:
        return "There is an issue connecting to the database, please check logs",500


if __name__ == "__main__":
    PORT = int(os.getenv("PORT")) if os.getenv("PORT") else 8080
    app.run(debug=False, host="127.0.0.1", port=PORT)
