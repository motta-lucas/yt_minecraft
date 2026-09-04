{% macro generate_schema_name(custom_schema_name, node) -%}
   {%- set default_schema = target.schema -%}

   {# Debug #}

   {{ log("DEBUG generate_schema_name:", info=True)}}
   {{ log(" custom_schema_name '" ~ custom_schema_name ~ "'", info=True)}}
   {{ log(" default_schema: '" ~ default_schema ~ "'", info=True)}}
   {{ log(" node.name: " ~ node.name, info=True)}}
   
   {%- if custom_schema_name is none -%}

      {{ log(" -> Using default_schema: " ~ default_schema, info=True)}}
      {{ default_schema }}
   
   {%- else -%}

      {%- set trimmed = custom_schema_name | trim -%}
      {{ log(" -> custom_schema_name (trimmed): '" ~ trimmed ~ "'", info=True)}}

      {%- if trimmed | length > 0 -%}

         {{log(" -> Using custom: " ~ trimmed, info=True)}}
         {{ trimmed }}
      
      {%- else -%}

         {{log(" -> Custom is empty, using default: " ~ default_schema, info=True)}}
         {{default_schema}}
      
      {%- endif -%}
   
   {%- endif -%}

{%- endmacro -%}
