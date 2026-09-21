select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
    



select collected_at
from "elt_db_minecraft"."core_dbt"."fct_youtube_videos"
where collected_at is null



      
    ) dbt_internal_test