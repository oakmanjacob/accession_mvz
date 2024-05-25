import glob
import math

import pandas as pd

from ranges.sheets import SheetParser
from ranges.specimen import Specimen, ReviewNeededException

def import_excel(file_name, arctos_data):
    accession_data = pd.read_excel(file_name, dtype=str)
    accession_data = accession_data.to_dict(orient="records")

    total_specimens = 0

    if len(accession_data) == 0:
        return

    missing_columns = SheetParser.verify_columns_exist(accession_data[0].keys())
    if len(missing_columns) > 0:
        print(f"Missing columns in {file_name}", missing_columns)

    attributes = []
    unitless_attributes = []
    review_needed = []

    for raw_record in accession_data:
        record = SheetParser.extract_record(raw_record)

        try:
            specimen = Specimen(record)
            specimen_attributes, specimen_unitless_attributes = specimen.export_attributes(arctos_data[specimen.guid]["ended_date"])

            attributes.extend(specimen_attributes)
            unitless_attributes.extend(specimen_unitless_attributes)
        except ReviewNeededException as ex:
            review_needed.append(ex.args)
        total_specimens = total_specimens + 1

    return attributes, unitless_attributes, total_specimens, review_needed


def main():
    accession_files = glob.glob(".\\data\\*.xlsx")
    accession_files.sort()

    arctos_data = pd.read_csv(".\\arctos\\arctos_data.csv", dtype=str)
    arctos_data = arctos_data.fillna("")
    arctos_data = arctos_data.to_dict(orient="records")
    arctos_data = {record["guid"]: record for record in arctos_data}

    total_specimens = 0
    total_attributes = []
    total_unitless_attributes = []
    total_review_needed = {}
    for accession_file in accession_files:
        print(accession_file)
        attributes, unitless_attributes, count, total_review_needed[accession_file] = import_excel(file_name=accession_file, arctos_data=arctos_data)
        total_attributes.extend(attributes)
        total_unitless_attributes.extend(unitless_attributes)
        total_specimens = total_specimens + count
        print(count)

    print(total_specimens)

    fucked_guids = set()

    total_attribute_counts = {
        "total": 0,
        "total length": 0,
        "tail length": 0,
        "hind foot with claw": 0,
        "ear from notch": 0,
        "ear from crown": 0,
        "weight": 0,
        "crown-rump length": 0,
        "reproductive data": 0,
        "unformatted measurements": 0,
    }

    attribute_counts = {
        "total": 0,
        "total length": 0,
        "tail length": 0,
        "hind foot with claw": 0,
        "ear from notch": 0,
        "ear from crown": 0,
        "weight": 0,
        "crown-rump length": 0,
        "reproductive data": 0,
        "unformatted measurements": 0,
    }

    filtered_attributes = []
    for attribute in total_attributes:
        total_attribute_counts["total"] = total_attribute_counts["total"] + 1
        total_attribute_counts[attribute["attribute"]] = total_attribute_counts[attribute["attribute"]] + 1
        if attribute["guid"] not in arctos_data:
            fucked_guids.add(attribute["guid"])
        elif arctos_data[attribute["guid"]][attribute["attribute"]] is None or arctos_data[attribute["guid"]][attribute["attribute"]] == "":
            filtered_attributes.append(attribute)
            attribute_counts[attribute["attribute"]] = attribute_counts[attribute["attribute"]] + 1
            attribute_counts["total"] = attribute_counts["total"] + 1


    csv_dataframe = pd.DataFrame.from_records(filtered_attributes)
    csv_dataframe.to_csv(f"./output/numerical_attributes.csv", index=False)

    filtered_text_attributes = []
    for attribute in total_unitless_attributes:
        total_attribute_counts["total"] = total_attribute_counts["total"] + 1
        total_attribute_counts[attribute["attribute"]] = total_attribute_counts[attribute["attribute"]] + 1
        if attribute["guid"] not in arctos_data:
            fucked_guids.add(attribute["guid"])
        elif arctos_data[attribute["guid"]][attribute["attribute"]] is None or arctos_data[attribute["guid"]][attribute["attribute"]] == "":
            filtered_text_attributes.append(attribute)
            attribute_counts[attribute["attribute"]] = attribute_counts[attribute["attribute"]] + 1
            attribute_counts["total"] = attribute_counts["total"] + 1
    
    csv_dataframe = pd.DataFrame.from_records(filtered_text_attributes)
    csv_dataframe.to_csv(f"./output/text_attributes.csv", index=False)

    print(", ".join([f"'{fucked_guid}'" for fucked_guid in fucked_guids]))

    print("Total Attributes Processed:", total_attribute_counts)
    print("Attributes to be uploaded: ", attribute_counts)


    total_review_needed_csv = []

    for key, value in total_review_needed.items():
        if len(value) > 0:
            for specimen in value:
                total_review_needed_csv.append({
                    "sheet": key,
                    "guid": specimen[0],
                    "reason": specimen[1]
                })

    total_review_needed_csv = pd.DataFrame.from_records(total_review_needed_csv)
    total_review_needed_csv.to_csv(f"./output/review_needed.csv", index=False)


if __name__ == "__main__":
    main()