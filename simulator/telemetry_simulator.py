import csv
import random
import time
import json
from datetime import datetime

INPUT_FILE = "data/seed_machines.csv"
OUTPUT_FILE = "data/telemetry_live.csv"


def load_machines():
    with open(INPUT_FILE, "r", newline="", encoding="utf-8") as file:
        return list(csv.DictReader(file))


def generate_telemetry(machine):
    # Simulate small changes in machine readings
    fuel = max(0, min(100, float(machine["fuel"]) + random.uniform(-0.5, 0.2)))

    engine_hours = (
        float(machine["engine_hours"])
        + random.uniform(0.01, 0.05)
    )

    idle_hours = (
        float(machine["idle_hours"])
        + random.uniform(0, 0.05)
    )

    # Simulate location around the assigned site
    latitude = 12.9718 + random.uniform(-0.01, 0.01)
    longitude = 77.6412 + random.uniform(-0.01, 0.01)

    telemetry = {
        "machine_code": machine["machine_code"],
        "machine_type": machine["machine_type"],
        "status": machine["status"],
        "site": machine["site"],
        "operator": machine["operator"],
        "fuel": round(fuel, 2),
        "engine_hours": round(engine_hours, 2),
        "idle_hours": round(idle_hours, 2),
        "latitude": round(latitude, 6),
        "longitude": round(longitude, 6),
        "rental_end": machine["rental_end"],
        "timestamp": datetime.now().isoformat(timespec="seconds")
    }

    return telemetry


def save_telemetry(telemetry):
    file_exists = False

    try:
        with open(OUTPUT_FILE, "r", encoding="utf-8"):
            file_exists = True
    except FileNotFoundError:
        pass

    with open(OUTPUT_FILE, "a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=telemetry.keys()
        )

        if not file_exists:
            writer.writeheader()

        writer.writerow(telemetry)


def main():
    machines = load_machines()

    print("=" * 60)
    print("CAT INTELLIFLEET - TELEMETRY SIMULATOR")
    print("=" * 60)
    print("Live telemetry simulation started...")
    print("Press CTRL+C to stop.\n")

    while True:

        for machine in machines:

            telemetry = generate_telemetry(machine)

            save_telemetry(telemetry)

            print(json.dumps(telemetry, indent=2))

            time.sleep(2)


if __name__ == "__main__":
    main()