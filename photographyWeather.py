#!/usr/bin/python
# -*- coding:utf-8 -*-

import re
import requests
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


def get_daylight_dict(daytime_str: str) -> dict:
    sunrise = re.findall(r"(?<=<strong>Sunrise:</strong>\s).+?(?=\s&nbsp;)", daytime_str)[0]
    sunrise = [int(hhmm) for hhmm in sunrise.split(":")]
    sunset = re.findall(r"(?<=<strong>Sunset:</strong>\s).+?(?=\s<br\s/>\s<strong>Sun\sTransit:)", daytime_str)[0]
    sunset = [int(hhmm) for hhmm in sunset.split(":")]
    daylight_d = {"sunrise": {"hours": sunrise[0], "minutes": sunrise[1], "timestamp": 0},  # TODO: get timestamp using funct above
                  "sunset": {"hours": sunset[0], "minutes": sunset[1], "timestamp": 0},  # TODO: continue extracting data
                  "meridian transit": {"hours": 0, "minutes": 0, "timestamp": 0},
                  "civil dark": {"start": {"hours": 0, "minutes": 0, "timestamp": 0},
                                 "end": {"hours": 0, "minutes": 0, "timestamp": 0}},
                  "nautical dark": {"start": {"hours": 0, "minutes": 0, "timestamp": 0},
                                    "end": {"hours": 0, "minutes": 0, "timestamp": 0}},
                  "astro dark": {"start": {"hours": 0, "minutes": 0, "timestamp": 0},
                                 "end": {"hours": 0, "minutes": 0, "timestamp": 0}},
                  "morning golden hour": {"start": {"hours": 0, "minutes": 0, "timestamp": 0},
                                          "end": {"hours": 0, "minutes": 0, "timestamp": 0}},
                  "morning blue hour": {"start": {"hours": 0, "minutes": 0, "timestamp": 0},
                                        "end": {"hours": 0, "minutes": 0, "timestamp": 0}},
                  "evening golden hour": {"start": {"hours": 0, "minutes": 0, "timestamp": 0},
                                          "end": {"hours": 0, "minutes": 0, "timestamp": 0}},
                  "evening blue hour": {"start": {"hours": 0, "minutes": 0, "timestamp": 0},
                                        "end": {"hours": 0, "minutes": 0, "timestamp": 0}}}
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
        # TODO: get day, month, year
        # TODO: get lunar phase, lunar rise, lunar set, lunar meridian
        # get the first row: hours, general visibility and sun intensity
        hour_row_and_daylight_row = clearout_soup.find(class_="fc_hours fc_hour_ratings")
        hours_and_visibility = [cell.text.split(" ") for cell in hour_row_and_daylight_row.find_all("li")]
        hours = [cc[1] for cc in hours_and_visibility]
        gral_visib = [cc[2] for cc in hours_and_visibility]
        daylight_s = hour_row_and_daylight_row.find(class_="fc_daylight")
        daylight_d = get_daylight_dict(daylight_s)
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
