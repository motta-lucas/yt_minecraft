with base as (
    select *
    from "elt_db_minecraft"."staging_dbt_staging_dbt"."stg_youtube_videos"
),

dedup as (
    select
        *,
        row_number() over (
            partition by video_id
            order by _extracted_at desc, raw_id desc
        ) as rn
    from base
)

select
    _extracted_at as as_of_ts,
    video_id,
    title,
    published_at,
    duration_seconds,
    view_count,
    like_count,
    comment_count
from dedup
where rn = 1