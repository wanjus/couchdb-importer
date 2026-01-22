import pyelasticsearch as pyes
import csv

URL_ES = 'http://localhost:9200/'
CSV_FILE = 'MOCK_DATA.csv'
INDEX = 'mock'
TYPE = '_doc'
ID_FIELD = 'id'

f = open(CSV_FILE)
rows = csv.DictReader(f)
print('Connecting to elastic...', end="")
es = pyes.ElasticSearch(URL_ES)
print('Done!')

actions = []
for row in rows:
    actions.append(row)

    while len(actions) > 10000 and len(actions) % 10000 == 0:
        print('Inserting bulk data...', end="")
        es.bulk_index(INDEX, TYPE, actions, id_field=ID_FIELD)
        print('done!')
        del actions[0:len(actions)]
        break

if len(actions) > 0:
    print('Inserting bulk data...', end="")
    es.bulk_index(INDEX, TYPE, actions, id_field=ID_FIELD)
    print('done!')
    del actions[0:len(actions)]

print('Finished.')