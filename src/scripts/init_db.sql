CREATE TABLE "tg_users" (
  "tg_user_id" bigint PRIMARY KEY NOT NULL,
  "vk_access_token" text,
  "vk_user_id" bigint,
  "filter_city_name" varchar(128),
  "filter_gender" smallint,
  "filter_age_from" smallint,
  "filter_age_to" smallint,
  "history_cursor" integer DEFAULT 0
);

CREATE TABLE "vk_profiles" (
  "vk_user_id" bigint PRIMARY KEY NOT NULL,
  "first_name" varchar(128),
  "last_name" varchar(128),
  "profile_url" text,
  "status" varchar(16) DEFAULT 'new',
  "found_at" timestamp
);

CREATE TABLE "search_queue" (
  "id" SERIAL PRIMARY KEY,
  "tg_user_id" bigint NOT NULL,
  "vk_profile_id" bigint NOT NULL,
  "position" integer NOT NULL
);

CREATE TABLE "seen_profiles" (
  "id" SERIAL PRIMARY KEY,
  "tg_user_id" bigint NOT NULL,
  "vk_profile_id" bigint NOT NULL
);

CREATE TABLE "view_history" (
  "id" SERIAL PRIMARY KEY,
  "tg_user_id" bigint NOT NULL,
  "vk_profile_id" bigint NOT NULL,
  "position" integer NOT NULL,
  "photo_attachments" text
);

CREATE TABLE "favorite_profiles" (
  "id" SERIAL PRIMARY KEY,
  "tg_user_id" bigint NOT NULL,
  "vk_profile_id" bigint NOT NULL
);

CREATE TABLE "blacklist_profiles" (
  "id" SERIAL PRIMARY KEY,
  "tg_user_id" bigint NOT NULL,
  "vk_profile_id" bigint NOT NULL
);

CREATE TABLE "vk_photos" (
  "id" SERIAL PRIMARY KEY,
  "vk_user_id" bigint NOT NULL,
  "vk_photo_id" bigint NOT NULL,
  "likes_count" integer DEFAULT 0,
  "file_path" text,
  "downloaded_at" timestamp,
  "status" varchar(16) DEFAULT 'raw',
  "reject_reason" varchar(32),
  "faces_count" smallint,
  "det_score" real,
  "bbox" jsonb,
  "blur_score" real,
  "embedding" bytea,
  "embedding_normed" boolean DEFAULT false,
  "model_name" varchar(64),
  "model_version" varchar(32),
  "processed_at" timestamp
);

CREATE UNIQUE INDEX ON "search_queue" ("tg_user_id", "vk_profile_id");

CREATE INDEX ON "search_queue" ("tg_user_id", "position");

CREATE UNIQUE INDEX ON "seen_profiles" ("tg_user_id", "vk_profile_id");

CREATE INDEX ON "seen_profiles" ("tg_user_id");

CREATE UNIQUE INDEX ON "view_history" ("tg_user_id", "position");

CREATE UNIQUE INDEX ON "favorite_profiles" ("tg_user_id", "vk_profile_id");

CREATE INDEX ON "favorite_profiles" ("tg_user_id");

CREATE UNIQUE INDEX ON "blacklist_profiles" ("tg_user_id", "vk_profile_id");

CREATE INDEX ON "blacklist_profiles" ("tg_user_id");

CREATE UNIQUE INDEX ON "vk_photos" ("vk_user_id", "vk_photo_id");

CREATE INDEX ON "vk_photos" ("vk_user_id");

CREATE INDEX ON "vk_photos" ("status");

COMMENT ON COLUMN "tg_users"."tg_user_id" IS 'Telegram user ID';

COMMENT ON COLUMN "tg_users"."vk_access_token" IS 'VK токен пользователя';

COMMENT ON COLUMN "tg_users"."vk_user_id" IS 'VK ID пользователя';

COMMENT ON COLUMN "tg_users"."filter_city_name" IS 'название города';

COMMENT ON COLUMN "tg_users"."filter_gender" IS '0=любой, 1=жен, 2=муж';

COMMENT ON COLUMN "tg_users"."filter_age_from" IS 'возраст ОТ';

COMMENT ON COLUMN "tg_users"."filter_age_to" IS 'возраст ДО';

COMMENT ON COLUMN "tg_users"."history_cursor" IS 'текущая позиция в view_history';

COMMENT ON COLUMN "vk_profiles"."vk_user_id" IS 'VK ID кандидата';

COMMENT ON COLUMN "vk_profiles"."profile_url" IS 'ссылка на профиль VK';

COMMENT ON COLUMN "vk_profiles"."status" IS 'new / processing / ready / error';

COMMENT ON COLUMN "vk_profiles"."found_at" IS 'когда найден через users.search';

COMMENT ON COLUMN "search_queue"."position" IS 'порядок в результатах поиска';

COMMENT ON COLUMN "view_history"."position" IS 'порядковый номер в истории';

COMMENT ON COLUMN "view_history"."photo_attachments" IS 'PostgreSQL TEXT ARRAY — фото attachments';

COMMENT ON COLUMN "vk_photos"."vk_user_id" IS 'владелец фото';

COMMENT ON COLUMN "vk_photos"."vk_photo_id" IS 'ID фото в VK';

COMMENT ON COLUMN "vk_photos"."likes_count" IS 'лайки — ключ ранжирования';

COMMENT ON COLUMN "vk_photos"."file_path" IS 'путь к файлу на диске';

COMMENT ON COLUMN "vk_photos"."downloaded_at" IS 'когда скачали';

COMMENT ON COLUMN "vk_photos"."status" IS 'raw / accepted / rejected / selected';

COMMENT ON COLUMN "vk_photos"."reject_reason" IS 'no_face, multi_face, blurry, small_face, low_score, error';

COMMENT ON COLUMN "vk_photos"."faces_count" IS 'сколько лиц нашёл детектор';

COMMENT ON COLUMN "vk_photos"."det_score" IS 'уверенность детектора для выбранного лица';

COMMENT ON COLUMN "vk_photos"."bbox" IS 'координаты лица — x1, y1, x2, y2';

COMMENT ON COLUMN "vk_photos"."blur_score" IS 'variance of Laplacian';

COMMENT ON COLUMN "vk_photos"."embedding" IS 'ArcFace 512 x float32 = 2048 bytes';

COMMENT ON COLUMN "vk_photos"."embedding_normed" IS 'эмбеддинг L2-нормирован';

COMMENT ON COLUMN "vk_photos"."model_name" IS 'напр. buffalo_l';

COMMENT ON COLUMN "vk_photos"."model_version" IS 'версия модели';

COMMENT ON COLUMN "vk_photos"."processed_at" IS 'когда обработали';

ALTER TABLE "search_queue" ADD FOREIGN KEY ("tg_user_id") REFERENCES "tg_users" ("tg_user_id");

ALTER TABLE "search_queue" ADD FOREIGN KEY ("vk_profile_id") REFERENCES "vk_profiles" ("vk_user_id");

ALTER TABLE "seen_profiles" ADD FOREIGN KEY ("tg_user_id") REFERENCES "tg_users" ("tg_user_id");

ALTER TABLE "seen_profiles" ADD FOREIGN KEY ("vk_profile_id") REFERENCES "vk_profiles" ("vk_user_id");

ALTER TABLE "view_history" ADD FOREIGN KEY ("tg_user_id") REFERENCES "tg_users" ("tg_user_id");

ALTER TABLE "view_history" ADD FOREIGN KEY ("vk_profile_id") REFERENCES "vk_profiles" ("vk_user_id");

ALTER TABLE "favorite_profiles" ADD FOREIGN KEY ("tg_user_id") REFERENCES "tg_users" ("tg_user_id");

ALTER TABLE "favorite_profiles" ADD FOREIGN KEY ("vk_profile_id") REFERENCES "vk_profiles" ("vk_user_id");

ALTER TABLE "blacklist_profiles" ADD FOREIGN KEY ("tg_user_id") REFERENCES "tg_users" ("tg_user_id");

ALTER TABLE "blacklist_profiles" ADD FOREIGN KEY ("vk_profile_id") REFERENCES "vk_profiles" ("vk_user_id");

ALTER TABLE "vk_photos" ADD FOREIGN KEY ("vk_user_id") REFERENCES "vk_profiles" ("vk_user_id");