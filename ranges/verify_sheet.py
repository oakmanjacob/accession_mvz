import sqlite3
import glob
import pandas as pd
import datetime
import math
import re

from dateutil.parser import parse

expected_columns = [
    {
        "column_name": "MVZ #",
        "valid_names": ["MVZ #", "MVZ#", "catalognumberint"],
        "type": "whole",
        "optional": False
    },
    {
        "column_name": "total",
        "valid_names": ["total"],
        "type": "decimal",
        "optional": False
    },
    {
        "column_name": "tail",
        "valid_names": ["tail"],
        "type": "decimal",
        "optional": False
    },
    {
        "column_name": "hf",
        "valid_names": ["hf"],
        "type": "decimal",
        "optional": False
    },
    {
        "column_name": "ear",
        "valid_names": ["ear"],
        "type": "decimal",
        "optional": False
    },
    {
        "column_name": "Notch",
        "valid_names": ["Notch"],
        "type": "decimal",
        "optional": False
    },
    {
        "column_name": "Crown",
        "valid_names": ["Crown"],
        "type": "decimal",
        "optional": False
    },
    {
        "column_name": "unit",
        "valid_names": ["unit"],
        "type": "distance_unit",
        "optional": False
    },
    {
        "column_name": "wt",
        "valid_names": ["wt"],
        "type": "decimal",
        "optional": False
    },
    {
        "column_name": "units",
        "valid_names": ["units"],
        "type": "mass_unit",
        "optional": False
    },
    {
        "column_name": "repro comments",
        "valid_names": ["units"],
        "type": "text",
        "optional": False
    },
    {
        "column_name": "testes L",
        "valid_names": ["testes L", "testis L"],
        "type": "decimal",
        "optional": False
    },
    {
        "column_name": "testes W",
        "valid_names": ["testes W", "testes R", "testis W", "testis R"],
        "type": "decimal",
        "optional": False
    },
    {
        "column_name": "emb count",
        "valid_names": ["emb count"],
        "type": "whole",
        "optional": True
    },
    {
        "column_name": "embs L",
        "valid_names": ["embs L"],
        "type": "whole",
        "optional": False
    },
    {
        "column_name": "embs R",
        "valid_names": ["embs R"],
        "type": "whole",
        "optional": False
    },
    {
        "column_name": "emb CR",
        "valid_names": ["emb CR"],
        "type": "decimal",
        "optional": True
    },
    {
        "column_name": "scars",
        "valid_names": ["scars"],
        "type": "text",
        "optional": True
    }]

def is_none(value):
    if value is None:
        return True

    if isinstance(value, float) and math.isnan(value):
        return True

    if isinstance(value, str):
        value_cleaned = value.strip().lower()

        if value_cleaned in ["", "not recorded", "?"]:
            return True
    
    return False

def is_valid_whole(value) -> bool:
    try:
        parse_whole(value)
    except:
        return False
    return True

def parse_whole(value) -> int:
    if is_none(value):
        return None
    
    if isinstance(value, int):
        return value
    
    value_cleaned = re.sub("mm$", "", value.strip()).strip()
    if value_cleaned != value:
        print(value, "-->", value_cleaned)
    
    # 2+

    # 5+-

    # 8-

    # 12*

    # [101]

    # 8 mm

    # 8 +-

    # 8mm

    # 15in 15 in 

    # 5
    return int(value_cleaned)

def is_valid_decimal(value) -> bool:
    try:
        parse_decimal(value)
    except:
        return False
    return True

def parse_decimal(value) -> float:
    if is_none(value):
        return None
    
    if isinstance(value, float):
        return value
    
    value_cleaned = re.sub("mm$", "", value.strip()).strip()
    if value_cleaned != value:
        print(value, "-->", value_cleaned)
    
    try:
        return float(parse_decimal(value_cleaned))
    except:
        matched = re.match("([0-9]+) ([0-9+])/([1-9][0-9]*)", value_cleaned)

        if matched:
            return float(matched.group(1)) + float(matched.group(2)) / float(matched.group(3))
        else:
            return float(value_cleaned)


def verify_columns_exist(columns):
    missing_columns = []

    for expected_column in expected_columns:
        found = False
        for valid_name in expected_column["valid_names"]:
            if valid_name in columns:
                found = True
        
        if not found and not expected_column["optional"]:
            missing_columns.append(expected_column["column_name"])

    return missing_columns

def extract_record(raw_record):
    record = {}

    for expected_column in expected_columns:
        found = False
        for valid_name in expected_column["valid_names"]:
            if valid_name in raw_record:
                record[expected_column["column_name"]] = raw_record[valid_name]
                found = True
                break
        
        if not found and expected_column["optional"]:
            record[expected_column["column_name"]] = None

    return record


def is_valid_distance_unit(value):
    try:
        parse_distance_unit(value)
        return True
    except:
        return False

def parse_distance_unit(value):
    if is_none(value):
        return "mm"

    value_cleaned = re.sub("\.", "", value.strip())

    if value_cleaned == "inches":
        return "in"

    valid_units = ["mm", "in"]
    if value_cleaned in valid_units:
        return value_cleaned
    
    if value_cleaned == "":
        return "mm"

    raise ValueError("Cannot convert value to distance unit", value, value_cleaned)

def is_valid_mass_unit(value):
    try:
        verify_mass_unit(value)
        return True
    except:
        return False

def verify_mass_unit(value):
    if is_none(value):
        return "g"

    value_cleaned = re.sub("\.", "", value.strip())

    valid_units = ["g"]
    if value_cleaned in valid_units:
        return value_cleaned
    
    if value_cleaned == "":
        return "g"

    raise ValueError("Cannot convert value to distance unit", value, value_cleaned)

def verify_excel(file_name):
    accession_data = pd.read_excel(file_name, dtype=str)
    accession_data = accession_data.to_dict(orient="records")

    if len(accession_data) == 0:
        return

    missing_columns = verify_columns_exist(accession_data[0].keys())
    if len(missing_columns) > 0:
        print(f"Missing columns in {file_name}", missing_columns)


    failures = set()
    for raw_record in accession_data:
        record = extract_record(raw_record)

        for expected_column in expected_columns:
            is_valid = True
            match expected_column["type"]:
                case "decimal":
                    is_valid = is_valid_decimal(record[expected_column["column_name"]])
                case "whole":
                    is_valid = is_valid_decimal(record[expected_column["column_name"]])
                case "distance_unit":
                    is_valid = is_valid_distance_unit(record[expected_column["column_name"]])
                case "mass_unit":
                    is_valid = is_valid_mass_unit(record[expected_column["column_name"]])
            
            if not is_valid:
                failures.add(f"Could not parse '{expected_column['column_name']}': '{record[expected_column['column_name']]}'")
    
    if len(failures) != 0:
        for failure in failures:
            print(failure)


def main():
    accession_files = glob.glob(".\\data\\*.xlsx")

    for accession_file in accession_files:
        print(accession_file)
        verify_excel(file_name=accession_file)


if __name__ == "__main__":
    main()