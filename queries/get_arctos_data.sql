SELECT
    flat.collection_object_id,
    guid,
    a0.attribute_value AS "total length",
    a1.attribute_value AS "tail length",
    a2.attribute_value AS "hind foot with claw",
    a3.attribute_value AS "ear from notch",
    a4.attribute_value AS "ear from crown",
    a5.attribute_value AS "weight",
    a6.attribute_value AS "crown-rump length",
    a7.attribute_value AS "reproductive data",
    a8.attribute_value AS "unformatted measurements"
FROM
    flat
LEFT OUTER JOIN
    (SELECT *
    FROM attributes
    WHERE attribute_type = 'total length') AS a0 ON flat.collection_object_id = a0.collection_object_id
LEFT OUTER JOIN
    (SELECT *
    FROM attributes
    WHERE attribute_type = 'tail length') AS a1 ON flat.collection_object_id = a1.collection_object_id
LEFT OUTER JOIN
    (SELECT *
    FROM attributes
    WHERE attribute_type = 'hind foot with claw') AS a2 ON flat.collection_object_id = a2.collection_object_id
LEFT OUTER JOIN
    (SELECT *
    FROM attributes
    WHERE attribute_type = 'ear from notch') AS a3 ON flat.collection_object_id = a3.collection_object_id
LEFT OUTER JOIN
    (SELECT *
    FROM attributes
    WHERE attribute_type = 'ear from crown') AS a4 ON flat.collection_object_id = a4.collection_object_id
LEFT OUTER JOIN
    (SELECT *
    FROM attributes
    WHERE attribute_type = 'weight') AS a5 ON flat.collection_object_id = a5.collection_object_id
LEFT OUTER JOIN
    (SELECT *
    FROM attributes
    WHERE attribute_type = 'crown-rump length') AS a6 ON flat.collection_object_id = a6.collection_object_id
LEFT OUTER JOIN
    (SELECT *
    FROM attributes
    WHERE attribute_type = 'reproductive data') AS a7 ON flat.collection_object_id = a7.collection_object_id
LEFT OUTER JOIN
    (SELECT *
    FROM attributes
    WHERE attribute_type = 'unformatted measurements') AS a8 ON flat.collection_object_id = a8.collection_object_id
WHERE
    guid_prefix LIKE 'MVZ:Mamm'
AND
    genus in ('Anourosorex', 'Myosorex', 'Notiosorex', 'Sorex', 'Sorex; Sorex', 'Soriculus', 'Suncus')
ORDER BY guid asc
limit 9000
OFFSET 9000