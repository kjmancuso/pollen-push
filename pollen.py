import requests

from datetime import datetime

from influxdb import InfluxDBClient

IFLX_HOST = 'localhost'
IFLX_DB = 'pollen'

def get_data(scope='Today'):
    headers = {'Accept': 'application/json'}
    url = 'http://saallergy.info/'
    if scope == 'Today':
        url = url + 'today'
    if scope == 'All':
        url = url + '?more=true'
    r = requests.get(url, headers=headers)

    return r.json()

def send_to_influx(metrics, host=IFLX_HOST, db=IFLX_DB):
    client = InfluxDBClient(host=host, database=db)
    client.write_points(metrics)

if __name__ == '__main__':
    m = []
    data = get_data()
    results = data['results']
    for i in results:
        date = i['date']
        allergen = i['allergen']
        count = i['count']
        # Scott adds unit delimiters in large numbers
        if type(count) != int:
            count = int(count.replace(',', ''))
        ts = datetime.strptime(date, '%Y-%m-%d').isoformat('T')
        metric = {'measurement': 'allergen',
                  'time': ts,
                  'tags': {'allergen': allergen},
                  'fields': {'value': count}}
        m.append(metric)
    send_to_influx(m)
