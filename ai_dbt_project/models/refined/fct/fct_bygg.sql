SELECT number_of_vacancies, relevance, application_deadline
FROM staging.load_data_from_raw_to_staging
WHERE occupation_field__label = 'Bygg och anläggning'