SELECT
    id,
    siret,
    created_at,
    code_sous_classe,
    libelle_sous_classe,
    libelle_classe,
    code_classe,
    libelle_groupe,
    code_groupe,
    libelle_division,
    code_division,
    libelle_section,
    code_section
FROM
    "refined_zone_enriched"."company_enriched"
WHERE
    "created_at" <= CURRENT_DATE - CAST(
        EXTRACT(
            dow
            FROM
                CURRENT_DATE
        ) AS INT
    )
