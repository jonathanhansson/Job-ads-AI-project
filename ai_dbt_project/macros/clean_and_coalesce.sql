-- macros/clean_and_coalesce.sql
{% macro clean_and_coalesce(column, default='ej angiven', lower=false, trim=true) %}
  {% set expr = "COALESCE(" ~ column ~ ", '" ~ default ~ "')" %}
  {% if lower %}
    {% set expr = "LOWER(" ~ expr ~ ")" %}
  {% endif %}
  {% if trim %}
    {% set expr = "TRIM(" ~ expr ~ ")" %}
  {% endif %}
  {{ return(expr) }}
{% endmacro %}
-- this macro trims, lowercases and coalesces the column with a default value