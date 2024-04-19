# Filter out specimens in an accession that already have measurements in arctos
import json
accession = 14836

file_name = f"./data/{accession}.xlsx" # path to file + file name
#sheet = "13065" # sheet name or sheet number or list of sheet numbers and names

import pandas as pd
# Query to get reproductive data
"""
SELECT
    flat.accession, guid,
    CAST(flat.cat_num as INTEGER) as catalognumberint,
    ended_date,
    a1.attribute_value as tail_length,
    a2.attribute_value as ear_from_notch,
    a3.attribute_value as total_length,
    a4.attribute_value as hind_foot_with_claw,
    a5.attribute_value as weight,
    a6.attribute_value as reproductive_data, a7.attribute_value as unformatted_measurements
FROM
    flat
    LEFT OUTER JOIN (SELECT * FROM attributes WHERE attribute_type = 'tail length') as a1 ON flat.collection_object_id = a1.collection_object_id
    LEFT OUTER JOIN (SELECT * FROM attributes WHERE attribute_type = 'ear from notch') as a2 ON flat.collection_object_id = a2.collection_object_id
    LEFT OUTER JOIN (SELECT * FROM attributes WHERE attribute_type = 'total length') as a3 ON flat.collection_object_id = a3.collection_object_id
    LEFT OUTER JOIN (SELECT * FROM attributes WHERE attribute_type = 'hind foot with claw') as a4 ON flat.collection_object_id = a4.collection_object_id
    LEFT OUTER JOIN (SELECT * FROM attributes WHERE attribute_type = 'weight') as a5 ON flat.collection_object_id = a5.collection_object_id
    LEFT OUTER JOIN (SELECT * FROM attributes WHERE attribute_type = 'reproductive data') as a6 ON flat.collection_object_id = a6.collection_object_id
LEFT OUTER JOIN (SELECT * FROM attributes WHERE attribute_type = 'unformatted measurements') as a7 ON flat.collection_object_id = a7.collection_object_id
WHERE
    guid_prefix LIKE 'MVZ:Mamm'
AND
    accession IN ('13569', '13065', '13623', '13765', '13774', '13802', '13817', '13828', '13830', '13895', '13968', '13538', '13552', '13574', '13575', '13585', '13627', '13654', '13657', '13677', '13690', '13738', '13972', '13974', '14020', '14348', '14349', '14396', '14454', '14472', '14473', '14485', '14486', '14503', '14564', '14597', '14609', '14672', '14680', '14836')
"""

def get_csv_for_field(accession_data, arctos_data, arctos_data_lookup, arctos_field, accession_field):
    results = []
    arctos_data_search = {}
    for arctos_record in arctos_data:
        arctos_data_search[int(arctos_record["catalognumberint"])] = arctos_record

    for specimen in accession_data:
        # if the specimen does not have data in arctos for this field
        if int(specimen["catalognumberint"]) not in arctos_data_lookup[arctos_field] \
            and specimen[accession_field] != None and specimen[accession_field] != "":
            row= {
                "guid": specimen["guid"],
                "attribute":arctos_field.replace("_", " "),
                "attribute_value": specimen[accession_field]
                }
            
            

            if arctos_field == "weight":
                row["attribute_units"] = "g"
            elif arctos_field in ["total_length", "tail_length", "ear_from_notch", "hind_foot_with_claw"]:
                row["attribute_units"] = "mm"

            row["attribute_date"] = arctos_data_search[int(specimen["catalognumberint"])]["ended_date"]

            # DO NOT FORGET TO REMOVE THIS LATER!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            row["determiner"]= "James L. Patton"
            results.append(row)
        
    return results

def convert_arctos_data(arctos_data, fields):
    arctos_data_lookup = {}

    for field in fields:
        arctos_data_lookup[field] = []

    for record in arctos_data:
        for field in fields:
            if record[field] != None and record[field] != "":
                arctos_data_lookup[field].append(int(record["catalognumberint"]))
    
    return arctos_data_lookup


def main():
    accession_data = pd.read_excel(io=file_name, dtype=str)
    accession_data = accession_data.fillna("")
    accession_data = accession_data.to_dict(orient="records")

    arctos_data = pd.read_excel(io="./data/ArctosAccessionData.xlsx", sheet_name="ArctosAcc")
    arctos_data = arctos_data.fillna("")
    arctos_data = arctos_data.to_dict(orient="records")

    fields = {
        "reproductive_data": "reproductive_data",
        "tail_length": "tail_length",
        "total_length": "total_length",
        "ear_from_notch": "ear_from_notch",
        "hind_foot_with_claw":"hind_foot_with_claw",
        "weight": "weight",
        "unformatted_measurements":"remarks"
        }



    arctos_data_lookup = convert_arctos_data(arctos_data, fields.keys())
    with open("arctos_data_lookup.json", "w") as f:
        json.dump(arctos_data_lookup, f)

    for arctos_field, accession_field in fields.items():
        csv_data = get_csv_for_field(accession_data, arctos_data, arctos_data_lookup, arctos_field, accession_field)
        csv_dataframe = pd.DataFrame.from_records(csv_data)
        csv_dataframe.to_csv(f"./output/{accession}_{arctos_field}.csv", index=False)

main()