select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
    



select data
from "elt_db_minecraft"."raw"."videos_data_json"
where data is null



      
    ) dbt_internal_test