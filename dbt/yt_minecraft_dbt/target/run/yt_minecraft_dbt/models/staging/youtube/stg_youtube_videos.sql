
  create view "elt_db_minecraft"."staging_dbt_staging_dbt"."stg_youtube_videos__dbt_tmp"
    
    
  as (
    with src as(
    select
        id as raw_id,
        _extracted_at,
        data
    from "elt_db_minecraft"."raw"."videos_data_json"
),

typed as (
    select
        raw_id,
        _extracted_at,

        data->>'video_id' as video_id,
        data->>'title' as title,

        (data->>'publishedAt')::timestamptz as published_at,

        (
            coalesce(nullif(substring(data->>'duration' from '([0-9]+)H'), '')::int, 0)*3600
            + coalesce(nullif(substring(data->>'duration' from '([0-9]+)M'), '')::int, 0)*60
            + coalesce(nullif(substring(data->>'duration' from '([0-9]+)S'), '')::int, 0)
        )::int as duration_seconds,

        (nullif(data->>'viewCount',''))::bigint as view_count,
        (nullif(data->>'likeCount',''))::bigint as like_count,
        (nullif(data->>'commentCount',''))::bigint as comment_count
    
    from src
)

select * from typed
  );