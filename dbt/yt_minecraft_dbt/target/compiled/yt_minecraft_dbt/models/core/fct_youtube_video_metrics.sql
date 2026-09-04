

with base as (
    select *
    from "elt_db_minecraft"."staging_dbt"."stg_youtube_videos"
    
)

select
    video_id,
    _extracted_at as collected_at,
    published_at,
    view_count,
    like_count,
    comment_count
from base
where video_id is not null