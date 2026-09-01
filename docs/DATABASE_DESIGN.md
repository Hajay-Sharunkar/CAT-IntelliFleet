# CAT IntelliFleet — Database Design Document

| | |
|---|---|
| **Project** | CAT IntelliFleet – AI Powered Fleet Decision Platform |
| **Document type** | Logical and physical database design (specification only — no SQL or ORM code) |
| **Target database** | PostgreSQL |
| **Audience** | Backend developers implementing SQLAlchemy models and Alembic migrations |
| **Version** | 1.1 |
| **Date** | 1 September 2026 |

---

## Introduction

CAT IntelliFleet is an **AI-powered fleet decision platform** for Caterpillar. It is **not** a rental tracking system. The database exists to give fleet managers a single, trustworthy source of truth for machines, sites, operators, and day-to-day operations — and to power the intelligence layer that reduces downtime, improves utilization, predicts demand, detects anomalies, and records how managers act on AI advice.

This document defines the **complete relational schema** for that platform. It specifies tables, columns, PostgreSQL data types, keys, relationships, allowed status values, indexes, and integrity rules. A backend developer should be able to implement SQLAlchemy models directly from this specification without inventing additional schema.

### What this database must support

| Capability | How the schema delivers it |
|---|---|
| Reduce downtime | `maintenance` history, `alerts`, and `recommendations` for proactive service |
| Improve asset utilization | `telemetry` time-series + `rentals` assignment history |
| Predict demand | `rentals` × `sites` × `assets.machine_type` as feature sources |
| Detect anomalies | `telemetry` ingestion → materialized `alerts` |
| Decision support | Persisted `recommendations` + `decision_log` audit trail |

### Architectural centre: `assets`

Every machine-centric table hangs off **`assets`**, not off a rental record. A machine has a life beyond a single checkout. Telemetry, maintenance, alerts, and recommendations all reference `asset_id`. Rentals record assignment history but do not own sensor or AI data.

```
                    ┌─────────────┐
                    │    users    │  (authentication — no FK edges in v1)
                    └─────────────┘

┌──────────┐     ┌──────────┐     ┌────────────┐
│  sites   │────▶│  assets  │◀────│ operators  │
└──────────┘     └────┬─────┘     └────────────┘
                      │
        ┌─────────────┼─────────────┬──────────────┐
        ▼             ▼             ▼              ▼
    rentals      telemetry    maintenance       alerts
   (history)   (append-only)  (work orders)  (detections)
                                              │
                                              ▼
                                       recommendations
                                              │
                                              ▼
                                        decision_log
```

---

## Table of contents

1. [Design principles](#1-design-principles)
2. [Naming and type conventions](#2-naming-and-type-conventions)
3. [Table catalogue by layer](#3-table-catalogue-by-layer)
4. [Master data tables](#4-master-data-tables)
5. [Operational data tables](#5-operational-data-tables)
6. [Intelligence data tables](#6-intelligence-data-tables)
7. [Foreign-key relationship matrix](#7-foreign-key-relationship-matrix)
8. [Cardinality summary](#8-cardinality-summary)
9. [Relationship diagrams](#9-relationship-diagrams)
10. [Referential integrity and update rules](#10-referential-integrity-and-update-rules)
11. [Design rationale](#11-design-rationale)
12. [How the schema supports product features](#12-how-the-schema-supports-product-features)
13. [Implementation guidance (no code)](#13-implementation-guidance-no-code)
14. [Out of scope](#14-out-of-scope)

---

## 1. Design principles

1. **Assets are the hub.** Operational and intelligence tables reference the machine, not the rental contract.
2. **Telemetry is historical, never current-state.** `assets` stores *where the machine is assigned now*. `telemetry` stores *every sensor reading over time*. They must not be merged.
3. **AI output is persisted.** Alerts and recommendations are written once and tracked through their lifecycle — not recomputed on every dashboard load.
4. **Decisions are first-class data.** `decision_log` is separate from `recommendations` so accept/reject rates and audit trails are measurable.
5. **Current assignment vs history.** `assets.current_site_id` and `assets.current_operator_id` are denormalized pointers for fast dashboards. `rentals` is the historical source of truth.
6. **Identity vs operations.** `users` handles login. Operators, site managers, and technicians are operational entities and are not assumed to share a row with `users` in this version.

---

## 2. Naming and type conventions

| Convention | Rule |
|---|---|
| Table names | Lowercase `snake_case`, plural (`users`, `assets`). Exceptions: `telemetry` (mass noun), `decision_log` (event log). |
| Primary keys | Surrogate integer IDs. `BIGINT` for `telemetry` only; `INTEGER` for all others. |
| Foreign keys | Named `<referenced_table_singular>_id` (e.g. `asset_id`, `site_id`). |
| Timestamps | `TIMESTAMPTZ` stored in UTC; UI converts to local time. |
| Money / scores | `NUMERIC` with explicit precision — never `FLOAT` for money. |
| Coordinates | `DOUBLE PRECISION`. Latitude −90 to 90; longitude −180 to 180. |
| Status / type columns | `VARCHAR` with a documented closed value set. Implement as PostgreSQL `ENUM` or `CHECK` constraint. |
| Soft deletes | Not used. Rows are retained; status columns represent lifecycle. |
| Passwords | Only `password_hash` stored. Never plaintext. |

---

## 3. Table catalogue by layer

Tables are grouped by the role they play in the platform. **`assets`** appears under Master Data but is also the hub for all downstream tables.

### Master Data

Reference entities that change slowly and define *who* and *what* exists in the fleet.

| Table | Purpose |
|---|---|
| `users` | Login identity and authorization |
| `sites` | Construction / mining locations |
| `operators` | People who run machines |
| `assets` | Machines — identity, classification, and current assignment snapshot |

### Operational Data

Day-to-day transactions and time-series facts that describe *what is happening*.

| Table | Purpose |
|---|---|
| `rentals` | Checkout / return assignment history |
| `telemetry` | Append-only machine sensor readings |
| `maintenance` | Planned and completed service work orders |

### Intelligence Data

System-generated insights and human responses — *what the platform detected, advised, and what managers decided*.

| Table | Purpose |
|---|---|
| `alerts` | Rule/model-detected operational problems |
| `recommendations` | AI-generated recommended actions |
| `decision_log` | Manager accept/reject/modify audit trail |

---

## 4. Master data tables

---

### 4.1 `users`

**Layer:** Master Data

#### Purpose

Stores login identity for the platform. Answers: *who can sign in, and with what permission?* Does **not** store operator certifications, site assignments, or rental history.

#### Columns

| Column | PostgreSQL data type | Nullable | Description |
|---|---|---|---|
| `user_id` | `INTEGER` | No | Surrogate primary key |
| `full_name` | `VARCHAR(150)` | No | Display name in UI and audit text |
| `email` | `VARCHAR(255)` | No | Login identifier; unique; stored lowercase |
| `password_hash` | `VARCHAR(255)` | No | Bcrypt (or equivalent) hash only |
| `role` | `VARCHAR(50)` | No | Authorization role |
| `created_at` | `TIMESTAMPTZ` | No | Account creation time; default UTC now |

#### Primary key

| Column |
|---|
| `user_id` |

#### Foreign keys

None.

#### Relationships

| Direction | Related table | Via | Notes |
|---|---|---|---|
| — | — | — | No FK relationships in v1 |
| Logical | `decision_log` | `manager_name` | Name match until `user_id` is added later |
| Logical | `sites` | `manager_name` | Display field; not a FK |

#### Allowed enum / status values

**`role`**

| Value | Meaning |
|---|---|
| `admin` | Full system access, user management |
| `fleet_manager` | Dashboard, alerts, recommendations, decisions |
| `technician` | Maintenance records |
| `viewer` | Read-only dashboards |

#### Important notes

- Operators who never log into the web app live in `operators`, not here.
- `created_at` is immutable after insert.
- Do not store plaintext passwords or session tokens in this table.

#### Suggested indexes

| Index | Type | Purpose |
|---|---|---|
| `email` | UNIQUE | Login lookup |
| `role` | B-tree (optional) | Admin UI role filter |

---

### 4.2 `sites`

**Layer:** Master Data

#### Purpose

Stores construction and mining sites where Caterpillar machines are deployed. Provides geographic and managerial context for utilization, demand forecasting, and "move machine" recommendations.

#### Columns

| Column | PostgreSQL data type | Nullable | Description |
|---|---|---|---|
| `site_id` | `INTEGER` | No | Surrogate primary key |
| `site_name` | `VARCHAR(150)` | No | Human-readable site name |
| `address` | `VARCHAR(500)` | Yes | Street / site address |
| `latitude` | `DOUBLE PRECISION` | Yes | Site centroid latitude |
| `longitude` | `DOUBLE PRECISION` | Yes | Site centroid longitude |
| `manager_name` | `VARCHAR(150)` | Yes | On-site or regional manager display name |
| `status` | `VARCHAR(30)` | No | Whether the site is currently active |

#### Primary key

| Column |
|---|
| `site_id` |

#### Foreign keys

None.

#### Relationships

| Direction | Related table | Via | Cardinality |
|---|---|---|---|
| Parent of | `operators` | `operators.assigned_site` → `sites.site_id` | 1 site : N operators |
| Parent of | `assets` | `assets.current_site_id` → `sites.site_id` | 1 site : N assets (current) |
| Parent of | `rentals` | `rentals.site_id` → `sites.site_id` | 1 site : N rentals |

A site may have zero machines (new site or all returned) and may have operators assigned without an active rental.

#### Allowed enum / status values

**`status`**

| Value | Meaning |
|---|---|
| `active` | Site operating; machines may be assigned |
| `inactive` | Site closed or paused; no new rentals |
| `planned` | Site planned but not yet live |

#### Important notes

- Site latitude/longitude is the **site centroid**, not live machine GPS (that belongs in `telemetry`).
- `manager_name` is a display field, not a FK to `users`.
- Unique `site_name` is recommended if names appear in UI dropdowns.

#### Suggested indexes

| Index | Type | Purpose |
|---|---|---|
| `site_name` | UNIQUE (recommended) | Dropdown lookup |
| `status` | B-tree | "Active sites" dashboard filter |

---

### 4.3 `operators`

**Layer:** Master Data

#### Purpose

Stores equipment operators — people who physically run machines on site. Supports "missing operator" alerts, "assign operator" recommendations, and utilization analysis by skill level.

#### Columns

| Column | PostgreSQL data type | Nullable | Description |
|---|---|---|---|
| `operator_id` | `INTEGER` | No | Surrogate primary key |
| `operator_name` | `VARCHAR(150)` | No | Full name |
| `phone` | `VARCHAR(30)` | Yes | Contact number |
| `experience_level` | `VARCHAR(30)` | No | Skill band for assignment logic |
| `certification` | `VARCHAR(150)` | Yes | License summary (e.g. "Excavator Class A") |
| `assigned_site` | `INTEGER` | Yes | Home site; FK → `sites.site_id` |
| `availability_status` | `VARCHAR(30)` | No | Whether operator can take a machine |

#### Primary key

| Column |
|---|
| `operator_id` |

#### Foreign keys

| Column | References | On delete | On update |
|---|---|---|---|
| `assigned_site` | `sites.site_id` | `SET NULL` | `CASCADE` |

#### Relationships

| Direction | Related table | Via | Cardinality |
|---|---|---|---|
| Child of | `sites` | `assigned_site` | N operators : 1 site |
| Parent of | `assets` | `assets.current_operator_id` → `operators.operator_id` | 1 operator : N assets (current) |
| Parent of | `rentals` | `rentals.operator_id` → `operators.operator_id` | 1 operator : N rentals |

An operator may currently run zero or one machine (`assets.current_operator_id`). Historical work across machines is in `rentals`.

#### Allowed enum / status values

**`experience_level`**

| Value | Meaning |
|---|---|
| `trainee` | Supervised operation only |
| `intermediate` | Standard machines |
| `senior` | Complex / high-value machines |
| `expert` | Any class; may train others |

**`availability_status`**

| Value | Meaning |
|---|---|
| `available` | Can be assigned |
| `on_duty` | Currently assigned to a machine |
| `off_duty` | Not working this shift |
| `unavailable` | Leave, injury, or otherwise blocked |

#### Important notes

- `assigned_site` is the operator's **home site**, not a visit history.
- Missing operator alert: rented asset with `current_operator_id` null, or rental with `operator_id` null.
- Do not store login credentials here.

#### Suggested indexes

| Index | Type | Purpose |
|---|---|---|
| `(assigned_site, availability_status)` | Composite B-tree | "Who can I assign at this site?" |
| `assigned_site` | B-tree | Site operator list |

---

### 4.4 `assets` — Fleet Hub

**Layer:** Master Data (central hub for all other layers)

#### Purpose

Master record for every rental machine in the Caterpillar fleet. Stores **identity, classification, and current operational snapshot only**. Does **not** store telemetry history, maintenance history, alerts, or recommendations.

#### Columns

| Column | PostgreSQL data type | Nullable | Description |
|---|---|---|---|
| `asset_id` | `INTEGER` | No | Surrogate primary key |
| `serial_number` | `VARCHAR(80)` | No | Manufacturer serial; unique across fleet |
| `machine_name` | `VARCHAR(150)` | No | Display name (e.g. "CAT 336 – North Pit") |
| `machine_type` | `VARCHAR(80)` | No | Machine class |
| `manufacturer` | `VARCHAR(80)` | No | Typically `Caterpillar` |
| `model` | `VARCHAR(80)` | No | Model code (e.g. `336`, `D8T`) |
| `manufacturing_year` | `INTEGER` | Yes | Model year; range 1980 – current year + 1 |
| `current_status` | `VARCHAR(30)` | No | Live mechanical/operational state |
| `rental_status` | `VARCHAR(30)` | No | Commercial / assignment state |
| `current_site_id` | `INTEGER` | Yes | Current site; null if in yard / unassigned |
| `current_operator_id` | `INTEGER` | Yes | Current operator; null if unmanned |
| `created_at` | `TIMESTAMPTZ` | No | Row creation; default UTC now |
| `updated_at` | `TIMESTAMPTZ` | No | Last mutation; application must update on change |

#### Primary key

| Column |
|---|
| `asset_id` |

#### Foreign keys

| Column | References | On delete | On update |
|---|---|---|---|
| `current_site_id` | `sites.site_id` | `SET NULL` | `CASCADE` |
| `current_operator_id` | `operators.operator_id` | `SET NULL` | `CASCADE` |

Deleting a site or operator must not delete the machine — the current pointer is cleared.

#### Relationships

| Direction | Related table | Via | Cardinality |
|---|---|---|---|
| Child of | `sites` | `current_site_id` | N assets : 1 site |
| Child of | `operators` | `current_operator_id` | N assets : 1 operator |
| Parent of | `rentals` | `rentals.asset_id` | 1 asset : N rentals |
| Parent of | `telemetry` | `telemetry.asset_id` | 1 asset : N readings (very large N) |
| Parent of | `maintenance` | `maintenance.asset_id` | 1 asset : N work orders |
| Parent of | `alerts` | `alerts.asset_id` | 1 asset : N alerts |
| Parent of | `recommendations` | `recommendations.asset_id` | 1 asset : N recommendations |

`assets` is the parent of all machine-centric operational and intelligence tables.

#### Allowed enum / status values

**`machine_type`**

`excavator` · `dozer` · `wheel_loader` · `haul_truck` · `motor_grader` · `backhoe_loader` · `articulated_truck` · `compactor` · `other`

**`current_status`** *(mechanical / operational)*

| Value | Meaning |
|---|---|
| `operational` | Machine is working |
| `idle` | On site but not producing work |
| `maintenance` | In service |
| `down` | Failed / cannot operate |
| `in_transit` | Being moved between sites |

**`rental_status`** *(commercial / assignment)*

| Value | Meaning |
|---|---|
| `available` | In yard / pool; can be rented |
| `reserved` | Earmarked; not yet checked out |
| `rented` | Checked out to a site |
| `overdue` | Past expected return; not yet returned |
| `returned` | Last rental closed; awaiting next assignment |

A machine can be `operational` and `rented`, or `down` and `rented` (broken while on hire).

#### Important notes

- **Do not store** engine hours, fuel, GPS, or idle hours here — those belong in `telemetry`.
- `current_site_id` / `current_operator_id` enable fast dashboard queries without scanning `rentals` or `telemetry`.
- On checkout/return, update these pointers **and** write/close a `rentals` row in the same transaction.
- `updated_at` reflects master-record changes, not sensor time (`telemetry.timestamp`).

#### Suggested indexes

| Index | Type | Purpose |
|---|---|---|
| `serial_number` | UNIQUE | Machine identity |
| `current_site_id` | B-tree | Site dashboard |
| `current_status` | B-tree | KPI status cards |
| `rental_status` | B-tree | Rental state filters |
| `machine_type` | B-tree | Fleet mix / demand analytics |

---

## 5. Operational data tables

---

### 5.1 `rentals`

**Layer:** Operational Data

#### Purpose

Stores every rental transaction: checkout, expected return, actual return, and commercial status. This is the **history of assignments**. Supports overdue detection, utilization by site, demand forecasting, and Return Machine / Extend Rental recommendations.

#### Columns

| Column | PostgreSQL data type | Nullable | Description |
|---|---|---|---|
| `rental_id` | `INTEGER` | No | Surrogate primary key |
| `asset_id` | `INTEGER` | No | Machine being rented |
| `site_id` | `INTEGER` | No | Site the machine is rented to |
| `operator_id` | `INTEGER` | Yes | Operator at checkout; null triggers Missing Operator alerts |
| `checkout_time` | `TIMESTAMPTZ` | No | When machine was assigned |
| `expected_return` | `TIMESTAMPTZ` | No | Contracted or planned return time |
| `actual_return` | `TIMESTAMPTZ` | Yes | Null while open; set on return |
| `rental_status` | `VARCHAR(30)` | No | Lifecycle of this transaction |

#### Primary key

| Column |
|---|
| `rental_id` |

#### Foreign keys

| Column | References | On delete | On update |
|---|---|---|---|
| `asset_id` | `assets.asset_id` | `RESTRICT` | `CASCADE` |
| `site_id` | `sites.site_id` | `RESTRICT` | `CASCADE` |
| `operator_id` | `operators.operator_id` | `SET NULL` | `CASCADE` |

`RESTRICT` on asset/site preserves rental history required for AI and audit.

#### Relationships

| Direction | Related table | Via | Cardinality |
|---|---|---|---|
| Child of | `assets` | `asset_id` | N rentals : 1 asset |
| Child of | `sites` | `site_id` | N rentals : 1 site |
| Child of | `operators` | `operator_id` (optional) | N rentals : 1 operator |

Rentals do **not** own telemetry, alerts, or recommendations — those belong to the asset.

#### Allowed enum / status values

**`rental_status`**

| Value | Meaning |
|---|---|
| `active` | Machine is currently out |
| `extended` | Expected return was pushed forward |
| `returned` | Closed normally |
| `overdue` | `expected_return` passed; `actual_return` still null |
| `cancelled` | Checkout reversed before productive use |

#### Important notes

- Business rule: at most **one** `active` or `overdue` rental per asset at a time (enforce in application logic).
- Overdue detection: `rental_status = overdue` OR (`actual_return` IS NULL AND `expected_return` < now).
- `expected_return` vs `actual_return` drives extend/return recommendations.

#### Suggested indexes

| Index | Type | Purpose |
|---|---|---|
| `(asset_id, checkout_time DESC)` | Composite B-tree | Asset rental history |
| `(site_id, checkout_time)` | Composite B-tree | Site demand analytics |
| `rental_status` | B-tree | Open / overdue dashboard lists |

---

### 5.2 `telemetry`

**Layer:** Operational Data — **append-only**

#### Purpose

Stores **historical** machine telemetry. Every row is one sensor reading at one point in time. A single machine may have thousands to millions of rows. Raw material for utilization, idle analysis, anomaly detection, fuel trends, and forecasting.

#### Columns

| Column | PostgreSQL data type | Nullable | Description |
|---|---|---|---|
| `telemetry_id` | `BIGINT` | No | Surrogate primary key (`BIGINT` — unbounded growth) |
| `asset_id` | `INTEGER` | No | Machine that produced the reading |
| `timestamp` | `TIMESTAMPTZ` | No | Sensor capture time (preferred) or ingest time |
| `engine_hours` | `NUMERIC(12, 2)` | Yes | Cumulative engine hours at this reading |
| `idle_hours` | `NUMERIC(12, 2)` | Yes | Cumulative idle hours at this reading |
| `runtime_hours` | `NUMERIC(12, 2)` | Yes | Cumulative productive hours at this reading |
| `fuel_level` | `NUMERIC(5, 2)` | Yes | Fuel percent remaining (0.00–100.00) |
| `latitude` | `DOUBLE PRECISION` | Yes | Machine GPS latitude |
| `longitude` | `DOUBLE PRECISION` | Yes | Machine GPS longitude |
| `engine_status` | `VARCHAR(30)` | Yes | Engine state at this reading |

#### Primary key

| Column |
|---|
| `telemetry_id` |

#### Foreign keys

| Column | References | On delete | On update |
|---|---|---|---|
| `asset_id` | `assets.asset_id` | `CASCADE` | `CASCADE` |

`CASCADE` keeps hackathon teardown simple. Production systems may later switch to `RESTRICT` with archival.

#### Relationships

| Direction | Related table | Via | Cardinality |
|---|---|---|---|
| Child of | `assets` | `asset_id` | N readings : 1 asset |

No FK to `rentals`, `sites`, or `operators`. Site/operator at reading time is inferred by joining `rentals` where `timestamp` falls between `checkout_time` and `actual_return` (accurate), or via `assets` current pointers (approximate).

#### Allowed enum / status values

**`engine_status`**

| Value | Meaning |
|---|---|
| `on` | Engine running |
| `off` | Engine stopped |
| `idle` | Running but not under load |
| `fault` | Diagnostic / fault state |

#### Important notes

- **Append-only.** Never update rows in place except to correct ingestion errors.
- `engine_hours`, `idle_hours`, `runtime_hours` are **cumulative counters** — idle in a window = delta between two readings.
- Excess idle: compare idle delta vs runtime delta over a time window.
- Low fuel: `fuel_level` below threshold (e.g. 15) on latest row per asset.
- Do **not** add `site_id` here — keep the table narrow; volume is the enemy.
- Optional: partition by `timestamp` (monthly) for large datasets.

#### Suggested indexes

| Index | Type | Purpose |
|---|---|---|
| `(asset_id, timestamp DESC)` | Composite B-tree | Latest reading + time-range charts |
| `(asset_id, timestamp)` | UNIQUE (optional) | Prevent duplicate ingest |

---

### 5.3 `maintenance`

**Layer:** Operational Data

#### Purpose

Stores planned and completed maintenance against a machine. Serves as an operational work-order log and as context data for the recommendation engine ("Maintenance Required", downtime risk, estimated hours).

#### Columns

| Column | PostgreSQL data type | Nullable | Description |
|---|---|---|---|
| `maintenance_id` | `INTEGER` | No | Surrogate primary key |
| `asset_id` | `INTEGER` | No | Machine under service |
| `maintenance_type` | `VARCHAR(50)` | No | Kind of work |
| `issue_description` | `TEXT` | No | What is wrong or planned |
| `priority` | `VARCHAR(20)` | No | Scheduling urgency |
| `status` | `VARCHAR(30)` | No | Work-order lifecycle |
| `scheduled_date` | `DATE` | Yes | Planned service date; null if emergency |
| `completed_date` | `DATE` | Yes | Actual completion; null until done |
| `technician` | `VARCHAR(150)` | Yes | Technician display name |
| `estimated_hours` | `NUMERIC(8, 2)` | Yes | Planned labour hours |
| `remarks` | `TEXT` | Yes | Notes, parts used, follow-up |

#### Primary key

| Column |
|---|
| `maintenance_id` |

#### Foreign keys

| Column | References | On delete | On update |
|---|---|---|---|
| `asset_id` | `assets.asset_id` | `RESTRICT` | `CASCADE` |

Maintenance history must not be erased when experimenting with assets.

#### Relationships

| Direction | Related table | Via | Cardinality |
|---|---|---|---|
| Child of | `assets` | `asset_id` | N records : 1 asset |
| Logical | `alerts` | `asset_id` + time window | Maintenance Due alerts |
| Logical | `recommendations` | `asset_id` + time window | Maintenance Required recommendations |

No direct FK between maintenance and alerts/recommendations — AI and humans create records independently.

#### Allowed enum / status values

**`maintenance_type`**

| Value | Meaning |
|---|---|
| `preventive` | Scheduled service by hours/calendar |
| `corrective` | Repair after a fault |
| `inspection` | Check only |
| `overhaul` | Major rebuild |
| `recall` | Manufacturer campaign |

**`priority`**

`low` · `medium` · `high` · `critical`

**`status`**

| Value | Meaning |
|---|---|
| `open` | Logged; not yet scheduled |
| `scheduled` | Date assigned |
| `in_progress` | Being worked |
| `completed` | Closed successfully |
| `deferred` | Intentionally postponed |
| `cancelled` | Will not be done |

#### Important notes

- Maintenance Due alert: `status` IN (`open`, `scheduled`) AND `scheduled_date` <= today, or engine hours from latest telemetry exceed service interval.
- `technician` is a name field, not a FK to `users` (may map to `users.role = technician` later).
- `estimated_hours` supports cost/downtime estimates in `recommendations.estimated_cost_saving`.

#### Suggested indexes

| Index | Type | Purpose |
|---|---|---|
| `(asset_id, scheduled_date)` | Composite B-tree | Due lists per machine |
| `(status, priority)` | Composite B-tree | Workshop queue |

---

## 6. Intelligence data tables

---

### 6.1 `alerts`

**Layer:** Intelligence Data

#### Purpose

Stores operational alerts generated by rules or models. Alerts are **events the manager should see now**. Distinct from recommendations: an alert says *something is wrong*; a recommendation says *here is what to do*.

**Example types:** Excess Idle · Missing Operator · Overdue Rental · Maintenance Due · Low Fuel

#### Columns

| Column | PostgreSQL data type | Nullable | Description |
|---|---|---|---|
| `alert_id` | `INTEGER` | No | Surrogate primary key |
| `asset_id` | `INTEGER` | No | Machine the alert is about |
| `alert_type` | `VARCHAR(50)` | No | Classifier for grouping and filters |
| `severity` | `VARCHAR(20)` | No | UI urgency level |
| `description` | `TEXT` | No | Human-readable explanation with context |
| `status` | `VARCHAR(30)` | No | Whether alert is still live |
| `generated_time` | `TIMESTAMPTZ` | No | When system created the alert; default UTC now |
| `resolved_time` | `TIMESTAMPTZ` | Yes | When cleared; null if still open |

#### Primary key

| Column |
|---|
| `alert_id` |

#### Foreign keys

| Column | References | On delete | On update |
|---|---|---|---|
| `asset_id` | `assets.asset_id` | `CASCADE` | `CASCADE` |

Alerts are derived events; they may be removed with the asset.

#### Relationships

| Direction | Related table | Via | Cardinality |
|---|---|---|---|
| Child of | `assets` | `asset_id` | N alerts : 1 asset |
| Logical input | `telemetry`, `rentals`, `maintenance` | Read by detection jobs | No FK |

One alert may yield zero, one, or several recommendations (no FK between them in v1).

#### Allowed enum / status values

**`alert_type`**

| Value | Display label |
|---|---|
| `excess_idle` | Excess Idle |
| `missing_operator` | Missing Operator |
| `overdue_rental` | Overdue Rental |
| `maintenance_due` | Maintenance Due |
| `low_fuel` | Low Fuel |
| `engine_fault` | Engine fault from telemetry |
| `geofence_deviation` | Machine GPS far from assigned site |

**`severity`**

`info` · `warning` · `high` · `critical`

**`status`**

| Value | Meaning |
|---|---|
| `open` | Visible on live alert feed |
| `acknowledged` | Seen by manager; not yet fixed |
| `resolved` | Condition cleared |
| `dismissed` | Judged not actionable |

#### Important notes

- Deduplicate before insert: check for existing `open` or `acknowledged` row with same `(asset_id, alert_type)`.
- Set `resolved_time` whenever `status` becomes `resolved` or `dismissed`.
- Detection jobs **write** here; the alerts UI **reads** here only.

#### Suggested indexes

| Index | Type | Purpose |
|---|---|---|
| `(status, severity, generated_time DESC)` | Composite B-tree | Alert feed panel |
| `(asset_id, generated_time DESC)` | Composite B-tree | Asset detail alert history |

---

### 6.2 `recommendations`

**Layer:** Intelligence Data

#### Purpose

Stores AI-generated recommended actions. Decision-support output: a persisted proposal of what should happen next, with reason, confidence, and estimated saving.

**Example types:** Move Machine · Return Machine · Assign Operator · Extend Rental · Maintenance Required

#### Columns

| Column | PostgreSQL data type | Nullable | Description |
|---|---|---|---|
| `recommendation_id` | `INTEGER` | No | Surrogate primary key |
| `asset_id` | `INTEGER` | No | Machine the action refers to |
| `recommendation_type` | `VARCHAR(50)` | No | Action class |
| `reason` | `TEXT` | No | Explainable rationale shown to manager |
| `confidence_score` | `NUMERIC(5, 4)` | No | Model confidence (0.0000–1.0000) |
| `estimated_cost_saving` | `NUMERIC(12, 2)` | Yes | Estimated saving if action taken (e.g. USD) |
| `recommendation_time` | `TIMESTAMPTZ` | No | When engine produced this; default UTC now |
| `recommendation_status` | `VARCHAR(30)` | No | Lifecycle until manager acts or it expires |

#### Primary key

| Column |
|---|
| `recommendation_id` |

#### Foreign keys

| Column | References | On delete | On update |
|---|---|---|---|
| `asset_id` | `assets.asset_id` | `RESTRICT` | `CASCADE` |

Recommendations feed `decision_log` and model evaluation — do not delete assets with recommendation history.

#### Relationships

| Direction | Related table | Via | Cardinality |
|---|---|---|---|
| Child of | `assets` | `asset_id` | N recommendations : 1 asset |
| Parent of | `decision_log` | `decision_log.recommendation_id` | 1 recommendation : N decisions |
| Logical input | `telemetry`, `rentals`, `maintenance`, `alerts`, `operators` | Read by engine | No FK |

#### Allowed enum / status values

**`recommendation_type`**

| Value | Meaning |
|---|---|
| `move_machine` | Relocate to higher-demand or nearer site |
| `return_machine` | End rental; machine underused or needed elsewhere |
| `assign_operator` | Pair available operator with unmanned asset |
| `extend_rental` | Keep machine on site past `expected_return` |
| `maintenance_required` | Take machine out of production for service |

**`recommendation_status`**

| Value | Meaning |
|---|---|
| `pending` | Waiting for manager |
| `accepted` | Manager agreed (see `decision_log`) |
| `rejected` | Manager declined |
| `expired` | Stale because situation changed |
| `executed` | Accepted and operational change applied |

#### Important notes

- Persist recommendations for stable explanations, fast action queue, and accept/reject analytics.
- After a decision, update `recommendation_status` **and** insert `decision_log` in the same transaction.
- `recommendation_status` is the denormalized current outcome; `decision_log` is the audit of who did what.

#### Suggested indexes

| Index | Type | Purpose |
|---|---|---|
| `(recommendation_status, recommendation_time DESC)` | Composite B-tree | Pending action queue |
| `(asset_id, recommendation_time DESC)` | Composite B-tree | Asset recommendation history |

---

### 6.3 `decision_log`

**Layer:** Intelligence Data

#### Purpose

Stores the fleet manager's decision after an AI recommendation. Answers: was the recommendation accepted or rejected, by whom, when, and with what comment? Closed-loop learning and accountability layer — **separate from `recommendations`** so advice and human action are independently queryable.

#### Columns

| Column | PostgreSQL data type | Nullable | Description |
|---|---|---|---|
| `decision_id` | `INTEGER` | No | Surrogate primary key |
| `recommendation_id` | `INTEGER` | No | AI recommendation being acted on |
| `manager_name` | `VARCHAR(150)` | No | Display name of decision maker |
| `action_taken` | `VARCHAR(50)` | No | Outcome of the decision |
| `decision_time` | `TIMESTAMPTZ` | No | When manager submitted; default UTC now |
| `remarks` | `TEXT` | Yes | Why accepted, rejected, or modified |

#### Primary key

| Column |
|---|
| `decision_id` |

#### Foreign keys

| Column | References | On delete | On update |
|---|---|---|---|
| `recommendation_id` | `recommendations.recommendation_id` | `RESTRICT` | `CASCADE` |

Never delete a recommendation that has a decision attached.

#### Relationships

| Direction | Related table | Via | Cardinality |
|---|---|---|---|
| Child of | `recommendations` | `recommendation_id` | N decisions : 1 recommendation |
| Logical | `users` | `manager_name` | Name snapshot; no FK in v1 |

Expected cardinality is 1:1 for the hackathon; 1:N allows follow-up corrections.

#### Allowed enum / status values

**`action_taken`**

| Value | Meaning |
|---|---|
| `accepted` | Follow recommendation as stated |
| `rejected` | Do not follow it |
| `modified` | Follow a variant (details in `remarks`) |
| `deferred` | Decide later; recommendation may stay pending |

#### Important notes

- Inserting `accepted` / `rejected` / `modified` must update `recommendations.recommendation_status` in the same transaction.
- `manager_name` is a snapshot so the log remains readable if accounts change. Add `manager_user_id` → `users.user_id` in a later version.
- `remarks` on rejected items is qualitative feedback for the recommendation engine team.

#### Suggested indexes

| Index | Type | Purpose |
|---|---|---|
| `recommendation_id` | B-tree | Join from recommendation |
| `decision_time DESC` | B-tree | Decision timeline on dashboard |

---

## 7. Foreign-key relationship matrix

All foreign keys in the schema, verified for consistency.

| Child table | FK column | Parent table | Parent column | On delete | On update |
|---|---|---|---|---|---|
| `operators` | `assigned_site` | `sites` | `site_id` | `SET NULL` | `CASCADE` |
| `assets` | `current_site_id` | `sites` | `site_id` | `SET NULL` | `CASCADE` |
| `assets` | `current_operator_id` | `operators` | `operator_id` | `SET NULL` | `CASCADE` |
| `rentals` | `asset_id` | `assets` | `asset_id` | `RESTRICT` | `CASCADE` |
| `rentals` | `site_id` | `sites` | `site_id` | `RESTRICT` | `CASCADE` |
| `rentals` | `operator_id` | `operators` | `operator_id` | `SET NULL` | `CASCADE` |
| `telemetry` | `asset_id` | `assets` | `asset_id` | `CASCADE` | `CASCADE` |
| `maintenance` | `asset_id` | `assets` | `asset_id` | `RESTRICT` | `CASCADE` |
| `alerts` | `asset_id` | `assets` | `asset_id` | `CASCADE` | `CASCADE` |
| `recommendations` | `asset_id` | `assets` | `asset_id` | `RESTRICT` | `CASCADE` |
| `decision_log` | `recommendation_id` | `recommendations` | `recommendation_id` | `RESTRICT` | `CASCADE` |

**Consistency rules verified:**

- All FK column names follow `<table_singular>_id` convention.
- Every FK references an existing primary key on the parent table.
- `users` has no outgoing or incoming FKs in v1.
- `assets` is referenced by six child tables — the hub is intact.
- `telemetry` references only `assets` — append-only time-series is isolated.
- `decision_log` references only `recommendations` — decision tracking is isolated from alerts.
- Delete behaviour is intentional: history tables (`rentals`, `maintenance`, `recommendations`, `decision_log`) use `RESTRICT`; derived/event tables (`telemetry`, `alerts`) use `CASCADE`; current pointers (`assets`, `operators`) use `SET NULL`.

---

## 8. Cardinality summary

| Parent | Child | Cardinality | Child required? |
|---|---|---|---|
| `sites` | `operators` | 1 : N | No |
| `sites` | `assets` (current) | 1 : N | No |
| `sites` | `rentals` | 1 : N | No |
| `operators` | `assets` (current) | 1 : N | No |
| `operators` | `rentals` | 1 : N | No |
| `assets` | `rentals` | 1 : N | No |
| `assets` | `telemetry` | 1 : N (very large N) | No |
| `assets` | `maintenance` | 1 : N | No |
| `assets` | `alerts` | 1 : N | No |
| `assets` | `recommendations` | 1 : N | No |
| `recommendations` | `decision_log` | 1 : N | No |
| `users` | — | — | Auth only |

---

## 9. Relationship diagrams

### Hub-and-spoke (primary view)

```
Users
  (login — no FK edges in v1)

Sites ──────────── Operators
  │                    │
  └─────────┬──────────┘
            ▼
         Assets  ◄── FLEET HUB
            │
            ├── Rentals          (Operational)
            ├── Telemetry        (Operational — append-only)
            ├── Maintenance      (Operational)
            ├── Alerts           (Intelligence)
            └── Recommendations  (Intelligence)
                    │
                    └── Decision Log  (Intelligence)
```

### Layer view

```
┌─────────────────────────────────────────────────────────┐
│  MASTER DATA                                            │
│  users · sites · operators · assets (hub)               │
└──────────────────────────┬──────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────┐
│  OPERATIONAL DATA                                       │
│  rentals · telemetry (append-only) · maintenance        │
└──────────────────────────┬──────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────┐
│  INTELLIGENCE DATA                                      │
│  alerts · recommendations · decision_log                  │
└─────────────────────────────────────────────────────────┘
```

### Detailed FK flow

```
sites
  │
  ├── operators.assigned_site
  ├── assets.current_site_id
  └── rentals.site_id

operators
  │
  ├── assets.current_operator_id
  └── rentals.operator_id

assets
  │
  ├── rentals.asset_id
  ├── telemetry.asset_id
  ├── maintenance.asset_id
  ├── alerts.asset_id
  └── recommendations.asset_id
          │
          └── decision_log.recommendation_id
```

---

## 10. Referential integrity and update rules

| Event | Tables affected | Expected behaviour |
|---|---|---|
| **Checkout** | `rentals`, `assets`, `operators` | Insert `rentals` (`rental_status = active`). Set `assets.current_site_id`, `current_operator_id`, `rental_status = rented`. Set operator `availability_status = on_duty` if assigned. |
| **Return** | `rentals`, `assets`, `operators` | Set `rentals.actual_return`, `rental_status = returned`. Clear or retarget asset current pointers. Set `assets.rental_status = available` or `returned`. Set operator `availability_status = available`. |
| **Overdue** | `rentals`, `assets`, `alerts` | Flag rental and asset `rental_status = overdue`. Insert `alerts` row `overdue_rental` if none open. |
| **Telemetry ingest** | `telemetry`, `assets` (optional) | Insert-only into `telemetry`. Optionally refresh `assets.current_status` from latest `engine_status`. Do **not** copy hours/fuel onto `assets`. |
| **Alert generation** | `alerts` | Deduplicate on `(asset_id, alert_type)` where status is `open` or `acknowledged`. |
| **Recommendation generation** | `recommendations` | Write row with `recommendation_status = pending`. Skip duplicate pending row for same asset + type. |
| **Manager decision** | `decision_log`, `recommendations` | Insert `decision_log`. Update `recommendations.recommendation_status` in same transaction. |
| **Decision executed** | `rentals`, `assets`, `operators`, `maintenance` | Apply operational change per accepted recommendation type. |

---

## 11. Design rationale

### Why telemetry is stored separately from assets

| | `assets` | `telemetry` |
|---|---|---|
| Change frequency | Slow (master data) | High (every minute) |
| Row count per machine | 1 | Thousands to millions |
| Purpose | Current assignment snapshot | Historical sensor facts |

If sensor readings lived on `assets`, only the latest snapshot would survive, utilization charts and forecasting would be impossible, and every GPS ping would contend with checkout/return updates on the same row.

Separation enables fast current-state reads from `assets`, honest time-series analytics from `telemetry`, window-based anomaly detection, and future partitioning/archival without touching master data.

Assignment location (`assets.current_site_id`) and physical location (latest `telemetry` GPS) answer different questions and must remain separate.

### Why recommendations are stored instead of recalculated

The recommendation engine reads telemetry trends, rental windows, maintenance backlog, site demand, and alerts. That work is too expensive and unstable to rerun on every dashboard refresh.

| Benefit | Explanation |
|---|---|
| Stable explanations | Manager sees the same `reason` and `confidence_score` they acted on |
| Decision tracking | `decision_log` must point at a specific `recommendation_id` |
| Performance | Action queue = filter on `recommendation_status = pending` |
| Audit | Stakeholders can review what was advised on any date |
| Model quality | Acceptance rate by `recommendation_type` requires persisted rows |
| Idempotency | Jobs skip duplicate pending recommendations |
| Expiry | Rows marked `expired` when the world changes |

Recalculation happens on schedule or on event — the **output** is a stored row, not a throwaway API payload.

### Why `decision_log` is separate from `recommendations`

A recommendation is *what the AI proposed*. A decision is *what the human did*. Keeping them separate allows:

- Multiple decisions on one recommendation (corrections)
- Querying all rejections without filtering mixed status fields
- Measuring AI quality independently of recommendation lifecycle state

---

## 12. How the schema supports product features

### Dashboard (current-state)

| Widget | Tables | Query pattern |
|---|---|---|
| Fleet counts by status | `assets` | Group by `current_status` / `rental_status` |
| Machines per site | `assets` + `sites` | `current_site_id` |
| Who is operating what | `assets` + `operators` | `current_operator_id` |
| Open / overdue rentals | `rentals` | Filter `rental_status` |
| Live alert badge | `alerts` | Count `status = open` |
| Pending AI actions | `recommendations` | `recommendation_status = pending` |
| Map pins | `sites` + latest `telemetry` | Site centroid vs machine GPS |
| Utilization strip | Latest `telemetry` per asset | Idle vs runtime deltas |

### Alerts (materialized detections)

| Alert type | Reads from | Writes to |
|---|---|---|
| Excess Idle | `telemetry` idle/runtime deltas | `alerts` (`excess_idle`) |
| Missing Operator | `assets` / `rentals` with null operator | `alerts` (`missing_operator`) |
| Overdue Rental | `rentals.expected_return` vs now | `alerts` (`overdue_rental`) |
| Maintenance Due | `maintenance` + `telemetry.engine_hours` | `alerts` (`maintenance_due`) |
| Low Fuel | Latest `telemetry.fuel_level` | `alerts` (`low_fuel`) |

### Analytics (historical)

- Utilization / idle ratios: windowed deltas on `telemetry`
- Rental duration / overdue rate: `rentals` checkout / expected / actual
- Demand by site and machine type: `rentals` × `assets` × `sites`
- Maintenance burden: `maintenance.estimated_hours`, completion lag
- Alert frequency: `alerts` by `alert_type` and `severity`
- Recommendation yield: `recommendations.estimated_cost_saving` vs `decision_log.action_taken`

### AI forecasting (feature sources)

| Forecast | Feature tables |
|---|---|
| Demand for model at site | `rentals` + `assets.machine_type` + `sites` |
| Likely idle / underuse | `telemetry` idle vs runtime trends |
| Maintenance / downtime risk | `maintenance` + `telemetry.engine_hours` + `alerts` |
| Return vs extend | Open `rentals` window vs site utilization |

### Recommendation engine (read-many, write-one)

1. Read `assets`, recent `telemetry`, open `rentals`, `operators` availability, `maintenance`, `alerts`
2. Write `recommendations` (type, reason, confidence, estimated saving)

| Recommendation | Typical evidence |
|---|---|
| Move Machine | High idle at site A; unmet demand at site B |
| Return Machine | Active rental but persistent idle in telemetry |
| Assign Operator | Rented asset, null `current_operator_id`, operator `available` at site |
| Extend Rental | High utilization; `expected_return` approaching |
| Maintenance Required | Hours interval due; open high-priority maintenance or fault alert |

### Decision tracking (closed loop)

1. Engine inserts `recommendations` (`pending`)
2. Manager authenticates via `users`
3. Manager records `decision_log` (`accepted` / `rejected` / `modified` / `deferred`)
4. Same transaction updates `recommendations.recommendation_status`
5. If accepted, application updates `rentals`, `assets`, `operators`, or `maintenance`

---

## 13. Implementation guidance (no code)

When creating SQLAlchemy models from this document:

1. Map every table and column name **exactly** as specified.
2. Use `Numeric` for hours, fuel, scores, and money — not `Float`.
3. Use `DateTime(timezone=True)` for all `TIMESTAMPTZ` columns.
4. Use `BigInteger` for `telemetry.telemetry_id`.
5. Define `relationship()` on both sides of each FK in sections 4–6.
6. Do **not** add telemetry columns to the Asset model.
7. Treat `users` as standalone until `user_id` is added to `decision_log`.
8. Encode allowed values as Python `enum.Enum` or documented constants with check constraints.
9. Default `created_at`, `generated_time`, `recommendation_time`, and `decision_time` to UTC now at insert.
10. Application code must maintain `assets.updated_at` on every change.

---

## 14. Out of scope

The following are intentionally **not** tables in this version:

- Parts / inventory
- Invoices and rental rates
- ML feature store or model-run registry
- Notifications (email/SMS) outbox
- GPS geofence polygons
- `users.user_id` FK on `decision_log` and `sites`

They can be added without breaking the hub-and-spoke design around `assets`.

---

*End of database design document. This specification is sufficient to implement SQLAlchemy models and Alembic migrations without further schema invention.*
