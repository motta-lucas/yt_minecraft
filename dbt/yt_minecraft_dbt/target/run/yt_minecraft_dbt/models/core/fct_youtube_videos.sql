
      
  
    

  create  table "elt_db_minecraft"."core_dbt"."fct_youtube_videos"
  
  
    as
  
  (
    

with base as (
    select *
    from "elt_db_minecraft"."staging_dbt"."stg_youtube_videos"
    
)

select
    video_id,
    _extracted_at as collected_at,
    published_at,
    duration_seconds,
    view_count,
    like_count,
    comment_count
from base
where video_id is not null
  );
  
  