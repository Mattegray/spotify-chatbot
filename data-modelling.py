import sys
import os
import logging
import pymysql
import boto3
import time
import math


'''
Fetch data from AWS Athena
    Artist avg metrics
    metrics: max & min
    normalization
    euclidean distance
Import data to mysql
'''

host = "fastcampus.crqhm4yzezxw.us-east-2.rds.amazonaws.com"
port = 3306
username = "matt"
database = "production"
password = "matt1234"


def main():
    try:
        conn = pymysql.connect(host, user=username, passwd=password, db=database, use_unicode=True, charset='utf8')
        cursor = conn.cursor()
    except:
        logging.error("Could not connect to RDS")
        sys.exit(1)

    athena = boto3.client('athena')

    query = """
        SELECT
         artist_id,
         AVG(danceability) AS danceability,
         AVG(energy) AS energy,
         AVG(loudness) AS loudness,
         AVG(speechiness) AS speechiness,
         AVG(acousticness) AS acousticness,
         AVG(instrumentalness) AS instrumentalness
        FROM
         top_tracks t1
        JOIN
         audio_features t2 ON t2.id = t1.id AND CAST(t1.dt AS DATE) = DATE('2019-11-18') AND CAST(t2.dt AS DATE) = DATE('2019-11-18')
        GROUP BY t1.artist_id
        LIMIT 20
    """

    r = query_athena(query, athena)
    results = get_query_result(r['QueryExecutionId'], athena)
    artists = process_data(results)

    query = """
        SELECT
         MIN(danceability) AS danceability_min,
         MAX(danceability) AS danceability_max,
         MIN(energy) AS energy_min,
         MAX(energy) AS energy_max,
         MIN(loudness) AS loudness_min,
         MAX(loudness) AS loudness_max,
         MIN(speechiness) AS speechiness_min,
         MAX(speechiness) AS speechiness_max,
         ROUND(MIN(acousticness),4) AS acousticness_min,
         MAX(acousticness) AS acousticness_max,
         MIN(instrumentalness) AS instrumentalness_min,
         MAX(instrumentalness) AS instrumentalness_max
        FROM
         audio_features
    """

    r = query_athena(query, athena)
    results = get_query_result(r['QueryExecutionId'], athena)
    artists = process_data(results)[0]


def query_athena(query, athena):
    response = athena.start_query_execution(
        QueryString=query,
        QueryExecutionContext={
            'Database': 'production'
        },
        ResultConfiguration={
            'OutputLocation': "s3://athena-panomix-tables/repair/",
            'EncryptionConfiguration': {
                'EncryptionOption': 'SSE_S3'
            }
        }
    )

    return response


def get_query_result(query_id, athena):

    response = athena.get_query_execution(
        QueryExecutionId=str(query_id)
    )

    while response['QueryExecution']['Status']['State'] != 'SUCCEEDED':
        if response['QueryExecution']['Status']['State'] == 'FAILED':
            logging.error('QUERY FAILED')
            break
        time.sleep(5)
        response = athena.get_query_execution(
            QueryExecutionId=str(query_id)
        )

    response = athena.get_query_results(
        QueryExecutionId=str(query_id),
        MaxResults=1000
    )

    return response


def process_data(results):

    columns = [col['Label'] for col in results['ResultSet']['ResultSetMetadata']['ColumnInfo']]

    listed_results = []
    for res in results['ResultSet']['Rows'][1:]:
        values = []
        for field in res['Data']:
            try:
                values.append(list(field.values())[0])
            except:
                values.append(list(' '))
        listed_results.append(dict(zip(columns, values)))

    return listed_results


def insert_row(cursor, data, table):
    placeholders = ', '.join(['%s'] * len(data))
    columns = ', '.join(data.keys())
    key_placeholders = ', '.join(['{0}=%s'.format(k) for k in data.keys()])
    sql = "INSERT INTO %s (%s) VALUES (%s) ON DUPLICATE KEY UPDATE %s" % (table, columns, placeholders, key_placeholders)
    cursor.execute(sql, list(data.values())*2)


if __name__ == '__main__':
    main()
