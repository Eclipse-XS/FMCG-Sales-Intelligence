with dates as (select sale_date as date_day from {{ ref('stg_sales') }} union select snapshot_date from {{ ref('stg_inventory') }})
select cast(strftime(date_day,'%Y%m%d') as integer) as date_key,date_day,year(date_day) as year,quarter(date_day) as quarter,month(date_day) as month,week(date_day) as week,dayofweek(date_day) as day_of_week,case when dayofweek(date_day) in (0,6) then true else false end as is_weekend from dates

