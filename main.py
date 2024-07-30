import argparse
import glob
import logging

import pandas as pd

from ranges.sheets import SheetParser
from ranges.specimen import Specimen, ReviewNeededException

logger = logging.getLogger(__name__)

def import_excel(file_name):
    accession_data = pd.read_excel(file_name, dtype=str)
    accession_data = accession_data.to_dict(orient="records")

    if len(accession_data) == 0:
        return

    missing_columns = SheetParser.verify_columns_exist(accession_data[0].keys())
    if len(missing_columns) > 0:
        print(f"Missing columns in {file_name}", missing_columns)

    review_needed = []
    specimens = []
    for raw_record in accession_data:
        try:
            specimen = Specimen.from_raw_record(raw_record)
            specimens.append(specimen)
        except ReviewNeededException as ex:
            review_needed.append(ex.args)

    return specimens, review_needed


def get_attributes(specimens, arctos_data):
    attributes = []
    unitless_attributes = []

    for specimen in specimens:
        if specimen.collectors is None and specimen.guid in arctos_data:
            specimen.collectors = arctos_data[specimen.guid]["collectors"].split(",")[0]

        specimen.collected_date = arctos_data[specimen.guid]["ended_date"]

        specimen_attributes, specimen_unitless_attributes = specimen.export_attributes()

        attributes.extend(specimen_attributes)
        unitless_attributes.extend(specimen_unitless_attributes)

    return attributes, unitless_attributes


def eliminate_duplicates(attributes):
    existing_records = set()

    result = []
    for attribute in attributes:
        key = f"{attribute['guid']}_{attribute['attribute_type']}"
        if key in existing_records:
            logger.warning("Duplicate entries found for guid: %s, attribute: %s", attribute["guid"], attribute["attribute_type"])
        else:
            existing_records.add(key)
            result.append(attribute)
    
    return result

def filter_attributes(attributes, arctos_data):
    filtered_attributes = []
    for attribute in attributes:
        if attribute["guid"] not in arctos_data:
            logger.warning("Guid: %s not found in arctos data!", attribute["guid"])
        elif arctos_data[attribute["guid"]][attribute["attribute_type"]] is None or arctos_data[attribute["guid"]][attribute["attribute_type"]] == "":
            filtered_attributes.append(attribute)

    return filtered_attributes


def summarize_data(attributes):
    total_attribute_counts = {
        "specimens": len(set([attribute["guid"] for attribute in attributes])),
        "total attributes": len(attributes),
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

    for attribute in attributes:
        total_attribute_counts[attribute["attribute_type"]] = total_attribute_counts[attribute["attribute_type"]] + 1

    return total_attribute_counts


def main():
    parser = argparse.ArgumentParser(
                    prog='Arctosify',
                    description='Converts accession and ranges sheets into a format which can be uploaded to Arctos')
    
    parser.add_argument('--arctos_data', type=str, default="arctos\\arctos_data.csv")
    parser.add_argument('--input', type=str, default=".\\data\\*.xlsx")
    parser.add_argument('--output_prefix', type=str, default="")
    
    args = parser.parse_args()

    accession_files = glob.glob(args.input)
    accession_files.sort()

    # Import all specimens from Excel files
    specimens = []
    review_needed = {}
    for accession_file in accession_files:
        print(accession_file)
        file_specimens, review_needed[accession_file] = import_excel(file_name=accession_file)
        specimens.extend(file_specimens)

    # Export review needed files
    review_needed_csv = []
    for key, value in review_needed.items():
        if len(value) > 0:
            for specimen in value:
                review_needed_csv.append({
                    "sheet": key,
                    "guid": specimen[0],
                    "reason": specimen[1]
                })

    if len(review_needed_csv) > 0:
        logger.warning("Review Needed")

    review_needed_csv = pd.DataFrame.from_records(review_needed_csv)
    review_needed_csv.to_csv(f"./output/{args.output_prefix}review_needed.csv", index=False)
        
    # Export list of guids for arctos data input
    specimen_guids = set(specimen.guid for specimen in specimens)
    with open(f"./output/{args.output_prefix}required_guids.txt", "w", encoding="utf8") as guids_file:
        guids_file.write(", ".join([f"'{specimen_guid}'" for specimen_guid in specimen_guids]))
    
    # Import arctos data
    arctos_data = pd.read_csv(args.arctos_data, dtype=str)
    arctos_data = arctos_data.fillna("")
    arctos_data = arctos_data.to_dict(orient="records")
    arctos_data = {record["guid"]: record for record in arctos_data}

    # Get all attribute data
    attributes, unitless_attributes = get_attributes(specimens, arctos_data)

    # Check for and eliminate duplicates
    attributes = eliminate_duplicates(attributes)
    unitless_attributes = eliminate_duplicates(unitless_attributes)

    # Filter out attributes which were found in arctos already
    attributes = filter_attributes(attributes, arctos_data)
    unitless_attributes = filter_attributes(unitless_attributes, arctos_data)

    # Save data to files
    csv_dataframe = pd.DataFrame.from_records(attributes)
    csv_dataframe.to_csv(f"./output/{args.output_prefix}numerical_attributes.csv", index=False)
    
    csv_dataframe = pd.DataFrame.from_records(unitless_attributes)
    csv_dataframe.to_csv(f"./output/{args.output_prefix}text_attributes.csv", index=False)

    # Print summary of data
    summary = summarize_data(attributes + unitless_attributes)
    print(summary)


if __name__ == "__main__":
    main()