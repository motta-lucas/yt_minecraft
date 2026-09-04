
    
    



select collected_at
from "elt_db_minecraft"."staging_dbt_core_dbt"."fct_youtube_videos"
where collected_at is null


