# MRO-Magic ✨
MRO-Magic is a Python script that automates the generation of flight turnaround and maintenance work packages.✈️🛠️

## 🚀 Features

- **Generates Flight Data**: Creates realistic flight schedules with various aircraft, airlines, and stations.
- **Generates Work Packages**: Automates the creation of detailed maintenance work packages from the generated flight data.

## 🛫 `CreateFlights.py`

### 🎯 Purpose
This script generates realistic flight turnaround data, including both arrivals and departures, to simulate aircraft maintenance scenarios. It can be configured for different environments to suit your needs.

### 💡 Key Features
- **Environment-aware**: Supports **test**, **uat**, **prod** environments. 🧪
- **Realistic data**: Uses actual airlines, aircraft types, registrations, and stations.🌍
- **Turnaround generation**: Creates arrival-departure flight pairs
- **Day-based selection**: Prevents duplicate data by using different aircraft registrations for each day of the week. 🗓️
- **Overnight support**: Allows for extended turnaround durations to simulate longer maintenance windows. 🌙

**⚙️ Proces Flow:**
1. Load environment configuration from FlightConfigLibrary
2. Select registrations based on turnaround duration and day of week
3. Generate arrival flight with random timing and departure station
4. Generate departure flight with calculated timing and arrival station
5. Save data to `seed/flights/seed_flight.json`

### 💻 CLI Usage
```bash
python Libraries/CreateFlights.py --environment test
# Interactive prompts:
# - Turnaround Location: AMD
# - Day Delta: 0
# - Turnaround duration: 1
# - Number of turnarounds: 3
```

## 🔧 CreateWorkpackage.py

### 🎯 Purpose
Creates comprehensive aircraft maintenance work packages based on flight turnaround data with detailed work orders and resource requirements.

### 💡 Key Features
- **Flight data integration**: Reads directly from the generated flight data file.
- **Turnaround detection**: Automatically identifies maintenance windows between flights. ⏱️
- **Work order generation**: Creates detailed maintenance tasks for each package.
- **Resource allocation**: Specifies the scope and skill requirements for each work order.
- **Aircraft mapping**: Type-specific maintenance categorization
- **Interactive customization**: User-defined work package counts

**⚙️ Process Flow:**
1. Load flight data from `seed/flights/seed_flight.json`
2. Find turnaround pairs from flight data
3. User input for work package count per turnaround
4. Calculate maintenance window between flights
5. Start work package creation
6. Start work order creation
7. Create work package with all work orders
8. Save data to `seed/workpackages/seed_workpackages.json`

### 💻 CLI Usage
```bash
python Libraries/CreateWorkpackage.py --environment test
# Interactive prompt:
# - Number of workpackages count for registration: 2
```

## 📊 Generated Data Structure

### ✈️ Flight Data Structure
```json
{
    "flightId": "7deba1d0-6536-46be-940b-f18166c7a2d5",
    "airline": "LH",
    "registration": "41SH",
    "aircraftType": "A330",
    "flightNumber": "347",
    "schedDepTime": "2025-09-07T01:30:00.000+05:30",
    "schedArrTime": "2025-09-07T06:30:00.000+05:30",
    "schedDepStation": "DEL",
    "schedArrStation": "AMD",
    "depStand": "115",
    "arrStand": "100",
    "cancelled": false
  }
```

### 📦 Work Package Structure
```json
{
  "workPackageId": "52f5136f-fbe1-4892-8791-adbe85a8164e",
  "workPackageName": "41SH/B-202509070714-185",
  "workPackageBarcode": "V1BCYXJjb2Rl-20250907",
  "station": "AMD",
  "workPackageStatus": "PLANNED",
  "workPackageArea": "ENG 1",
  "maintenanceType": "Normal",
  "maintenanceDate": "2025-09-07",
  "shortDescription": "Torque Prop Blade Retainers",
  "aircraft": "41SH",
  "aircraftType": "A330",
  "aircraftSubType": "E",
  "expectedStartDateTime": "2025-09-07T07:14:00.000+05:30",
  "expectedEndDateTime": "2025-09-07T13:57:00.000+05:30",
  "workOrders": []
}
```

## ⚠️ Troubleshooting

### 🚧 Common Issues
1. **Configuration not found**: Double-check your environment parameter and file paths.
2. **Invalid JSON**: Make sure your configuration file syntax is correct. 🧐
3. **Missing seed data**: Ensure flight data is generated before work packages
4. **Permission errors**: Check file write permissions for seed directories

### 🐛 Debug Information
- You can enable verbose logging by modifying the print statements in the code.
- Validate your JSON syntax with a linter or online tool.
- Confirm that file paths and permissions are set correctly.

## 🤝 Contributing
1. **Fork** the repository
2. **Create** a feature branch(`git checkbout -b amazing_feature`)
3. **Commit** your changes
4. **Push** to the branch
5. **Open** a Pull request

## ⚖️ License
This project is licensed under the **MIT License**

## 🙏 Acknowledgments
- Aviation industry standards for maintenance procedures
- Aircraft type and registration data from public sources

## 💌 Support 
- Email: bariaharshg@gmail.com 📧
- Issues: [GitHub Issues](https://github.com/harshbaria7371/MRO-Magic/issues) 🐛

---
**Made with ❤️ for the Aviation industry**