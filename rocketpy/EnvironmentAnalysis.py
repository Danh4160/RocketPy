from datetime import datetime
from datetime import timedelta

import numpy as np

from .Environment import Environment
from .Function import Function

from windrose import WindroseAxes, WindAxes
from matplotlib import pyplot as plt
import numpy as np


class EnvironmentAnalysis:
    def __init__(self, railLength,
                 start_date,
                 end_date,
                 gravity=9.80665,
                 latitude=0,
                 longitude=0,
                 elevation=0,
                 datum="SIRGAS2000",
                 timeZone="UTC"):

        # not the bast fashion
        hours = (datetime(*end_date) - datetime(*start_date)).days * 24
        self.environments = []

        for hour in range(0, hours, 3):
            # error handling for days that there isn't data
            date = datetime(*start_date) + timedelta(hours=hour)

            # may be a solution more slow, but less intrusive on the environment class
            environment = Environment(railLength,
                                      gravity=gravity,
                                      date=date,
                                      latitude=latitude,
                                      longitude=longitude,
                                      elevation=elevation,
                                      datum=datum,
                                      timeZone=timeZone)
            try:
                environment.setAtmosphericModel(type='Forecast', file='GFS')
            except ValueError as exc:
                print(str(exc))
                continue
            self.environments.append(environment)

        self.average_max_temperature = 0
        self.average_min_temperature = 0
        self.max_temperature = 0
        self.min_temperature = 0

        self.average_max_wind_gust = 0
        self.maximum_wind_gust = 0

        self.average_day_wind_profile = None

        self.average_wind_profile()

    def process_data(self):
        self.calculate_average_max_temperature()
        self.calculate_average_min_temperature()
        self.calculate_max_temperature()
        self.calculate_min_temperature()

        self.calculate_average_max_wind_gust()
        self.calculate_maximum_wind_gust()

    def calculate_average_max_temperature(self):
        self.average_max_temperature = np.average(
            [np.max(env.temperature.source[:, 1]) for env in self.environments])

    def calculate_average_min_temperature(self):
        self.average_min_temperature = np.average(
            [np.min(env.temperature.source[:, 1]) for env in self.environments])

    def calculate_max_temperature(self):
        self.max_temperature = np.max(
            [np.max(env.temperature.source[:, 1]) for env in self.environments])

    def calculate_min_temperature(self):
        self.min_temperature = np.min(
            [np.min(env.temperature.source[:, 1]) for env in self.environments])

    def calculate_average_max_wind_gust(self):
        self.average_max_wind_gust = np.average(
            [np.max(env.windSpeed.source[:, 1]) for env in self.environments])

    def calculate_maximum_wind_gust(self):
        self.maximum_wind_gust = np.max(
            [np.max(env.windSpeed.source[:, 1]) for env in self.environments])

    def get_wind_speed(self, i):
        windDirection = []
        windSpeed = []
        for idx in range(i, len(self.environments), 8):
            windDirection.extend(self.environments[idx].windDirection.source[:, 1])
            windSpeed.extend(self.environments[idx].windSpeed.source[:, 1])
        return windSpeed, windDirection

    def animate_wind_rose(self):
        ax = WindroseAxes.from_ax()
        for i in range(8):
            windSpeed, windDir = self.get_wind_speed(i)
            ax.bar(windSpeed, windDir, normed=True, opening=0.8, edgecolor='white')
            plt.pause(0.3)

        plt.show()

    def calculate_average_wind_profile(self):
        windSpeedAverage = []
        x = []

        for i in range(8):
            windSpeed, windDir = self.get_wind_speed(i)
            windSpeedAverage.append(np.average(windSpeed))
            x.append(i * 3)
        average_speed = Function(np.array([x, windSpeedAverage]).T, inputs="Hour in the day",
                                 outputs="Wind Speed (m/s)",
                                 interpolation="linear", )
        self.average_day_wind_profile = average_speed

    def wind_profile(self):
        windSpeed = []
        for idx in range(0, len(self.environments)):
            windSpeed.extend(self.environments[idx].windSpeed.source[:, 1])
        ax = WindAxes.from_ax()
        ax.pdf(array, Nbins=20)
        plt.show()
