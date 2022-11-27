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
    for time_unit in [year, month, day, hour, minute, second]:
        if type(time_unit) not in [int, float]:
            return None
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
    if moonset_s == "Set":
        moonset = [None, None]
    else:
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
    # if moonset_s == "No Set":
    #     moonset = [None, None]
    # else:
    #     moonset = [int(hhmm) for hhmm in moonset_s.split(":")]
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


def get_clearoutside_weather_forecast(latitude: float, longitude: float) -> tuple[dict, dict, dict]:
    """
    Gets the clear outside site weather predictions
    :param latitude: latitude float
    :param longitude: longitude float
    :return: dictionary with the forecast data
    """
    forecast_hour_d = {}
    url = f"https://clearoutside.com/forecast/{reformat_lant_long(latitude, longitude)}?experimental=on"
    clear_outside = requests.get(url)
    w_status = clear_outside.status_code
    if w_status == 200:
        w_json = clear_outside.json
        w_content = clear_outside.text
        clearout_soup = BeautifulSoup(w_content, "html.parser")
        # get general night data
        moon_data = clearout_soup.find(class_="fc_moon").get("data-content")
        nightlight_d = get_nightlight_dict(moon_data, clearout_soup)
        # get the first row: hours, general visibility and sun intensity
        hour_row_and_daylight_row = clearout_soup.find(class_="fc_hours fc_hour_ratings")
        # get general day data
        daylight_s = hour_row_and_daylight_row.find(class_="fc_daylight")
        daylight_d = get_daylight_dict(daylight_s.text)
        # get row data
        hours_and_visibility = [cell.text.split(" ") for cell in hour_row_and_daylight_row.find_all("li")]
        hours = [cc[1] for cc in hours_and_visibility]
        gral_visib = [cc[2] for cc in hours_and_visibility]
        # get first day table
        current_day_table = clearout_soup.find(class_="fc_detail hidden-xs")
        # get each row data
        rows = current_day_table.find_all(class_="fc_detail_row")
        # get cloud data
        total_clouds = [int(cell.text) for cell in rows[0].find(class_="fc_hours").find_all("li")]
        low_clouds = [int(cell.text) for cell in rows[1].find(class_="fc_hours").find_all("li")]
        medium_clouds = [int(cell.text) for cell in rows[2].find(class_="fc_hours").find_all("li")]
        high_clouds = [int(cell.text) for cell in rows[3].find(class_="fc_hours").find_all("li")]
        # get experimental cloud data from 7timer! service
        seven_timer_cloud_cover = [int(cell.text) if re.findall(r"[0-9]", cell.text)
                                   else None for cell in rows[4].find(class_="fc_hours").find_all("li")]
        alternative_cloud_cover = [int(cell.text) if re.findall(r"[0-9]", cell.text)
                                   else None for cell in rows[5].find(class_="fc_hours").find_all("li")]
        seven_timer_seeing = [int(cell.text) if re.findall(r"[0-9]", cell.text)
                              else None for cell in rows[6].find(class_="fc_hours").find_all("li")]
        seven_timer_lifted_index = [int(cell.text) if re.findall(r"[0-9]", cell.text)
                                    else None for cell in rows[7].find(class_="fc_hours").find_all("li")]
        seven_timer_transparency = [int(cell.text) if re.findall(r"[0-9]", cell.text)
                                    else None for cell in rows[8].find(class_="fc_hours").find_all("li")]
        # get ISS passover time
        iss_passover = [False if "fc_none" in str(cell) else True
                        for cell in rows[9].find(class_="fc_hours").find_all("li")]
        # get humidity data
        visibility_mile = [float(cell.text) for cell in rows[10].find(class_="fc_hours").find_all("li")]
        visibility_km = [visib * 1.609344 for visib in visibility_mile]
        fog_percentage = [int(cell.text) for cell in rows[11].find(class_="fc_hours").find_all("li")]
        celsius_dew_point = [int(cell.text) for cell in rows[19].find(class_="fc_hours").find_all("li")]
        relative_humidity_percent = [int(cell.text) for cell in rows[20].find(class_="fc_hours").find_all("li")]
        # get precipitation type: 0 is none, 1 is drizzle, 2 is light rain, 3 is
        precipitation_type = [0 if "None" in str(cell) else str(cell) for cell in
                              rows[12].find(class_="fc_hours").find_all("li")]
        precipitation_type = [1 if (type(cell) is str and "Very Light Rain" in cell) else cell
                              for cell in precipitation_type]
        precipitation_type = [2 if (type(cell) is str and "Light Rain" in cell) else cell
                              for cell in precipitation_type]
        # TODO: complete precipitation types
        # get precipitation data
        precipitation_proba = [int(cell.text) for cell in rows[13].find(class_="fc_hours").find_all("li")]
        precipitation_amount_mm = [float(cell.text) for cell in rows[14].find(class_="fc_hours").find_all("li")]
        # get wind data (direction, miles per hour and km per hour)
        wind_direction = [re.findall(r'(?<=from the ).+?(?="><span>)', str(cell))
                          for cell in rows[15].find(class_="fc_hours").find_all("li")]
        wind_speed_mph = [int(cell.text) for cell in rows[15].find(class_="fc_hours").find_all("li")]
        wind_speed_kph = [int(mph * 1.609344) for mph in wind_speed_mph]
        # get frost
        frost = [True if "Chance of Frost" in str(cell) else False
                 for cell in rows[16].find(class_="fc_hours").find_all("li")]
        # get temperature data
        celsius_temp_real = [int(cell.text) for cell in rows[17].find(class_="fc_hours").find_all("li")]
        celsius_temp_feel = [int(cell.text) for cell in rows[18].find(class_="fc_hours").find_all("li")]
        # get other data
        pressure_mb = [int(cell.text) for cell in rows[21].find(class_="fc_hours").find_all("li")]
        ozone_du = [int(cell.text) for cell in rows[22].find(class_="fc_hours").find_all("li")]
        for hh, gv, lc, mc, hc, tc, ac, sc, ss, sl, st, iss, vm, vk, fp, dp, rh, pp, pa, pt, wd, wm, wk, ff, tr, \
            tf, pm, od in zip(hours, gral_visib, low_clouds, medium_clouds, high_clouds, total_clouds,
                              alternative_cloud_cover, seven_timer_cloud_cover, seven_timer_seeing,
                              seven_timer_lifted_index, seven_timer_transparency, iss_passover, visibility_mile,
                              visibility_km, fog_percentage, celsius_dew_point, relative_humidity_percent,
                              precipitation_proba, precipitation_amount_mm, precipitation_type, wind_direction,
                              wind_speed_mph, wind_speed_kph, frost, celsius_temp_real, celsius_temp_feel, pressure_mb,
                              ozone_du):
            forecast_hour_d[hh] = {"general_visibility": gv,
                                   "low_cloud_percent": lc,
                                   "medium_cloud_percent": mc,
                                   "high_cloud_percent": hc,
                                   "total_cloud_percent": tc,
                                   "alternative_cloud_percent": ac,
                                   "7timer_cloud_percent": sc,
                                   "7timer_seeing": ss,
                                   "7timer_lifted_ind": sl,
                                   "7timer_transparency": st,
                                   "iss_passover": iss,
                                   "visibility": {"miles": vm,
                                                  "km": vk},
                                   "fog_percent": fp,
                                   "dew_point_celsius": dp,
                                   "relative_humidity_percent": rh,
                                   "precipitation": {"probability": pp,
                                                     "amount_in_mm": pa,
                                                     "type": pt},
                                   "wind": {"direction": wd,
                                            "miles_per_hour": wm,
                                            "km_per_hour": wk},
                                   "frost": ff,
                                   "temperature": {"celsius": {"real": tr,
                                                               "feel": tf}},
                                   "pressure": {"millibar": pm},
                                   "ozone": {"dobson unit": od},
                                   }
        print(1111111, hours_and_visibility)
        return nightlight_d, daylight_d, forecast_hour_d
    return {}, {}, {}


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
    night_dict, day_dict, pred_dict = get_clearoutside_weather_forecast(lat_long[0], lat_long[1])
    # TODO: run predictions through conditions tresholds
    #########################################################################
    # TODO: use telegram or email to send message of recommendations
    return


if __name__ == "__main__":
    print(make_photo_weather_based_suggestions("Montreal, Quebec"))
