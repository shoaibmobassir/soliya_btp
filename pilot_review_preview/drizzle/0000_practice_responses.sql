CREATE TABLE `practice_responses` (
  `session_id` text NOT NULL,
  `condition_id` text NOT NULL,
  `reviewer_name` text NOT NULL,
  `response_json` text NOT NULL,
  `submitted_at` text NOT NULL,
  PRIMARY KEY(`session_id`, `condition_id`)
);
