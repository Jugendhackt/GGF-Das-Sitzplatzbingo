from flask import Flask
import requests
import urllib.parse
from datetime import datetime

app = Flask(__name__)

api_links = {
    'station': 'https://marudor.de/api/hafas/v1/station/{}',
    'train': 'https://marudor.de/api/hafas/v1/trainSearch/{}?date={}',
    'utilization': 'https://marudor.de/api/reihung/v1/auslastung/{}/{}/{}/{}',
    'sequence': 'https://marudor.de/api/reihung/v1/wagen/{}/{}'
}


def get_station(stations, station_id):
    for station in stations:
        if station['station']['id'] == station_id:
            if 'arrival' not in station or 'departure' not in station:
                return None, None
            return station['arrival']['time'], station['departure']['time']
    return None, None


def millis_to_iso_string(date_millis, to_utc):
    if to_utc:
        return datetime.utcfromtimestamp(date_millis // 1000).isoformat() + 'Z'
    else:
        return datetime.fromtimestamp(date_millis // 1000).isoformat() + 'Z'


def get_sequence_data(sequence_info, wagon_id):
    for wagon_group in sequence_info['allFahrzeuggruppe']:
        for wagon in wagon_group['allFahrzeug']:
            if wagon['fahrzeugnummer'] == wagon_id:
                return wagon
    return None


@app.route("/seats/<train_name>/<date_string>/<station_name>")
def seats(train_name, date_string, station_name):
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

    # parse string date to millis format
    try:
        date = datetime.strptime(date_string, "%Y-%m-%d")
    except ValueError:
        answer['error'] = 'Ungültiges Datum (Format: YYYY-MM-DD)'
        return answer, 400
    date_millis = int(date.timestamp() * 1000)

    # get train stations -> arrival and departure time at wanted station
    train_info = requests.get(api_links['train'].format(train_name, date_millis)).json()
    if 'jDetails' not in train_info or 'stops' not in train_info['jDetails']:
        answer['error'] = 'Zug nicht gefunden'
        return answer, 400

    train_stations = train_info['jDetails']['stops']
    station_arrival_millis, station_departure_millis = get_station(train_stations, station_id)
    if not station_departure_millis:
        answer['error'] = 'Zug hält nicht am angegebenen Bahnhof (oder ist Endhalt)'
        return answer, 400

    # convert request times to ISO format and return them
    answer['stationArrival'] = millis_to_iso_string(station_arrival_millis, False)
    answer['stationDeparture'] = millis_to_iso_string(station_departure_millis, False)

    # convert dates to UTC time and
    # remove 5 minutes from departure time (-> start time) and add 6 hours to departure time (-> end time)
    start_time_millis = station_departure_millis - 5 * 60 * 1000
    start_time_iso = millis_to_iso_string(start_time_millis, True)
    end_time_millis = station_departure_millis + 6 * 60 * 60 * 1000
    end_time_iso = millis_to_iso_string(end_time_millis, True)

    # get utilization of train at station
    utilization_info = requests.get(
        api_links['utilization'].format(train_name, station_id, start_time_iso, end_time_iso)).json()
    if 'auslastung' not in utilization_info:
        answer['error'] = 'Für den angegebenen Zug und Halt sind keine Auslastungsdaten verfügbar'
        return answer, 400

    # get sequence info of train at station departure time
    train_number = ''.join([c for c in train_name if c.isdigit()])
    sequence_info = requests.get(api_links['sequence'].format(train_number, station_departure_millis)).json()
    if 'allFahrzeuggruppe' not in sequence_info:
        answer['error'] = 'Für den angegebenen Zug sind keine Wagondaten verfügbar'
        return answer, 400

    # map data from utilization and sequence info to json object
    utilization = []
    for wagon_id, wagon_data in utilization_info['auslastung'].items():
        sequence_data = get_sequence_data(sequence_info, wagon_id)
        if not sequence_data:
            answer['error'] = 'Wagon-Informationen nicht gefunden'
            return answer, 500

        # don't use data of end and dining wagons
        if sequence_data['kategorie'] in ['TRIEBKOPF', 'SPEISEWAGEN']:
            continue

        utilization.append({
            'wagonPosition': sequence_data['positioningruppe'],
            'wagonNumber': sequence_data['wagenordnungsnummer'],
            'wagonType': sequence_data['fahrzeugtyp'],
            'capacitySeatsFirst': wagon_data['capacitySeatsFirst'],
            'capacitySeatsSecond': wagon_data['capacitySeatsSecond'],
            'seatReservationsFirst': wagon_data['seatReservationsFirst'] if wagon_data['seatReservationsFirst'] else 0,
            'seatReservationsSecond': wagon_data['seatReservationsSecond'] if wagon_data[
                'seatReservationsSecond'] else 0,
            'reservedSeats': wagon_data['occupiedSeats']
        })
    answer['utilization'] = utilization

    answer['success'] = True
    return answer


if __name__ == "__main__":
    app.run(host='0.0.0.0')
