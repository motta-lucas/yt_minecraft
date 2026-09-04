select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
    

select
    raw_id as unique_field,
    count(*) as n_records

from "elt_db_minecraft"."staging_dbt_staging_dbt"."stg_youtube_videos"
where raw_id is not null
group by raw_id
having count(*) > 1



      
    ) dbt_internal_test