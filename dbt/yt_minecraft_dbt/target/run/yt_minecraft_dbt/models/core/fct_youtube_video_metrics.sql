
      
        
            delete from "elt_db_minecraft"."core_dbt"."fct_youtube_video_metrics"
            using "fct_youtube_video_metrics__dbt_tmp170515474009"
            where (
                
                    "fct_youtube_video_metrics__dbt_tmp170515474009".video_id = "elt_db_minecraft"."core_dbt"."fct_youtube_video_metrics".video_id
                    and 
                
                    "fct_youtube_video_metrics__dbt_tmp170515474009".collected_at = "elt_db_minecraft"."core_dbt"."fct_youtube_video_metrics".collected_at
                    
                
                
            );
        
    

    insert into "elt_db_minecraft"."core_dbt"."fct_youtube_video_metrics" ("video_id", "collected_at", "published_at", "view_count", "like_count", "comment_count")
    (
        select "video_id", "collected_at", "published_at", "view_count", "like_count", "comment_count"
        from "fct_youtube_video_metrics__dbt_tmp170515474009"
    )
  