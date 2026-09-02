select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
    



select _extracted_at
from "elt_db_minecraft"."raw"."videos_data_json"
where _extracted_at is null



      
    ) dbt_internal_test