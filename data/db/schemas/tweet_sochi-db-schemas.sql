##
##  Table setup
##
BEGIN;
USE tweet_infx547;
CREATE TABLE `twitter_tweets` (
  `rid` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `tweet_id` BIGINT UNSIGNED DEFAULT NULL,
  `tweet_id_str` VARCHAR(64) CHARACTER SET 'utf8' COLLATE 'utf8_general_ci' DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `from_user_id` BIGINT UNSIGNED DEFAULT NULL,
  `from_user` VARCHAR(64) CHARACTER SET 'utf8' COLLATE 'utf8_general_ci' DEFAULT NULL,
  `from_user_name` VARCHAR(64) CHARACTER SET 'utf8' COLLATE 'utf8_general_ci' DEFAULT NULL,
  `lat` DECIMAL(25,16) DEFAULT NULL,
  `lon` DECIMAL(25,16) DEFAULT NULL,
  `tweet_text` VARCHAR(256) CHARACTER SET 'utf8' COLLATE 'utf8_general_ci' DEFAULT NULL 
) ENGINE=MyISAM DEFAULT CHARACTER SET 'utf8' COLLATE 'utf8_general_ci';
ALTER TABLE `twitter_tweets` ADD INDEX `tweet_index` (`tweet_id`);
ALTER TABLE `twitter_tweets` ADD INDEX `user_index` (`from_user`);
ALTER TABLE `twitter_tweets` ADD INDEX `id_index` (`from_user_id`);
ALTER TABLE `twitter_tweets` ADD INDEX `creation_index` (`created_at`);

CREATE TABLE `twitter_users` (
  `rid` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `user_name` VARCHAR(64) CHARACTER SET 'utf8' COLLATE 'utf8_general_ci' DEFAULT NULL,
  `screen_name` VARCHAR(64) CHARACTER SET 'utf8' COLLATE 'utf8_general_ci' DEFAULT NULL,
  `user_id` BIGINT UNSIGNED DEFAULT NULL,
  `join_dt` datetime DEFAULT NULL,
  `verified` BOOLEAN DEFAULT FALSE,
  `geo_enabled` BOOLEAN DEFAULT FALSE,
  `location` VARCHAR(64) CHARACTER SET 'utf8' COLLATE 'utf8_general_ci' DEFAULT NULL,
  `lang` VARCHAR(8) CHARACTER SET 'utf8' COLLATE 'utf8_general_ci' DEFAULT NULL,
  `time_zone` VARCHAR(64) CHARACTER SET 'utf8' COLLATE 'utf8_general_ci' DEFAULT NULL,
  `url` VARCHAR(256) CHARACTER SET 'utf8' DEFAULT NULL,
  `description` VARCHAR(256) CHARACTER SET 'utf8' COLLATE 'utf8_general_ci' DEFAULT NULL
) ENGINE=MyISAM DEFAULT CHARACTER SET 'utf8' COLLATE 'utf8_general_ci';
ALTER TABLE `twitter_users` ADD INDEX `name_index` (`user_name`);
ALTER TABLE `twitter_users` ADD INDEX `screen_index` (`screen_name`);
ALTER TABLE `twitter_users` ADD INDEX `id_index` (`user_id`);
  
CREATE TABLE `twitter_user_meta` (
  `rid` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `user_name` VARCHAR(64) CHARACTER SET 'utf8' COLLATE 'utf8_general_ci' DEFAULT NULL,
  `screen_name` VARCHAR(64) CHARACTER SET 'utf8' COLLATE 'utf8_general_ci' DEFAULT NULL,
  `user_id` BIGINT UNSIGNED DEFAULT NULL,
  `friend_count` BIGINT UNSIGNED DEFAULT NULL,
  `follower_count` BIGINT UNSIGNED DEFAULT NULL,
  `profile_collect_dt` datetime DEFAULT NULL,
  `friend_collect_dt` datetime DEFAULT NULL,
  `friend_collect_resp` VARCHAR(32) CHARACTER SET 'utf8' COLLATE 'utf8_general_ci' DEFAULT NULL,
  `follower_collect_dt` datetime DEFAULT NULL,
  `follower_collect_resp` VARCHAR(32) CHARACTER SET 'utf8' COLLATE 'utf8_general_ci' DEFAULT NULL
) ENGINE=MyISAM DEFAULT CHARACTER SET 'utf8' COLLATE 'utf8_general_ci';
ALTER TABLE `twitter_user_meta` ADD INDEX `name_index` (`user_name`);
ALTER TABLE `twitter_user_meta` ADD INDEX `screen_index` (`screen_name`);
ALTER TABLE `twitter_user_meta` ADD INDEX `id_index` (`user_id`);

CREATE TABLE `twitter_friends` (
  `rid` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `user` VARCHAR(64) CHARACTER SET 'utf8' COLLATE 'utf8_general_ci' DEFAULT NULL,
  `friend` VARCHAR(64) CHARACTER SET 'utf8' COLLATE 'utf8_general_ci' DEFAULT NULL,
  `user_id` BIGINT UNSIGNED DEFAULT NULL,
  `friend_id` BIGINT UNSIGNED DEFAULT NULL,
  `user_local_id` BIGINT UNSIGNED DEFAULT NULL,
  `friend_local_id` BIGINT UNSIGNED DEFAULT NULL
) ENGINE=MyISAM DEFAULT CHARACTER SET 'utf8' COLLATE 'utf8_general_ci';
ALTER TABLE `twitter_friends` ADD INDEX `user_index` (`user`);
ALTER TABLE `twitter_friends` ADD INDEX `user_id_index` (`user_id`);
ALTER TABLE `twitter_friends` ADD INDEX `user_local_index` (`user_local_id`);
ALTER TABLE `twitter_friends` ADD INDEX `friend_index` (`friend_id`);

CREATE TABLE `twitter_followers` (
  `rid` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `user` VARCHAR(64) CHARACTER SET 'utf8' COLLATE 'utf8_general_ci' DEFAULT NULL,
  `follower` VARCHAR(64) CHARACTER SET 'utf8' COLLATE 'utf8_general_ci' DEFAULT NULL,
  `user_id` BIGINT UNSIGNED DEFAULT NULL,
  `follower_id` BIGINT UNSIGNED DEFAULT NULL,
  `user_local_id` BIGINT UNSIGNED DEFAULT NULL,
  `follower_local_id` BIGINT UNSIGNED DEFAULT NULL
) ENGINE=MyISAM DEFAULT CHARACTER SET 'utf8' COLLATE 'utf8_general_ci';
ALTER TABLE `twitter_followers` ADD INDEX `user_index` (`user`);
ALTER TABLE `twitter_followers` ADD INDEX `user_id_index` (`user_id`);
ALTER TABLE `twitter_followers` ADD INDEX `user_local_index` (`user_local_id`);
ALTER TABLE `twitter_followers` ADD INDEX `follower_index` (`follower_id`);
COMMIT;
