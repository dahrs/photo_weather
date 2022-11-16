#!/usr/bin/python
# -*- coding:utf-8 -*-

import re
import requests
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
        ##### https://www.crummy.com/software/BeautifulSoup/bs4/doc/
        #####################################################################
        # TODO: extract all data from the page
    return fore_data


def photo_conditions() -> dict:
    photo_cond = {
        "day": {},  # TODO: fog and low clouds to photograph buildings of 100+ meters
        "night": {},  # TODO: clear visibility for astro photo
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
