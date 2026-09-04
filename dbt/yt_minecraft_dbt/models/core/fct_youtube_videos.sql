{{
    config(
        materialized='incremental',
        unique_key=['video_id','collected_at'],
        incremental_strategy='delete+insert'
    )
}}

with base as (
    select *
    from {{ ref('stg_youtube_videos')}}
    {%if is_incremental()%}
    where _extracted_at > (
        select max(collected_at) from {{ this }}
    )
    {% endif %}
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