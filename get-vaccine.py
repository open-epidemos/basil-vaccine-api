# -*- coding: utf-8 -*-

import sys
from datetime import datetime, timedelta
from elasticsearch import Elasticsearch
from pymongo import MongoClient

# Get args from the command line
args = sys.argv

try:
    end_user_date = args[1]
    end_user_time = args[2]

    end_date = "{0}T{1}.000Z".format(end_user_date, end_user_time)
except:
    # Get current date
    current_date = datetime.now()
    end_date = current_date.isoformat()

# We connect to our local mongodb server
mongo_client: MongoClient = MongoClient('127.0.0.1', 27017)
mongo_db = mongo_client.api_brasil
vaccine_collection = mongo_db.vaccine
api_log = mongo_db.api_log

# We connect to the elasticsearch server
elasticsearch_client = Elasticsearch(
    ['https://imunizacao-es.saude.gov.br:443'],
    basic_auth=('imunizacao_public', 'api_password'),
    request_timeout=120,
    max_retries=20,
    retry_on_timeout=True
)

# We check if there is a log in the database
exists_log: int = api_log.count_documents({})

if exists_log:
    exists_log = api_log.find()
    iso8601_date = datetime.strptime(exists_log[0]['timestamp'], "%Y-%m-%dT%H:%M:%S.%fZ")
    start_date = (iso8601_date + timedelta(milliseconds=500)).isoformat()

    # We create the body of the query where we will filter range dates where @timestamp field in elasticsearch is between start_date and end_date
    body = {
        "bool": {
            "filter": {
                "range" : {
                    "@timestamp" : {
                        "gte": "{0}".format(start_date),
                        "lte": "{0}".format(end_date)
                    }
                }
            }
        }
    }
        
else:
    body = {"match_all": {}}

api_fields_name = [
    '_id',
    'vacina_nome',
    'paciente_id',
    'paciente_idade',
    'vacina_descricao_dose',
    'data_importacao_datalake',
    'paciente_dataNascimento',
    'vacina_fabricante_nome',
    'vacina_codigo',
    'paciente_enumSexoBiologico',
    'vacina_dataAplicacao',
    '@timestamp'
]

# We execute the query in elasticsearch
data = elasticsearch_client.search(query=body, scroll='600m', size=10000, source_includes=api_fields_name, sort='@timestamp:asc')

# We get the scroll_id and the size of the data
scroll_id = data['_scroll_id']
scroll_size = len(data['hits']['hits'])

# We iterate over the data and insert it into the mongodb database
while scroll_size > 0:
    hits = data['hits']['hits']
    for item in hits:
        api_id = item['_id']
        item['_source']['api_id'] = api_id
    
    vaccine_collection.insert_many([item['_source'] for item in hits])

    try:
        api_log.delete_many({})
    except:
        pass
    
    api_log.insert_one({
        'timestamp': hits[-1]['_source']['@timestamp'],
        'api_id': hits[-1]['_source']['api_id']
        })

    data = elasticsearch_client.scroll(scroll_id=scroll_id, scroll='600m')
    scroll_id = data['_scroll_id']
    scroll_size = len(data['hits']['hits'])
    
    print('Vacunas almacenadas: {0:,}'.format(vaccine_collection.count_documents({})), end='\r')

    # Check if hits[-1]['_source']['@timestamp'] is equal or mayor to end_date, if it is, we stop the loop
    if hits[-1]['_source']['@timestamp'] >= end_date:
        print('La última fecha de vacuna almacenada es: {0}'.format(end_date))
        break
    
elasticsearch_client.clear_scroll(scroll_id=scroll_id)
