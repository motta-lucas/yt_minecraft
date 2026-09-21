
      insert into "elt_db_minecraft"."staging_dbt"."stg_youtube_videos" ("raw_id", "video_id", "_extracted_at", "title", "published_at", "duration_seconds", "view_count", "like_count", "comment_count")
    (
        select "raw_id", "video_id", "_extracted_at", "title", "published_at", "duration_seconds", "view_count", "like_count", "comment_count"
        from "stg_youtube_videos__dbt_tmp170458562678"
    )


  