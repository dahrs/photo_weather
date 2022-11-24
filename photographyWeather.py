#!/usr/bin/python
# -*- coding:utf-8 -*-

import re
import requests
from datetime import date
from datetime import datetime
from bs4 import BeautifulSoup
from geopy.geocoders import Nominatim


def get_lat_and_long(city: str, country: str = None) -> tuple[float, float]:
    """
    Tutorial from
    https://medium.com/analytics-vidhya/how-to-generate-lat-and-long-coordinates-of-city-without-using-apis-25ebabcaf1d5
    :param city: city name
    :param country: country name
    :return: tuple with latitude and longitude
    """
    # only the name of the city is given
    if not country:
        query = city
    # the name of the city and country are given
    else:
        query = f"{city},{country}"
    # geolocation
    geolocator = Nominatim(user_agent="photography_weather")
    location = geolocator.geocode(query)
    address = location.address
    return location.latitude, location.longitude


def reformat_lant_long(latitude: float, longitude: float) -> str:
    """
    Reformat the way latitude and longitude, so it matches the clearoutside site search url
    :param latitude: float of latitude
    :param longitude: float of longitude
    :return: string of latitude and longitude separated by a '/'
    """
    lat_str = "{0:.2f}".format(latitude)
    long_str = "{0:.2f}".format(longitude)
    return f"{lat_str}/{long_str}"


def datetime_to_seconds_timestamp(year: int = 2022, month: int = 11, day: int = 22,
                                  hour: int = 0, minute: int = 0, second: int = 0) -> float:
    dt = datetime(year, month, day, hour, minute, second)
    return dt.timestamp()


def get_nightlight_dict(nighttime_str: str, clearout_soup: BeautifulSoup) -> dict:
    moon_altitude = re.findall(r"(?<=<strong>Altitude:</strong> ).+?(?= <br /> <strong>Distance:)", nighttime_str)[0]
    moon_dist_miles = re.findall(r"(?<=<strong>Distance:</strong> ).+?(?= miles <br />)", nighttime_str)[0]
    moon_dist_miles = int(moon_dist_miles.replace(",", ""))
    moon_dist_km = moon_dist_miles * 1.609344
    moon_phase = clearout_soup.find(class_="fc_moon_phase").text
    moon_percentage = clearout_soup.find(class_="fc_moon_percentage").text
    moon_percentage = int(moon_percentage.replace("%", ""))
    moonrise_s = clearout_soup.find(class_="fc_moon_riseset").text.split(" ")[1]
    moonrise = [int(hhmm) for hhmm in moonrise_s.split(":")]
    moonset_s = clearout_soup.find(class_="fc_moon_riseset").text.split(" ")[-1]
    moonset = [int(hhmm) for hhmm in moonset_s.split(":")]
    # get current date
    yy, mm, dd = date.today().year, date.today().month, date.today().day
    nightlight_d = {"moonrise": {"hours": moonrise[0], "minutes": moonrise[1], "time": moonrise_s,
                                 "timestamp": datetime_to_seconds_timestamp(yy, mm, dd, moonrise[0], moonrise[1])},
                    "moonset": {"hours": moonset[0], "minutes": moonset[1], "time": moonset_s,
                                "timestamp": datetime_to_seconds_timestamp(yy, mm, dd, moonset[0], moonset[1])},
                    "moon altitude": {"degrees": float(moon_altitude.replace("°", "")), "string": moon_altitude},
                    "moon distance": {"kilometers": moon_dist_km, "miles": moon_dist_miles},
                    "moon phase": {"phase name": moon_phase, "illumination percentage": moon_percentage}}
    return nightlight_d


def get_daylight_dict(daytime_str: str) -> dict:
    sunrise_s = re.findall(r"(?<=Sun - Rise: ).+?(?=, Set)", daytime_str)[0]
    sunrise = [int(hhmm) for hhmm in sunrise_s.split(":")]
    sunset_s = re.findall(r"(?<=, Set: ).+?(?=, Transit:)", daytime_str)[0]
    sunset = [int(hhmm) for hhmm in sunset_s.split(":")]
    sun_meridian_s = re.findall(r"(?<=, Transit: ).+?(?=\.\s\sMoon)", daytime_str)[0]
    sun_meridian = [int(hhmm) for hhmm in sun_meridian_s.split(":")]
    # moonrise_s = re.findall(r"(?<=Moon - Rise: ).+?(?=, Set)", daytime_str)[0]
    # moonrise = [int(hhmm) for hhmm in moonrise_s.split(":")]
    # moonset_s = re.findall(r"Moon - .+? Civil Dark:", daytime_str)[0]
    # moonset_s = re.findall(r"(?<=Set: ).+?(?=\. Civil Dark:)", moonset_s)[0]
    # moonset = [int(hhmm) for hhmm in moonset_s.split(":")]
    civil_dark_s = re.findall(r"(?<=Civil Dark: ).+?(?=\. Nautical Dark:)", daytime_str)[0]
    civil_dark = [[int(hhmm) for hhmm in star_end.split(":")] for star_end in civil_dark_s.split(" - ")]
    nautical_dark_s = re.findall(r"(?<=Nautical Dark: ).+?(?=\. Astro Dark:)", daytime_str)[0]
    nautical_dark = [[int(hhmm) for hhmm in star_end.split(":")] for star_end in nautical_dark_s.split(" - ")]
    astro_dark_s = re.findall(r"(?<=Astro Dark: ).+", daytime_str)[0]
    astro_dark = [[int(hhmm) for hhmm in star_end.split(":")] for star_end in astro_dark_s.split(" - ")]
    # get current date
    yy, mm, dd = date.today().year, date.today().month, date.today().day
    # populate dict
    daylight_d = {"sunrise": {"hours": sunrise[0], "minutes": sunrise[1], "time": sunrise_s,
                              "timestamp": datetime_to_seconds_timestamp(yy, mm, dd, sunrise[0], sunrise[1])},
                  "sunset": {"hours": sunset[0], "minutes": sunset[1], "time": sunset_s,
                             "timestamp": datetime_to_seconds_timestamp(yy, mm, dd, sunset[0], sunset[1])},
                  "meridian transit": {"hours": sun_meridian[0], "minutes": sun_meridian[1], "time": sun_meridian_s,
                                       "timestamp": datetime_to_seconds_timestamp(yy, mm, dd,
                                                                                  sun_meridian[0], sun_meridian[1])},
                  # "moonrise": {"hours": moonrise[0], "minutes": moonrise[1], "time": moonrise_s,
                  #              "timestamp": datetime_to_seconds_timestamp(yy, mm, dd, moonrise[0], moonrise[1])},
                  # "moonset": {"hours": moonset[0], "minutes": moonset[1], "time": moonset_s,
                  #             "timestamp": datetime_to_seconds_timestamp(yy, mm, dd, moonset[0], moonset[1])},
                  "civil dark": {"start": {"hours": civil_dark[0][0], "minutes": civil_dark[0][1],
                                           "time": civil_dark_s.split(" - ")[0],
                                           "timestamp": datetime_to_seconds_timestamp(yy, mm, dd, civil_dark[0][0],
                                                                                      civil_dark[0][1])},
                                 "end": {"hours": civil_dark[1][0], "minutes": civil_dark[1][1],
                                         "time": civil_dark_s.split(" - ")[1],
                                         "timestamp": datetime_to_seconds_timestamp(yy, mm, dd, civil_dark[1][0],
                                                                                    civil_dark[1][1])}},
                  "nautical dark": {"start": {"hours": nautical_dark[0][0], "minutes": nautical_dark[0][1],
                                              "time": nautical_dark_s.split(" - ")[0],
                                              "timestamp": datetime_to_seconds_timestamp(yy, mm, dd, nautical_dark[0][0],
                                                                                         nautical_dark[0][1])},
                                    "end": {"hours": nautical_dark[1][0], "minutes": nautical_dark[1][1],
                                            "time": nautical_dark_s.split(" - ")[1],
                                            "timestamp": datetime_to_seconds_timestamp(yy, mm, dd, nautical_dark[1][0],
                                                                                       nautical_dark[1][1])}},
                  "astro dark": {"start": {"hours": astro_dark[0][0], "minutes": astro_dark[0][1],
                                           "time": astro_dark_s.split(" - ")[0],
                                           "timestamp": datetime_to_seconds_timestamp(yy, mm, dd, astro_dark[0][0],
                                                                                      astro_dark[0][1])},
                                 "end": {"hours": astro_dark[1][0], "minutes": astro_dark[1][0],
                                         "time": astro_dark_s.split(" - ")[1],
                                         "timestamp": datetime_to_seconds_timestamp(yy, mm, dd, astro_dark[1][0],
                                                                                    astro_dark[1][1])}},
                  "morning golden hour": {"start": {"hours": civil_dark[1][0], "minutes": civil_dark[1][1],
                                                    "time": civil_dark_s.split(" - ")[1],
                                                    "timestamp": datetime_to_seconds_timestamp(yy, mm, dd,
                                                                                               civil_dark[1][0],
                                                                                               civil_dark[1][1])},
                                          "end": {"hours": sunrise[0], "minutes": sunrise[1],
                                                  "time": sunrise_s,
                                                  "timestamp": datetime_to_seconds_timestamp(yy, mm, dd,
                                                                                             sunrise[0], sunrise[1])}},
                  "morning blue hour": {"start": {"hours": nautical_dark[1][0], "minutes": nautical_dark[1][1],
                                                  "time": nautical_dark_s.split(" - ")[1],
                                                  "timestamp": datetime_to_seconds_timestamp(yy, mm, dd,
                                                                                             nautical_dark[1][0],
                                                                                             nautical_dark[1][1])},
                                        "end": {"hours": civil_dark[1][0], "minutes": civil_dark[1][1],
                                                "time": civil_dark_s.split(" - ")[1],
                                                "timestamp": datetime_to_seconds_timestamp(yy, mm, dd, civil_dark[1][0],
                                                                                           civil_dark[1][1])}},
                  "evening golden hour": {"start": {"hours": sunset[0], "minutes": sunset[1],
                                                    "time": sunset_s,
                                                    "timestamp": datetime_to_seconds_timestamp(yy, mm, dd, sunset[0],
                                                                                               sunset[1])},
                                          "end": {"hours": civil_dark[0][0], "minutes": civil_dark[0][0],
                                                  "time": civil_dark_s.split(" - ")[0],
                                                  "timestamp": datetime_to_seconds_timestamp(yy, mm, dd,
                                                                                             civil_dark[0][0],
                                                                                             civil_dark[0][1])}},
                  "evening blue hour": {"start": {"hours": civil_dark[0][0], "minutes": civil_dark[0][1],
                                                  "time": civil_dark_s.split(" - ")[0],
                                                  "timestamp": datetime_to_seconds_timestamp(yy, mm, dd,
                                                                                             civil_dark[0][0],
                                                                                             civil_dark[0][1])},
                                        "end": {"hours": nautical_dark[0][0], "minutes": nautical_dark[0][1],
                                                "time": nautical_dark_s.split(" - ")[0],
                                                "timestamp": datetime_to_seconds_timestamp(yy, mm, dd,
                                                                                           nautical_dark[0][0],
                                                                                           nautical_dark[0][1])}}}
    return daylight_d


def get_clearoutside_weather_forecast(latitude: float, longitude: float) -> dict:
    """
    Gets the clear outside site weather predictions
    :param latitude: latitude float
    :param longitude: longitude float
    :return: dictionary with the forecast data
    """
    fore_data = {}
    url = f"https://clearoutside.com/forecast/{reformat_lant_long(latitude, longitude)}?experimental=on"
    clear_outside = requests.get(url)
    w_status = clear_outside.status_code
    if w_status == 200:
        w_json = clear_outside.json
        w_content = clear_outside.text
        clearout_soup = BeautifulSoup(w_content, "html.parser")
        # get general data
        moon_data = clearout_soup.find(class_="fc_moon").get("data-content")
        nightlight_d = get_nightlight_dict(moon_data, clearout_soup)
        # get the first row: hours, general visibility and sun intensity
        hour_row_and_daylight_row = clearout_soup.find(class_="fc_hours fc_hour_ratings")
        hours_and_visibility = [cell.text.split(" ") for cell in hour_row_and_daylight_row.find_all("li")]
        hours = [cc[1] for cc in hours_and_visibility]
        gral_visib = [cc[2] for cc in hours_and_visibility]
        daylight_s = hour_row_and_daylight_row.find(class_="fc_daylight")
        daylight_d = get_daylight_dict(daylight_s.text)
        print(1111111, daylight_d)
        # TODO: get rest of row data, all rows should be of the same size as hours

        ##### https://www.crummy.com/software/BeautifulSoup/bs4/doc/
        #####################################################################
        # TODO: extract all data from the page
    return fore_data


def photo_conditions() -> dict:
    photo_cond = {
        "day": {},  # TODO: fog and low clouds to photograph buildings of 100+ meters; post-rain
        "night": {},  # TODO: clear visibility for astro photo, ISS passing and clear visibility
        "golden_hour": {},  # TODO: high clouds only during sunset/sunrise
        "blue_hour": {}
    }
    return photo_cond


def make_photo_weather_based_suggestions(location: str) -> None:
    """
    Get a message with the weather photography recommendations
    :param location: location where to photograph
    :return: None
    """
    location_list = re.split(r",\s?", location)
    if len(location_list) == 2:
        lat_long = get_lat_and_long(location_list[0], location_list[1])
    else:
        lat_long = get_lat_and_long(location_list[0])
    # get predictions from clear outside
    pred_dict = get_clearoutside_weather_forecast(lat_long[0], lat_long[1]) ############
    #########################################################################
    # TODO: use telegram or email to send message of recommendations
    return


if __name__ == "__main__":
    print(make_photo_weather_based_suggestions("Montreal, Quebec"))
