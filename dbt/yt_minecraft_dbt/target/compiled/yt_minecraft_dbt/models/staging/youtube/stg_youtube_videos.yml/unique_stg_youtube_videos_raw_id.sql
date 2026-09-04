
    
    

select
    raw_id as unique_field,
    count(*) as n_records

from "elt_db_minecraft"."staging_dbt_staging_dbt"."stg_youtube_videos"
where raw_id is not null
group by raw_id
having count(*) > 1


