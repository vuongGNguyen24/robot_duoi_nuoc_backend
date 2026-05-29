CREATE TABLE "devices" (
  "id" uuid PRIMARY KEY,
  "name" varchar UNIQUE NOT NULL,
  "firmware_version" varchar,
  "location" varchar,
  "installed_at" timestamp,
  "created_at" timestamp NOT NULL DEFAULT 'now',
  "is_locked" bool NOT NULL DEFAULT false,
  "locked_at" datetime,
  "notes" text
);

CREATE TABLE "multi_sensors" (
  "id" uuid PRIMARY KEY,
  "device_id" uuid NOT NULL,
  "name" varchar NOT NULL,
  "locked_at" datetime,
  "product_code" varchar,
  "vendor" varchar,
  "description" text
);

CREATE TABLE "sensors" (
  "id" uuid PRIMARY KEY,
  "multi_sensor_id" uuid NOT NULL,
  "name" varchar,
  "sensor_type" varchar,
  "description" text,
  "min_threshold" float,
  "max_threshold" float
);

CREATE TABLE "device_positions" (
  "device_id" uuid,
  "time" timestamp NOT NULL DEFAULT 'now',
  "location" "geography(Point)",
  PRIMARY KEY ("device_id", "time")
);

CREATE TABLE "telemetry" (
  "id" uuid,
  "sensor_id" uuid NOT NULL,
  "time" timestamp NOT NULL DEFAULT 'now',
  "unit" varchar NOT NULL,
  "value" float NOT NULL,
  "quality_flag" tinyint,
  PRIMARY KEY ("id")
);

CREATE TABLE "image_capture" (
  "id" uuid PRIMARY KEY,
  "device_id" uuid NOT NULL,
  "captured_at" timestamp NOT NULL DEFAULT 'now',
  "image_url" varchar NOT NULL,
  "file_size" int,
  "width" smallint,
  "height" smallint
);

CREATE TABLE "permissions" (
  "id" uuid,
  "name" varchar,
  "description" text
);

CREATE TABLE "image_analysis" (
  "id" uuid PRIMARY KEY,
  "image_id" uuid NOT NULL,
  "result" json NOT NULL,
  "confidence" float,
  "processed_at" timestamp NOT NULL DEFAULT 'now'
);

CREATE TABLE "users" (
  "id" uuid PRIMARY KEY,
  "username" varchar UNIQUE NOT NULL,
  "password_hash" varchar NOT NULL,
  "role" varchar NOT NULL,
  "phone_number" varchar UNIQUE NOT NULL,
  "created_at" timestamp NOT NULL DEFAULT 'now',
  "created_by" uuid,
  "is_locked" bool NOT NULL DEFAULT false,
  "locked_by" uuid,
  "locked_at" datetime,
  "notes" text
);

CREATE TABLE "roles" (
  "id" uuid,
  "user_id" uuid NOT NULL,
  "permission_id" uuid NOT NULL
);

CREATE TABLE "mods_devices" (
  "id" uuid PRIMARY KEY,
  "mod_id" uuid NOT NULL,
  "device_id" uuid NOT NULL,
  "granted_at" timestamp NOT NULL DEFAULT 'now',
  "granted_by" uuid NOT NULL,
  "revoked_at" timestamp,
  "revoked_by" uuid,
  "notes" text
);

CREATE TABLE "device_management_logs" (
  "id" uuid PRIMARY KEY,
  "user_id" uuid NOT NULL,
  "device_id" uuid NOT NULL,
  "create_at" timestamp NOT NULL DEFAULT 'now',
  "assigned_by" uuid NOT NULL,
  "removed_at" timestamp,
  "removed_by" uuid,
  "notes" text
);

CREATE TABLE "actuators" (
  "id" uuid PRIMARY KEY,
  "device_id" uuid NOT NULL,
  "name" varchar NOT NULL,
  "status" json
);

CREATE TABLE "actuator_commands" (
  "id" uuid PRIMARY KEY,
  "actuator_id" uuid NOT NULL,
  "comment" varchar,
  "send_time" datetime NOT NULL DEFAULT 'now',
  "response_time" datetime
);

CREATE TABLE "alerts" (
  "id" uuid PRIMARY KEY,
  "telemetry_id" uuid NOT NULL,
  "state" varchar NOT NULL DEFAULT 'to do',
  "end_time" datetime
);

CREATE INDEX ON "device_positions" ("time");

CREATE INDEX ON "telemetry" ("time");

ALTER TABLE "mods_devices" ADD FOREIGN KEY ("mod_id") REFERENCES "users" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "mods_devices" ADD FOREIGN KEY ("device_id") REFERENCES "devices" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "mods_devices" ADD FOREIGN KEY ("granted_by") REFERENCES "users" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "roles" ADD FOREIGN KEY ("user_id") REFERENCES "users" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "device_management_logs" ADD FOREIGN KEY ("assigned_by") REFERENCES "users" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "image_capture" ADD FOREIGN KEY ("device_id") REFERENCES "devices" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "roles" ADD FOREIGN KEY ("id") REFERENCES "permissions" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "multi_sensors" ADD FOREIGN KEY ("device_id") REFERENCES "devices" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "sensors" ADD FOREIGN KEY ("multi_sensor_id") REFERENCES "multi_sensors" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "device_management_logs" ADD FOREIGN KEY ("removed_by") REFERENCES "users" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "mods_devices" ADD FOREIGN KEY ("revoked_by") REFERENCES "users" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "device_positions" ADD FOREIGN KEY ("device_id") REFERENCES "devices" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "telemetry" ADD FOREIGN KEY ("sensor_id") REFERENCES "sensors" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "image_analysis" ADD FOREIGN KEY ("image_id") REFERENCES "image_capture" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "device_management_logs" ADD FOREIGN KEY ("user_id") REFERENCES "users" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "device_management_logs" ADD FOREIGN KEY ("device_id") REFERENCES "devices" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "users" ADD FOREIGN KEY ("locked_by") REFERENCES "users" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "users" ADD FOREIGN KEY ("created_by") REFERENCES "users" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "telemetry" ADD FOREIGN KEY ("id") REFERENCES "alerts" ("telemetry_id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "actuators" ADD FOREIGN KEY ("device_id") REFERENCES "devices" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "actuator_commands" ADD FOREIGN KEY ("actuator_id") REFERENCES "actuators" ("id") DEFERRABLE INITIALLY IMMEDIATE;
