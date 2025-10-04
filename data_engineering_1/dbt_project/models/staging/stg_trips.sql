{{
    config(
        materialized='view',
        tags=['staging', 'trips']
    )
}}

WITH source_data AS (
    SELECT *
    FROM {{ source('raw', 'taxi_trips') }}
),

renamed AS (
    SELECT
        vendorid AS vendor_id,
        pulocationid AS pickup_location_id,
        dolocationid AS dropoff_location_id,
        CAST(tpep_pickup_datetime AS TIMESTAMP) AS pickup_datetime,
        CAST(tpep_dropoff_datetime AS TIMESTAMP) AS dropoff_datetime,
        CAST(passenger_count AS INTEGER) AS passenger_count,
        CAST(trip_distance AS DECIMAL(10,2)) AS trip_distance_miles,
        ratecodeid AS rate_code_id,
        store_and_fwd_flag,
        payment_type,
        CAST(fare_amount AS DECIMAL(10,2)) AS fare_amount,
        CAST(extra AS DECIMAL(10,2)) AS extra_charges,
        CAST(mta_tax AS DECIMAL(10,2)) AS mta_tax,
        CAST(tip_amount AS DECIMAL(10,2)) AS tip_amount,
        CAST(tolls_amount AS DECIMAL(10,2)) AS tolls_amount,
        CAST(improvement_surcharge AS DECIMAL(10,2)) AS improvement_surcharge,
        CAST(total_amount AS DECIMAL(10,2)) AS total_amount,
        CAST(congestion_surcharge AS DECIMAL(10,2)) AS congestion_surcharge,
        processed_at,
        data_version
    FROM source_data
)

SELECT * FROM renamed
WHERE pickup_datetime IS NOT NULL
  AND dropoff_datetime IS NOT NULL
  AND fare_amount >= 0
  AND total_amount >= 0
