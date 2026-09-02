with base as (
    select *
    from {{ ref('stg_youtube_videos')}}
    where video_id is not null
),

dedup as (
    select
        *,
        row_number() over (
            partition by video_id, _extracted_at
            order by raw_id desc
        ) as rn
    from base
)

select
    video_id,
    _extracted_at as collected_at,
    published_at,
    view_count,
    like_count,
    comment_count
from dedup
where rn = 1