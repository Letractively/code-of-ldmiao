SELECT `board_id` , count( * ) FROM `article` GROUP BY `board_id` 
SELECT `board_id`, count(*) as article_count FROM `article` GROUP BY `board_id` ORDER BY article_count DESC
SELECT `user_name` , count(*) as artcile_count FROM `article` GROUP BY `user_name` ORDER BY artcile_count DESC

SELECT * FROM `article` WHERE `thread_id`=2074503 and `board_id`=65