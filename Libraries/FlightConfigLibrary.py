import json
import os
from datetime import datetime, timedelta


class FlightConfigLibrary:
    def __init__(self, environment=None):
        self.environment = environment or self._get_environment()
        self.config = self._load_config()

    def _get_environment(self):
        return os.environ.get("TESTING_ENVIRONMENT", 'test')

    def _load_config(self):
        config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'flight_config.json')

        try:
            with open(config_path, 'r', encoding='utf-8') as config_file:
                config_data = json.load(config_file)

                if self.environment not in config_data:
                    raise ValueError(f"Environment '{self.environment}' not found in config file")

            return config_data[self.environment]

        except FileNotFoundError:
            raise FileNotFoundError(f"Environment '{self.environment}' not found in config file")
        except json.JSONDecodeError as e:
            raise ValueError(f"Environment '{self.environment}' is not a valid JSON")
        except Exception as e:
            raise ValueError(f"Unexpected error: {e}")

    def get_airlines(self):
        return self.config.get("airlines", [])

    def get_aircraft_types(self):
        return self.config.get("aircraft_Types", [])

    def get_stations(self):
        return self.config.get("stations", [])

    def get_stands(self):
        return self.config.get("stands", [])

    def get_registrations_by_day(self, day_name=None):

        registrations_by_day = self.config.get("registrations_by_day", {})

        if day_name is None:
            all_registrations = []
            for day_registrations in registrations_by_day.values():
                all_registrations.extend(day_registrations)
            return all_registrations

        return registrations_by_day.get(day_name.lower(), [])

    def get_environment_info(self):
        return {
            'environment': self.environment,
            'airlines_count': len(self.get_airlines()),
            'aircraft_types_count': len(self.get_aircraft_types()),
            'stands_count': len(self.get_stands()),
            'total_registrations': len(self.get_registrations_by_day()),
            'stations_count': len(self.get_stations())
        }

    def get_overnight_registrations(self):
        self.get_registrations_by_day('overnight')

    def get_current_weekday_registrations(self, day_delta=0):
        current_date = datetime.now()
        target_date = current_date + timedelta(days=day_delta)

        if day_delta != 0:
            target_date = target_date + timedelta(days=day_delta)

        weekday_index = target_date.weekday()
        return self.get_registrations_for_weekday(weekday_index)

    def get_registrations_for_weekday(self, weekday_index):

        weekday_names = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]

        if weekday_index < 0 or weekday_index > 6:
            raise ValueError(f"Weekday index {weekday_index} is not valid")

        day_name = weekday_names[weekday_index]
        return self.get_registrations_by_day(day_name)