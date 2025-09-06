import math
import uuid
from datetime import datetime, timedelta
import json
import os
import random


class CreateWorkpackages:
    def __init__(self, environment=None):
        self.environment = environment or os.environ.get("TESTING_ENVIRONMENT", 'test')

        self.config = self._load_config(self.environment)

        self.scope_values = self.config.get('scope_values', [])
        self.skill_values = self.config.get('skill_values', [])
        self.wp_names = self.config.get('wp_names', [])
        self.aircraft_subtypes = self.config.get('aircraft_subtypes', [])
        self.work_order_area = self.config.get('work_order_area', [])
        self.work_package_area = self.config.get('work_package_area', [])
        self.work_order_names = self.config.get('work_order_names', [])


    def _load_config(self, environment):
        try:
            config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'workpackage_config.json')
            with open(config_path, 'r', encoding='utf-8') as config_file:
                config_data = json.load(config_file)

            if environment is None:
                environment = os.environ.get("TESTING_ENVIRONMENT", 'test')

            if environment in config_data:
                return config_data[environment]
            else:
                print(f"Environment '{environment}' not found in config file")
                return config_data.get('test', {})

        except FileNotFoundError:
            print(f"Environment '{environment}' not found in config file")
            return config_data.get('test', {})
        except Exception as e:
            print(f"Failed to load config file '{e}'")
            return config_data.get('test', {})

    def _load_flight_data(self):
        with open('seed/flights/seed_flight.json', 'r') as flight_file:
            return json.load(flight_file)

    def _find_turnaround_pairs(self, flight_data):
        turnaround_pairs = []

        for index in range(len(flight_data)-1):
            current = flight_data[index]
            next = flight_data[index+1]
            if (current['registration'] == next['registration'] and
                current['schedArrStation'] == next['schedDepStation']):
                turnaround_pairs.append((current, next))

        return turnaround_pairs

    def _calculate_maintenance_window(self, arrival_flight, departure_flight):
        inbound_arrival = datetime.strptime(arrival_flight['schedArrTime'], '%Y-%m-%dT%H:%M:%S.000+05:30')
        outbound_departure = datetime.strptime(departure_flight['schedDepTime'], '%Y-%m-%dT%H:%M:%S.000+05:30')

        start_time = inbound_arrival + timedelta(minutes=random.randint(15,45))
        end_time = outbound_departure - timedelta(minutes=random.randint(15,45))

        if end_time <= start_time:

            end_time = start_time + timedelta(minutes=60)

        return start_time, end_time

    def _create_scope_requirement(self, time_diff_minutes):

        use_scope = random.choice([True, False])

        if time_diff_minutes > 480:
            if time_diff_minutes > 1500:
                max_minutes = 1500
            else:
                max_minutes = int(time_diff_minutes)
            total_minutes = random.randint(120, max_minutes)

            if total_minutes <= 480:
                quantity = 1
            else:
                min_qty = math.ceil(time_diff_minutes // 240) // 2
                max_qty = math.ceil(time_diff_minutes // 240)
                quantity = random.randint(min_qty, max_qty)
        else:
            total_minutes = random.randint(30, int(time_diff_minutes))
            quantity = 1

        requirement = {
            "total_minutes": total_minutes,
            "quantity": quantity,
        }

        if use_scope:
            requirement["scopeValue"] = random.choice(self.scope_values)
        else:
            requirement["skillValue"] = random.choice(self.skill_values)

        return requirement

    def _get_aircraft_subtype(self, aircraft_type):
        try:
            mapping_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'aircraft_subtype_mappings.json')
            with open(mapping_path, 'r') as mapping_file:
                mapping_config = json.load(mapping_file)

            mappings = mapping_config.get('mappings', {})
            default_subtypes = mapping_config.get('default_subtypes', {}).get(self.environment, ['A', 'B'])

            subType = mappings.get(aircraft_type)

            if subType is None:
                return random.choice(self.aircraft_subtypes)

            if isinstance(subType, list):
                return random.choice(subType)

            return subType
        except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
            return random.choice(self.aircraft_subtypes)

    def _create_workorder(self, date_prefix, end_time, time_diff_minutes, param):
        num_scope_required = random.randint(1,5)
        scope_requirements = []

        for index in range(num_scope_required):
            new_requirement = self._create_scope_requirement(time_diff_minutes)

            new_requirement["index"] = index + 1

            duplicate = False
            for existing_requirement in scope_requirements:
                if ('skillValue' in new_requirement and 'skillValue' in existing_requirement and
                new_requirement['skillValue'] == existing_requirement['skillValue'] ):
                    duplicate = True
                    break
                if ('scopeValue' in new_requirement and 'scopeValue' in existing_requirement and
                new_requirement['scopeValue'] == existing_requirement['scopeValue'] ):
                    duplicate = True
                    break

            if not duplicate:
                scope_requirements.append(new_requirement)

        for index, requirement in enumerate(scope_requirements):
            requirement["index"] = index + 1

        order_number_random = random.randint(100,999)

        return {
            "workorderId": str(uuid.uuid4()),
            "workOrderName": random.choice(self.work_order_names),
            "workOrderBarcode": f"V09CYXJjb2Rl-{date_prefix}_{order_number_random}",
            "workOrderDueDate": end_time.strftime("%Y-%m-%dT%H:%M:00.000+05:30"),
            "workOrderStatus": random.choice(["PLANNED", "OPEN", "IN PROGRESS"]),
            "workOrderArea": random.choice(self.work_order_area),
            "workOrderPriority": random.randint(1,2),
            "workOrderSequence": random.randint(1,2),
            "scopeRequirements": scope_requirements
        }

    def _create_workpackage(self, arrival_flight, start_time, end_time, workorders):
        date_prefix = start_time.strftime("%Y%m%d")
        workpackage_name = f"{arrival_flight['registration']}/{random.choice(self.wp_names)}-{start_time.strftime('%Y%m%d%H%M')}-{random.randint(100,999):03d}"

        aircraft_subtype = self._get_aircraft_subtype(arrival_flight['aircraftType'])

        return {
            "workPackageId": str(uuid.uuid4()),
            "workPackageName": workpackage_name,
            "workPackageBarcode": f"V1BCYXJjb2Rl-{date_prefix}",
            "station": arrival_flight['schedArrStation'],
            "workPackageStatus": random.choice(["PLANNED", "OPEN", "IN PROGRESS"]),
            "workPackageArea": random.choice(self.work_order_area),
            "maintenanceType": "Normal",
            "maintenanceDate": start_time.strftime("%Y-%m-%d"),
            "shortDescription": random.choice(self.work_order_names),
            "aircraft": arrival_flight['registration'],
            "aircraftType": arrival_flight['aircraftType'],
            "aircraftSubType": aircraft_subtype,
            "expectedStartDateTime": start_time.strftime("%Y-%m-%dT%H:%M:00.000+05:30"),
            "expectedEndDateTime": end_time.strftime("%Y-%m-%dT%H:%M:00.000+05:30"),
            "workOrders": workorders
        }


    def generate_workpackage_data(self):

        global number_of_workorders
        flight_data = self._load_flight_data()
        turnaround_pairs = self._find_turnaround_pairs(flight_data)

        workpackages = []

        for arrival_flight, departure_flight in turnaround_pairs:
            req_turnaround = int(input(f'Enter number of workpackages for Registration {arrival_flight["registration"]}: '))

            if req_turnaround > 0:
                if req_turnaround <= 5:
                    number_of_workorders = random.randint(1, 6)
                else:
                    number_of_workorders = random.randint(7,20)

            start_time, end_time = self._calculate_maintenance_window(arrival_flight, departure_flight)

            time_diff = (end_time - start_time).days

            time_difference = (end_time - start_time).total_seconds()

            # Convert the difference to minutes
            time_diff_minutes = time_difference / 60

            for index_turnaround in range(req_turnaround):
                workorders = []
                date_prefix = start_time.strftime('%Y%m%d')

                for index_workorder in range(number_of_workorders):
                    workorder = self._create_workorder(
                        date_prefix, end_time, time_diff_minutes, index_workorder+1
                    )
                    workorders.append(workorder)

                workpackage = self._create_workpackage(arrival_flight, start_time, end_time, workorders)
                workpackages.append(workpackage)

        try:
            os.makedirs('seed/workpackages', exist_ok=True)
            with open('seed/workpackages/workpackages.json', 'w') as outfile:
                json.dump(workpackages, outfile, indent=2)
            print(f"Successfully wrote {len(workpackages)} workpackages to 'seed/workpackages'")
        except Exception as e:
            print(e)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Create work packages')
    parser.add_argument('-e', '--environment', type=str, default='test', help='Environment to use (test, uat, prod)')

    args = parser.parse_args()

    CW = CreateWorkpackages(environment=args.environment)

    CW.generate_workpackage_data()
