select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
    



select _extracted_at
from "elt_db_minecraft"."staging_dbt_staging_dbt"."stg_youtube_videos"
where _extracted_at is null



      
    ) dbt_internal_test