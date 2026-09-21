
      
        
            delete from "elt_db_minecraft"."core_dbt"."fct_youtube_videos"
            using "fct_youtube_videos__dbt_tmp170515489754"
            where (
                
                    "fct_youtube_videos__dbt_tmp170515489754".video_id = "elt_db_minecraft"."core_dbt"."fct_youtube_videos".video_id
                    and 
                
                    "fct_youtube_videos__dbt_tmp170515489754".collected_at = "elt_db_minecraft"."core_dbt"."fct_youtube_videos".collected_at
                    
                
                
            );
        
    

    insert into "elt_db_minecraft"."core_dbt"."fct_youtube_videos" ("video_id", "collected_at", "published_at", "duration_seconds", "view_count", "like_count", "comment_count")
    (
        select "video_id", "collected_at", "published_at", "duration_seconds", "view_count", "like_count", "comment_count"
        from "fct_youtube_videos__dbt_tmp170515489754"
    )
  