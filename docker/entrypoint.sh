#!/bin/sh

# Wait for MySQL to be ready using Python
echo "Waiting for MySQL to be ready..."
python -c "
import time
import pymysql
import os

db_host = os.environ.get('DB_HOST', 'mysql_db')
db_port = int(os.environ.get('DB_PORT', 3306))

for i in range(30):
    try:
        conn = pymysql.connect(
            host=db_host,
            user=os.environ.get('DB_USER'),
            password=os.environ.get('DB_PASSWORD'),
            port=db_port
        )
        conn.close()
        print(f'MySQL at {db_host}:{db_port} is ready!')
        break
    except Exception as e:
        print(f'Waiting for MySQL at {db_host}:{db_port}... ({i+1}/30)')
        time.sleep(2)
"

flask db upgrade

#python -m app.utils.load_defaults

gunicorn -b 0.0.0.0:5000 --timeout 120 --workers 5 --threads 2 run:app