import pandas as pd

import requests_cache
from retry_requests import retry
from openmeteo_requests import Client


class OpenMeteoAdapter:

    def __init__(self, latitude, longitude, cache_file=".cache"):

        self.cache_file = cache_file
        self.latitude = latitude
        self.longitude = longitude

        cache_session = requests_cache.CachedSession(".cache", expire_after=-1)
        retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
        self.openmeteo = Client(session=retry_session)

        self.columns = [
            "temperature_2m",
            "relative_humidity_2m",
            "cloud_cover",
            "surface_pressure",
            "wind_speed_10m",
            "wind_direction_100m",
            "shortwave_radiation",
            "direct_radiation",
            "diffuse_radiation",
            "direct_normal_irradiance",
        ]

        self.index_name = "datetime"

    def historical(
        self, start_date: pd.Timestamp, end_date: pd.Timestamp
    ) -> pd.DataFrame:

        url = "https://archive-api.open-meteo.com/v1/archive"
        params = {
            "latitude": self.latitude,
            "longitude": self.longitude,
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
            "hourly": self.columns,
        }

        responses = self.openmeteo.weather_api(url, params=params)
        response = responses[0]
        hourly = response.Hourly()

        hourly_data = {
            self.index_name: pd.date_range(
                start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
                end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
                freq=pd.Timedelta(seconds=hourly.Interval()),
                inclusive="left",
            )
        }

        for i in range(len(self.columns)):
            hourly_data[self.columns[i]] = hourly.Variables(i).ValuesAsNumpy()

        hourly_data_frame = pd.DataFrame(data=hourly_data)
        hourly_data_frame = hourly_data_frame.set_index(self.index_name)

        return hourly_data_frame

    def forecast(
        self, start_date: pd.Timestamp, end_date: pd.Timestamp
    ) -> pd.DataFrame:
        raise NotImplementedError("forecast has not fetched yet")
