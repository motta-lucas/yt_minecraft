select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
    



select raw_id
from "elt_db_minecraft"."staging_dbt_staging_dbt"."stg_youtube_videos"
where raw_id is null



      
    ) dbt_internal_test