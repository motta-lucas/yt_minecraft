select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
    



select video_id
from "elt_db_minecraft"."staging_dbt_core_dbt"."fct_youtube_videos"
where video_id is null



      
    ) dbt_internal_test