import glob
import math

import pandas as pd

from ranges.sheets import SheetParser
from ranges.specimen import Specimen

def import_excel(file_name):
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

    for raw_record in accession_data:
        record = SheetParser.extract_record(raw_record)
        specimen = Specimen(record)
        specimen_attributes, specimen_unitless_attributes = specimen.export_attributes(None)

        attributes.extend(specimen_attributes)
        unitless_attributes.extend(specimen_unitless_attributes)
        total_specimens = total_specimens + 1

    return attributes, unitless_attributes, total_specimens


def main():
    accession_files = glob.glob(".\\data\\*.xlsx")

    total_specimens = 0
    total_attributes = []
    total_unitless_attributes = []
    for accession_file in accession_files:
        print(accession_file)
        attributes, unitless_attributes, count = import_excel(file_name=accession_file)
        total_attributes.extend(attributes)
        total_unitless_attributes.extend(unitless_attributes)
        total_specimens = total_specimens + count

    print(total_specimens)

    arctos_data = pd.read_csv(".\\arctos\\arctos_data.csv", dtype=str)
    arctos_data = arctos_data.fillna("")
    arctos_data = arctos_data.to_dict(orient="records")

    arctos_data = {record["guid"]: record for record in arctos_data}

    fucked_guids = set()

    filtered_attributes = []
    for attribute in total_attributes:
        if attribute["guid"] not in arctos_data:
            fucked_guids.add(attribute["guid"])
        elif arctos_data[attribute["guid"]][attribute["attribute"]] is None or arctos_data[attribute["guid"]][attribute["attribute"]] == "":
            filtered_attributes.append(attribute)


    csv_dataframe = pd.DataFrame.from_records(filtered_attributes)
    csv_dataframe.to_csv(f"./output/numerical_attributes.csv", index=False)

    filtered_text_attributes = []
    for attribute in total_unitless_attributes:
        if attribute["guid"] not in arctos_data:
            fucked_guids.add(attribute["guid"])
        elif arctos_data[attribute["guid"]][attribute["attribute"]] is None or arctos_data[attribute["guid"]][attribute["attribute"]] == "":
            filtered_text_attributes.append(attribute)
    
    csv_dataframe = pd.DataFrame.from_records(filtered_text_attributes)
    csv_dataframe.to_csv(f"./output/text_attributes.csv", index=False)

    print(", ".join([f"'{fucked_guid}'" for fucked_guid in fucked_guids]))


if __name__ == "__main__":
    main()