CREATE TABLE "devices" (
  "id" uuid PRIMARY KEY,
  "name" varchar NOT NULL,
  "firmware_version" varchar,
  "location" varchar,
  "installed_at" timestamp,
  "created_at" timestamp NOT NULL DEFAULT 'now',
  "is_activated" bool NOT NULL DEFAULT true
);

CREATE TABLE "sensors" (
  "id" uuid PRIMARY KEY,
  "name" varchar NOT NULL,
  "device_id" uuid NOT NULL,
  "sensor_type" varchar,
  "product_code" varchar,
  "vendor" varchar,
  "description" text
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
  "is_activated" bool NOT NULL DEFAULT true,
  "deactivated_by" uuid,
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

CREATE INDEX ON "device_positions" ("time");

CREATE INDEX ON "telemetry" ("time");

CREATE INDEX idx_users_devices_current 
ON "users_devices" ("device_id") 
WHERE "removed_at" IS NULL;


ALTER TABLE "mods_devices" ADD FOREIGN KEY ("mod_id") REFERENCES "users" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "mods_devices" ADD FOREIGN KEY ("device_id") REFERENCES "devices" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "mods_devices" ADD FOREIGN KEY ("granted_by") REFERENCES "users" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "roles" ADD FOREIGN KEY ("user_id") REFERENCES "users" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "device_management_logs" ADD FOREIGN KEY ("assigned_by") REFERENCES "users" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "image_capture" ADD FOREIGN KEY ("device_id") REFERENCES "devices" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "roles" ADD FOREIGN KEY ("id") REFERENCES "permissions" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "sensors" ADD FOREIGN KEY ("device_id") REFERENCES "devices" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "device_management_logs" ADD FOREIGN KEY ("removed_by") REFERENCES "users" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "mods_devices" ADD FOREIGN KEY ("revoked_by") REFERENCES "users" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "device_positions" ADD FOREIGN KEY ("device_id") REFERENCES "devices" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "telemetry" ADD FOREIGN KEY ("sensor_id") REFERENCES "sensors" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "image_analysis" ADD FOREIGN KEY ("image_id") REFERENCES "image_capture" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "device_management_logs" ADD FOREIGN KEY ("user_id") REFERENCES "users" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "device_management_logs" ADD FOREIGN KEY ("device_id") REFERENCES "devices" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "users" ADD FOREIGN KEY ("deactivated_by") REFERENCES "users" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "users" ADD FOREIGN KEY ("created_by") REFERENCES "users" ("id") DEFERRABLE INITIALLY IMMEDIATE;







