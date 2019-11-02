from flask import Flask
import requests
import urllib.parse
import time
from datetime import datetime

app = Flask(__name__)

api_links = {
    'station': 'https://marudor.de/api/hafas/v1/station/{}',
    'train': 'https://marudor.de/api/hafas/v1/trainSearch/{}?date={}',
    'utilization': 'https://marudor.de/api/reihung/v1/auslastung/{}/{}/{}/{}'
}


def get_station(stations, station_id):
    for station in stations:
        if station['station']['id'] == station_id:
            if 'arrival' not in station or 'departure' not in station:
                return None, None
            return station['arrival']['time'], station['departure']['time']
    return None, None


@app.route("/seats/<train_name>/<date>/<station_name>")
def seats(train_name, date, station_name):
    answer = {
        'success': False
    }

    # URL encode
    train_name = urllib.parse.quote(train_name)
    station_name = urllib.parse.quote(station_name)

    # get station id
    stations_result = requests.get(api_links['station'].format(station_name)).json()
    if len(stations_result) == 0:
        answer['error'] = 'Bahnhof nicht gefunden'
        return answer, 400
    station_info = stations_result[0]  # use first found station, TODO: show user the possible stations?
    station_id = station_info['id'][2:]  # remove 2 leading zeros from id
    answer['stationId'] = station_id

    # get train stations -> arrival and departure time at wanted station
    date_now = int(round(time.time() * 1000))
    train_info = requests.get(api_links['train'].format(train_name, date_now)).json()
    if 'jDetails' not in train_info or 'stops' not in train_info['jDetails']:
        answer['error'] = 'Zug nicht gefunden'
        return answer, 400

    train_stations = train_info['jDetails']['stops']
    station_arrival, station_departure = get_station(train_stations, station_id)
    if not station_departure:
        answer['error'] = 'Ankunfts- und Abfahrtszeiten für Zug am Bahnhof nicht gefunden'
        return answer, 500

    # convert request times to UTC time and ISO format
    station_arrival_iso = datetime.fromtimestamp(station_arrival // 1000).isoformat() + 'Z'
    answer['stationArrival'] = station_arrival_iso
    station_departure_iso = datetime.fromtimestamp(station_departure // 1000).isoformat() + 'Z'
    answer['stationDeparture'] = station_departure_iso

    # remove 5 minutes from departure time (-> start time) and add 6 hours to departure time (-> end time)
    start_time_millis = station_departure - 5 * 60 * 1000
    start_time_iso = datetime.utcfromtimestamp(start_time_millis // 1000).isoformat() + 'Z'
    end_time_millis = station_departure + 6 * 60 * 60 * 1000
    end_time_iso = datetime.utcfromtimestamp(end_time_millis // 1000).isoformat() + 'Z'

    # get utilization of train at station
    utilization_info = requests.get(api_links['utilization'].format(train_name, station_id, start_time_iso, end_time_iso)).json()
    answer['utilization'] = utilization_info  # TODO: change

    answer['success'] = True
    return answer


if __name__ == "__main__":
    app.run(host='0.0.0.0')
