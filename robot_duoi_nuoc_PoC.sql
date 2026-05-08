CREATE TABLE "devices" (
  "id" uuid PRIMARY KEY,
  "user_id" uuid,
  "name" varchar,
  "device_type" varchar,
  "firmware_version" varchar,
  "location" varchar,
  "installed_at" timestamp,
  "created_at" timestamp
);

CREATE TABLE "sensors" (
  "id" uuid PRIMARY KEY,
  "device_id" uuid NOT NULL,
  "unit" varchar,
  "description" varchar
);

CREATE TABLE "device_positions" (
  "device_id" uuid,
  "time" timestamp,
  "location" "geography(Point)",
  PRIMARY KEY ("device_id", "time")
);

CREATE TABLE "telemetry" (
  "sensor_id" uuid,
  "time" timestamp,
  "value" float,
  "quality_flag" int,
  "ingestion_time" timestamp,
  PRIMARY KEY ("sensor_id", "time")
);

CREATE TABLE "image_capture" (
  "id" uuid PRIMARY KEY,
  "device_id" uuid,
  "captured_at" timestamp,
  "image_url" varchar,
  "file_size" int,
  "width" int,
  "height" int
);

CREATE TABLE "image_analysis" (
  "id" uuid PRIMARY KEY,
  "image_id" uuid,
  "result" json,
  "confidence" float,
  "processed_at" timestamp
);

CREATE TABLE "users" (
  "id" uuid PRIMARY KEY,
  "username" varchar UNIQUE,
  "password_hash" varchar,
  "role" varchar,
  "phone_number" varchar UNIQUE,
  "created_at" timestamp
);

CREATE INDEX ON "device_positions" ("time");

CREATE INDEX ON "telemetry" ("time");

ALTER TABLE "image_capture" ADD FOREIGN KEY ("device_id") REFERENCES "devices" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "sensors" ADD FOREIGN KEY ("device_id") REFERENCES "devices" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "device_positions" ADD FOREIGN KEY ("device_id") REFERENCES "devices" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "telemetry" ADD FOREIGN KEY ("sensor_id") REFERENCES "sensors" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "image_analysis" ADD FOREIGN KEY ("image_id") REFERENCES "image_capture" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "devices" ADD FOREIGN KEY ("user_id") REFERENCES "users" ("id") DEFERRABLE INITIALLY IMMEDIATE;
