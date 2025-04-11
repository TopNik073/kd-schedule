CREATE TABLE "users" (
  "id" UUID PRIMARY KEY,
  "name" varchar,
  "medicine_policy" int NOT NULL,
  "schedules" Schedules,
  "created_at" timestamp NOT NULL
);

CREATE TABLE "schedules" (
  "id" UUID PRIMARY KEY,
  "user_id" UUID NOT NULL,
  "user" Users NOT NULL,
  "medicine_name" varchar NOT NULL,
  "freequency" int NOT NULL,
  "start_date" timestamp NOT NULL,
  "end_date" timestamp,
  "created_at" timestamp NOT NULL
);

ALTER TABLE "schedules" ADD CONSTRAINT "user_schedules_ids" FOREIGN KEY ("user_id") REFERENCES "users" ("id");

ALTER TABLE "schedules" ADD CONSTRAINT "user_schedules" FOREIGN KEY ("user") REFERENCES "users" ("schedules");
