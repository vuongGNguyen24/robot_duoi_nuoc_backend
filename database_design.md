# Robot Telemetry System -- Database Design (PoC)

## 1. Overview

This document describes the database design used for the **Robot
Telemetry System Proof‑of‑Concept (PoC)** implemented in PostgreSQL.

The database stores telemetry and operational data produced by robotic
devices, including:

-   robot metadata
-   sensor measurements
-   robot position tracking
-   image capture
-   image analysis results

The design prioritizes simplicity and rapid development suitable for a
PoC environment.

The database currently models:

1.  Device metadata
2.  Sensor measurements (time-series)
3.  Robot position tracking
4.  Image capture and AI analysis
5.  User accounts

------------------------------------------------------------------------

# 2. PoC Design Assumptions

This database intentionally simplifies several aspects of the system.

### Hardware assumptions

-   Only one type of robot device
-   Sensors are few in number
-   Sensor types are not managed through a catalog table

### AI pipeline assumptions

-   Only 1--2 AI models
-   Model versioning is not required
-   AI results are stored directly in `image_analysis`

### Dashboard assumptions

-   Dashboard is hardcoded in the application
-   Each user owns exactly one dashboard
-   Each dashboard visualizes only one robot device

Therefore the database does not include:

-   dashboard configuration tables
-   model management tables
-   sensor type catalogs

These can be introduced later when the system evolves beyond PoC.

------------------------------------------------------------------------

# 3. Table Descriptions

## users

Stores application user accounts.

  column          type        description
  --------------- ----------- -----------------------------------
  id              uuid        unique identifier for user
  username        varchar     user login username
  password_hash   varchar     hashed password
  role            varchar     user role (admin/moderator/viewer)
  phone_number    varchar     user phone number
  created_at      timestamp   account creation time
  created_by      uuid        user who created this account
  is_locked       bool        whether the account is locked
  locked_at       timestamp   time when the account was locked
  locked_by       uuid        user who locked the account
  notes           text        optional notes about the account (reason for deactivation, ...)

Each user may control multiple devices via `device_management_logs`.

------------------------------------------------------------------------

## device_management_logs

Intermediary table linking users to devices (Many-to-Many).
When a new management permission is created between a user and a device, a new record is added here.

  column          type        description
  --------------- ----------- -----------------------------------
  id              uuid        unique log identifier
  user_id         uuid        user assigned to the device
  device_id       uuid        device managed by the user
  create_at       timestamp   time the assignment was created
  assigned_by     uuid        user who assigned the permission
  removed_at      timestamp   time the assignment was removed
  removed_by      uuid        user who removed the permission
  notes           text        optional notes about the assignment

Relationship:

users ↔ devices (M:N)

------------------------------------------------------------------------

## devices

Represents robotic devices registered in the system.

  column             type        description
  ------------------ ----------- -------------------------------
  id                 uuid        unique device identifier
  name               varchar     human readable device name
  device_type        varchar     device type (robot/telemetry_base_station)
  firmware_version   varchar     firmware version installed
  location           varchar     textual installation location
  installed_at       timestamp   time device was deployed
  created_at         timestamp   record creation time
  is_locked       bool        whether the device is locked

Relationship:

devices ↔ users (M:N) via device_management_logs

A device can be managed by multiple users, and a user can manage multiple devices.

------------------------------------------------------------------------

## mods_devices

Association table for managing device access by moderators and admins.
One moderator or admin can be assigned multiple devices, and one device can be managed by multiple moderators or admins.

  column          type        description
  --------------- ----------- -----------------------------------
  id              uuid        unique log identifier
  mod_id          uuid        moderator/admin assigned to the device
  device_id       uuid        device managed by the moderator/admin
  granted_at      timestamp   time the assignment was created
  granted_by      uuid        user who granted the permission
  revoked_at      timestamp   time the assignment was revoked
  revoked_by      uuid        user who revoked the permission
  notes           text        optional notes about the assignment

Relationship:

users ↔ devices (M:N) via mods_devices

------------------------------------------------------------------------

## sensors

Represents physical sensors attached to a robot.

  column        type      description
  ------------- --------- ------------------------------------
  id            uuid      unique sensor identifier
  name          varchar   sensor name
  device_id     uuid      robot device containing the sensor
  sensor_type   varchar   sensor type (temperature/ph/turbidity/dissolved_oxygen/water_level/multi_parameter/camera)
  description   text      optional description

Examples of sensors:

-   temperature
-   pH
-   turbidity
-   dissolved oxygen

Relationship:

devices → sensors (1:N)

One robot device may contain multiple sensors.

------------------------------------------------------------------------

## device_positions

Stores robot location over time.

  column      type               description
  ----------- ------------------ ----------------------------
  device_id   uuid               robot identifier
  time        timestamp          time position was recorded
  location    geography(Point)   geographic coordinates

Primary key:

(device_id, time)

Typical update frequency in PoC: \~2 minutes.

Relationship:

devices → device_positions (1:N)

This table enables:

-   robot trajectory visualization
-   map heatmap rendering
-   spatial queries

------------------------------------------------------------------------

## telemetry

Stores time-series measurements from sensors (including unit and id because of a sensor can measure multiple water quality parameters at the same time).

  column           type        description
  ---------------- ----------- -----------------------------------
  id              uuid         unique identifier for the measurement
  sensor_id        uuid        sensor generating the measurement
  time             timestamp   time measurement was taken
  value            float       numeric measurement value
  unit          varchar   measurement unit
  quality_flag     int         optional data quality indicator
  ingestion_time   timestamp   time data entered database

Primary key:

(id)

Relationship:

sensors → telemetry (1:N)

This table is the main telemetry data source for charts and monitoring.

Typical data frequency: \~2 minutes per sensor.

------------------------------------------------------------------------

## image_capture

Stores metadata about images captured by the robot.

  column        type        description
  ------------- ----------- --------------------------
  id            uuid        image identifier
  device_id     uuid        robot capturing image
  captured_at   timestamp   time image was taken
  image_url     varchar     location of stored image
  file_size     int         image file size
  width         int         image width
  height        int         image height

Images themselves are stored externally (object storage, file system, or
cloud storage).

The database stores only image metadata.

Relationship:

devices → image_capture (1:N)

------------------------------------------------------------------------

## image_analysis

Stores AI inference results produced from captured images.

  column         type        description
  -------------- ----------- -----------------------------
  id             uuid        analysis identifier
  image_id       uuid        image analyzed
  result         json        structured AI output
  confidence     float       model confidence score
  processed_at   timestamp   time analysis was generated

Relationship:

image_capture → image_analysis (1:N)

Example result JSON:

{ "objects": \[ { "label": "algae", "confidence": 0.92 } \] }

------------------------------------------------------------------------

# 4. Key Relationships

Core relational structure:

users ↔ device_management_logs ↔ devices
                                    ├── sensors
                                    │   └── telemetry
                                    ├── device_positions
                                    └── image_capture
                                        └── image_analysis

Summary:

  relationship                                     type
  ------------------------------------------------ ------
  users ↔ devices (via device_management_logs)     M:N
  devices → sensors                                1:N
  sensors → telemetry                              1:N
  devices → device_positions                       1:N
  devices → image_capture                          1:N
  image_capture → image_analysis                   1:N

------------------------------------------------------------------------

# 5. Data Flow

## Telemetry pipeline

Robot sensors\
↓\
Robot telemetry service\
↓\
Backend ingestion API\
↓\
telemetry table\
↓\
Dashboard visualization

------------------------------------------------------------------------

## Robot position pipeline

Robot GPS module\
↓\
device_positions\
↓\
Map visualization

------------------------------------------------------------------------

## Image processing pipeline

Robot camera\
↓\
image_capture\
↓\
AI inference service\
↓\
image_analysis

------------------------------------------------------------------------

# 6. Example Queries

## Latest telemetry readings

``` sql
SELECT time, value
FROM telemetry
WHERE sensor_id = :sensor_id
ORDER BY time DESC
LIMIT 100;
```

## Telemetry in a time window

``` sql
SELECT time, value
FROM telemetry
WHERE sensor_id = :sensor_id
AND time BETWEEN :start AND :end
ORDER BY time;
```

## Latest robot position

``` sql
SELECT location
FROM device_positions
WHERE device_id = :device_id
ORDER BY time DESC
LIMIT 1;
```

## Robot trajectory

``` sql
SELECT time, location
FROM device_positions
WHERE device_id = :device_id
AND time BETWEEN :start AND :end
ORDER BY time;
```

## Images captured by robot

``` sql
SELECT id, captured_at, image_url
FROM image_capture
WHERE device_id = :device_id
ORDER BY captured_at DESC;
```

## AI analysis results

``` sql
SELECT result, confidence
FROM image_analysis
WHERE image_id = :image_id;
```

------------------------------------------------------------------------

# 7. Indexes

Two indexes support common queries.

device_positions:

INDEX(device_positions.time)

telemetry:

INDEX(telemetry.time)

------------------------------------------------------------------------

# 8. Future Extensions

Possible improvements for production systems:

-   sensor type catalog
-   AI model registry
-   dashboard configuration tables
-   telemetry partitioning
-   mission / robot path planning tables

These features are intentionally excluded from the PoC to keep the
system simple.
