import json
import os
import sys
import random
import uuid

sys.path.insert(0, os.path.dirname(__file__))
from FlightConfigLibrary import FlightConfigLibrary

class CreateFlights:

    date_time_format = '%Y-%m-%dT%H:%M:00.000+05:30' # Indian Time format

    def __init__(self, environment="test"):
        self.config = FlightConfigLibrary(environment)
        self.used_registrations = set()

    def generate_turnaround_data(self, turnaround_loc, turnaround_duration=0, num_turnarounds=1, day_delta=0):
        from datetime import datetime, timedelta

        airlines = self.config.get_airlines()
        aircraft_types = self.config.get_aircraft_types()
        stations = self.config.get_stations()
        stands = self.config.get_stands()

        current_day = (datetime.now() + timedelta(days=day_delta)).weekday()

        if int(turnaround_duration) > 0:
            registrations = self.config.get_overnight_registrations()
        else:
            registrations = self.config.get_current_weekday_registrations(day_delta)

        turnarounds = []

        base_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

        for index in range(num_turnarounds):
            airline = random.choice(airlines)
            aircraft_type = random.choice(aircraft_types)
            available_registrations = [registration for registration in registrations if registration not in self.used_registrations]
            if not available_registrations:
                self.used_registrations.clear()
                available_registrations = registrations

            registration = random.choice(available_registrations)
            self.used_registrations.add(registration)
            flight_number = str(random.randint(100, 999))

            arrival_date = base_date + timedelta(days=day_delta)
            arrival_time = arrival_date.replace(
                hour=random.randint(1,15),
                minute=random.choice([0,10,15,20,25,30,35,40,45,50,55])
            )

            departure_time = arrival_time - timedelta(hours=random.randint(1,5))

            available_stations = [station for station in stations if station != turnaround_loc]
            departure_station = random.choice(available_stations)

            arrival_flight = {
                "flightId": str(uuid.uuid4()),
                "airline": airline,
                "registration": registration,
                "aircraftType": aircraft_type,
                "flightNumber": flight_number,
                "schedDepTime": departure_time.strftime("%Y-%m-%dT%H:%M:00.000+05:30"),
                "schedArrTime": arrival_time.strftime("%Y-%m-%dT%H:%M:00.000+05:30"),
                "schedDepStation": departure_station,
                "schedArrStation": turnaround_loc,
                "depStand": random.choice(stands),
                "origDepStand": random.choice(stands),
                "arrStand": random.choice(stands),
                "origArrStand": random.choice(stands),
                "cancelled": False
            }

            # Generate Departure flight
            if int(turnaround_duration) == 0:
                departure_time = arrival_time + timedelta(hours=random.randint(7,10))
            else:
                try:
                    days_to_add = int(turnaround_duration)
                    departure_time = arrival_time + timedelta(days=days_to_add, hours=random.randint(7,10))
                except ValueError:
                    departure_time = arrival_time + timedelta(hours=random.randint(7,10))

            arrival_time = departure_time + timedelta(hours=random.randint(2,4))

            arrival_station = random.choice(available_stations)

            departure_flght = {
                "flightId": str(uuid.uuid4()),
                "airline": airline,
                "registration": registration,
                "aircraftType": aircraft_type,
                "flightNumber": flight_number,
                "schedDepTime": departure_time.strftime("%Y-%m-%dT%H:%M:00.000+05:30"),
                "schedArrTime": arrival_time.strftime("%Y-%m-%dT%H:%M:00.000+05:30"),
                "schedDepStation": turnaround_loc,
                "schedArrStation": arrival_station,
                "depStand": random.choice(stands),
                "origDepStand": random.choice(stands),
                "arrStand": random.choice(stands),
                "origArrStand": random.choice(stands),
                "cancelled": False
            }

            turnarounds.extend([arrival_flight, departure_flght])

            try:
                os.makedirs('seed/flights',exist_ok=True)

                with open('seed/flights/seed_flight.json','w') as f:
                    json.dump(turnarounds, f, indent=2, sort_keys=False, default=str)
                    print(f"Successfully wrote {len(turnarounds)} to seed/flights")
            except Exception as e:
                print(f"Failed to write flight data to seed/flights")


if __name__ == '__main__':
    import argparse
    import os

    # Get environment from command line argument
    parser = argparse.ArgumentParser(description='Generate Flight Data')
    parser.add_argument('--environment', '-e', type=str, default='test', help="Environment to use (test, uat, prod)")
    args = parser.parse_args()

    print(f"Using environment: {args.environment}")
    location = str(input("Enter turnaround location (e.g., HEL, AMD, SIN, AMS) :"))
    day_delta = int(input("Enter after how many days to generate turnaround (default:0 for today's data) :"))
    duration = int(input("Enter turnaround duration (default:0 for today's data, 1 for next day,...) :"))
    count = int(input("How many flights to generate?: "))

    library = CreateFlights(args.environment)
    library.generate_turnaround_data(location, duration, count, day_delta)

    # Run with given CLI
    # python Libraries/CreateFlights.py --environment test
