import xml.etree.ElementTree as ET
import datetime
import requests
import geopy
from geopy.distance import geodesic
import gpxpy
import gpxpy.gpx

poi_enum = {'P1S':[360.0,5.0],'P2S': [120.0,5.0],'P3S': [240.0,5.0],'P1E': [360.0,30.0],'P2E': [120.0,30.0],'P3E': [240.0,30.0]}

def get_declination(lat, lon):
    # Get current month
    month = datetime.datetime.now().month
    # Generate parameter strings
    payload = {'lat1': lat, 'lon1': lon, 'resultFormat': 'xml', 'startMonth': month}
    # Retrieve XML results from NOAA
    result = requests.get('http://www.ngdc.noaa.gov/geomag-web/calculators/calculateDeclination', params=payload)
    # Process XML result and retrieve declination info.
    root = ET.fromstring(result.content)
    return float(root[1][4].text.strip('\n'))

def point_from_center(lat, lon, kilometers, bearing):
    origin = geopy.Point(lat, lon)
    destination = geodesic(kilometers=kilometers).destination(origin, bearing)

    return [destination.latitude, destination.longitude]

def poi_loop(lat, lon):

    # Get Magnetic declination
    declination = get_declination(lat, lon)

    # Loop over each POI and calc distance and declination ajustment.
    results = {}
    for name, point in poi_enum.items():
        kilometers = (point[1]/1000.0)
        adjusted_bearing = point[0] + declination
        # Add POI lat,long to the results table
        results[name]=point_from_center(lat, lon, kilometers, adjusted_bearing)

    return results

def main():
    # Get Center via user input
    center = input("Center Point [lat, long]:")
    gpx_output = True if 'y' in input("GPX output? [y/n]").lower() else False

    lat, lon = center.replace(' ','').split(',')
    results = poi_loop(lat, lon)

    if gpx_output:

        gpx_header = """<?xml version="1.0" encoding="UTF-8"?>\n<gpx xmlns="http://www.topografix.com/GPX/1/1" version="1.1" creator="EasyGPS 5.79 using Garmin eTrex 20" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd http://www.topografix.com/GPX/gpx_overlay/0/3 http://www.topografix.com/GPX/gpx_overlay/0/3/gpx_overlay.xsd http://www.topografix.com/GPX/gpx_modified/0/1 http://www.topografix.com/GPX/gpx_modified/0/1/gpx_modified.xsd">\n"""

        # Write file
        with open('result.gpx', 'w') as gpxout:
            gpxout.write(gpx_header)
            for poi, latlon in results.items():
                gpxout.write(f"<wpt lat='{latlon[0]}' lon='{latlon[1]}'>\n<name>'{poi}'</name>\n</wpt>\n")
            gpxout.write("</gpx>")

    else:

        #Pretty Print
        print("\n")
        for poi, latlon in results.items():
            print(f"{poi}, {latlon[0]}, {latlon[1]}")


if __name__ == "__main__":
    # execute only if run as a script
    main()