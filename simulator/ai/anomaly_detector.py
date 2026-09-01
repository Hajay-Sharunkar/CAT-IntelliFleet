import csv
import os
from datetime import datetime

INPUT_FILE = "data/telemetry_live.csv"
OUTPUT_FILE = "data/anomalies.csv"


def detect_anomalies(row):
    anomalies = []

    machine = row.get("machine_code", "UNKNOWN")
    status = row.get("status", "").upper()
    operator = row.get("operator", "")
    site = row.get("site", "")

    try:
        idle_hours = float(row.get("idle_hours", 0))
    except ValueError:
        idle_hours = 0

    try:
        engine_hours = float(row.get("engine_hours", 0))
    except ValueError:
        engine_hours = 0

    # 1. Missing operator
    if not operator or operator.upper() in ["NULL", "NONE", "N/A"]:
        anomalies.append({
            "machine_code": machine,
            "anomaly_type": "Missing Operator",
            "severity": "HIGH",
            "message": "Machine has no assigned operator.",
            "recommendation": "Assign an authorized operator or investigate the asset."
        })

    # 2. Unassigned site
    if not site or site.upper() in ["NULL", "NONE", "N/A"]:
        anomalies.append({
            "machine_code": machine,
            "anomaly_type": "Unassigned Site",
            "severity": "HIGH",
            "message": "Machine is not assigned to a site.",
            "recommendation": "Assign the machine to a valid operating site."
        })

    # 3. Excessive idle hours
    if idle_hours >= 10:
        anomalies.append({
            "machine_code": machine,
            "anomaly_type": "Excessive Idle",
            "severity": "MEDIUM",
            "message": f"Machine has {idle_hours:.1f} idle hours.",
            "recommendation": "Investigate utilization and consider reassignment."
        })

    # 4. Zero engine/runtime
    if engine_hours == 0:
        anomalies.append({
            "machine_code": machine,
            "anomaly_type": "Zero Runtime",
            "severity": "MEDIUM",
            "message": "Machine has recorded zero engine hours.",
            "recommendation": "Check whether the machine is unused, offline, or incorrectly reporting telemetry."
        })

    # 5. Idle machine marked active
    if status == "ACTIVE" and idle_hours >= 10:
        anomalies.append({
            "machine_code": machine,
            "anomaly_type": "Active But Idle",
            "severity": "HIGH",
            "message": "Machine is marked ACTIVE but has excessive idle time.",
            "recommendation": "Investigate machine usage and consider reassignment."
        })

    return anomalies


def main():

    if not os.path.exists(INPUT_FILE):
        print("ERROR: telemetry_live.csv was not found.")
        print("Run the telemetry simulator first.")
        return

    all_anomalies = []

    with open(INPUT_FILE, "r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            anomalies = detect_anomalies(row)
            all_anomalies.extend(anomalies)

    fieldnames = [
        "machine_code",
        "anomaly_type",
        "severity",
        "message",
        "recommendation"
    ]

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)

        writer.writeheader()
        writer.writerows(all_anomalies)

    print("=" * 60)
    print("CAT INTELLIFLEET - ANOMALY DETECTION")
    print("=" * 60)

    if not all_anomalies:
        print("No anomalies detected.")
    else:
        print(f"Detected {len(all_anomalies)} anomalies:\n")

        for anomaly in all_anomalies:
            print(
                f"[{anomaly['severity']}] "
                f"{anomaly['machine_code']} - "
                f"{anomaly['anomaly_type']}"
            )

            print(f"  Problem: {anomaly['message']}")
            print(f"  Action:  {anomaly['recommendation']}")
            print()

    print(f"Results saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()