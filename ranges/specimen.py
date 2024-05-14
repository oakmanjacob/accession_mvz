import sqlite3
import glob
import pandas as pd
import datetime
import math
import re
import decimal
import csv

from dateutil.parser import parse
from decimal import Decimal, InvalidOperation
from enum import Enum
from typing import Union, Callable, TypeVar

expected_columns = [
    {
        "column_name": "MVZ #",
        "valid_names": ["MVZ #", "MVZ#", "catalognumberint"],
        "type": "whole",
        "optional": False
    },
    {
        "column_name": "collector",
        "valid_names": ["collector", "collectors", "COLLECTORS"],
        "type": "text",
        "optional": False
    },
    {
        "column_name": "date",
        "valid_names": ["date"],
        "type": "text",
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
        "optional": True
    },
    {
        "column_name": "testes W",
        "valid_names": ["testes W", "testes R", "testis W", "testis R"],
        "type": "decimal",
        "optional": True
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
        "optional": True
    },
    {
        "column_name": "embs R",
        "valid_names": ["embs R"],
        "type": "whole",
        "optional": True
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
    },
    {
        "column_name": "unformatted measurements",
        "valid_names": ["unformatted measurements"],
        "type": "text",
        "optional": True
    },
    {
        "column_name": "REVIEW NEEDED",
        "valid_names": ["REVIEW NEEDED"],
        "type": "text",
        "optional": True
    }]

class WeightUnit(Enum):
    GRAMS = "g"
    OUNCES = "oz"

    def from_string(value: str):
        if value in ["g", "grams"]:
            return WeightUnit.GRAMS
        elif value in ["oz", "ounces"]:
            return WeightUnit.OUNCES
        elif value is None:
            return None
        else:
            raise ValueError("Could not parse distance unit from value", value)
        
    @staticmethod
    def split_value(value: str):
        matched = re.match(r"^(.+)\s*(g|grams|oz|ounces)?$", value.strip())

        if matched is None:
            raise ValueError("Could not parse value", value)
        
        value_cleaned = matched.group(1)
        extracted_unit = matched.group(2)

        return value_cleaned, WeightUnit.from_string(extracted_unit) if extracted_unit is not None else None

class DistanceUnit(Enum):
    INCHES = "in"
    MILLIMETERS = "mm"
    CENTIMETERS = "cm"

    @staticmethod
    def from_string(value: str):
        if value == "in" or value == "in." or value == "inches":
            return DistanceUnit.INCHES
        elif value == "mm":
            return DistanceUnit.MILLIMETERS
        elif value == "cm":
            return DistanceUnit.CENTIMETERS
        elif value is None:
            return None
        else:
            raise ValueError("Could not parse distance unit from value", value)
        
    @staticmethod
    def split_value(value: str):
        matched = re.match(r"^(.+)\s*(mm|in|in\.|inches)?$", value.strip())

        if matched is None:
            return value.strip(), None
        
        value_cleaned = matched.group(1)
        extracted_unit = matched.group(2)

        return value_cleaned, DistanceUnit.from_string(extracted_unit) if extracted_unit is not None else None


class SheetParser:
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

    def is_recorded(raw_value):
        if raw_value is None:
            return False

        if isinstance(raw_value, float) and math.isnan(raw_value):
            return False

        if isinstance(raw_value, str):
            value_cleaned = raw_value.strip().lower()

            if value_cleaned in ["", "not recorded", "?", "no recorded", "already in arctos",
                                "no measurements", "not recoded"]:
                return False
        
        return True

    def extract_record(raw_record):
        record = {}

        for expected_column in expected_columns:
            found = False
            for valid_name in expected_column["valid_names"]:
                if valid_name in raw_record:
                    column = raw_record[valid_name]
                    if isinstance(column, str):
                        column = column.strip()
                    
                    if SheetParser.is_recorded(column):
                        record[expected_column["column_name"]] = str(column)
                    else:
                        record[expected_column["column_name"]] = None

                    found = True
                    break
            
            if not found and expected_column["optional"]:
                record[expected_column["column_name"]] = None

        return record
    
    def parse_mvz_guid(value: str) -> str:
        return f"MVZ:Mamm:{int(value)}"

    
    def parse_numerical_attribute(raw_value: str,
                                  unit_splitter: Callable[
                                      [str],tuple[str, Union[DistanceUnit, WeightUnit]]],
                                  unit: Union[DistanceUnit, WeightUnit],
                                  default: Union[DistanceUnit, WeightUnit]) -> \
                                    tuple[Decimal, Union[DistanceUnit, WeightUnit], str]:
        if raw_value is None:
            return None, None, None

        value_cleaned, extracted_unit = unit_splitter(raw_value)

        matched = re.match("(?:([0-9]+) )?([0-9]+)/([1-9][0-9]*)", value_cleaned)

        value = None
        remarks = None
        try:
            if matched:
                remarks = value_cleaned
                value = Decimal(matched.group(1) or 0) + \
                    Decimal(matched.group(2)) / Decimal(matched.group(3)).quantize(Decimal('0.01'))
            else:
                value = Decimal(value_cleaned)
        except InvalidOperation:
            remarks = raw_value

        if extracted_unit is not None and unit is not None and extracted_unit != unit:
            print("Unit Mismatched")

        if extracted_unit is None:
            extracted_unit = unit or default

        return value, extracted_unit, remarks

class Specimen:
    guid: str
    collectors: str

    total_length: tuple[Decimal, DistanceUnit, str]
    tail_length: tuple[Decimal, DistanceUnit, str]
    hind_foot_with_claw: tuple[Decimal, DistanceUnit, str]
    ear_from_notch: tuple[Decimal, DistanceUnit, str]
    ear_from_crown: tuple[Decimal, DistanceUnit, str]
    weight: tuple[Decimal, WeightUnit, str]
    unformatted_measurements: str

    testes_length: tuple[Decimal, DistanceUnit, str]
    testes_width: tuple[Decimal, DistanceUnit, str]
    embryo_count: tuple[int, str]
    embryo_count_left: tuple[int, str]
    embryo_count_right: tuple[int, str]
    crown_rump_length: tuple[Decimal, DistanceUnit, str]
    scars: str
    reproductive_data: str

    def __init__(self):
        pass

    def __init__(self, record):
        self.guid = SheetParser.parse_mvz_guid(record["MVZ #"])
        self.collectors = record["collector"]

        distance_unit = DistanceUnit.from_string(record["unit"])

        self.total_length = SheetParser.parse_numerical_attribute(record["total"],
                                                             DistanceUnit.split_value,
                                                             distance_unit,
                                                             DistanceUnit.MILLIMETERS)

        self.tail_length = SheetParser.parse_numerical_attribute(record["tail"],
                                                             DistanceUnit.split_value,
                                                             distance_unit,
                                                             DistanceUnit.MILLIMETERS)

        self.hind_foot_with_claw = SheetParser.parse_numerical_attribute(record["hf"],
                                                             DistanceUnit.split_value,
                                                             distance_unit,
                                                             DistanceUnit.MILLIMETERS)

        self.ear_from_notch = SheetParser.parse_numerical_attribute(record["Notch"],
                                                             DistanceUnit.split_value,
                                                             distance_unit,
                                                             DistanceUnit.MILLIMETERS)
        
        self.ear_from_crown = SheetParser.parse_numerical_attribute(record["Crown"],
                                                             DistanceUnit.split_value,
                                                             distance_unit,
                                                             DistanceUnit.MILLIMETERS)
        
        weight_unit = WeightUnit.from_string(record["units"])

        self.weight = SheetParser.parse_numerical_attribute(record["wt"],
                                                             WeightUnit.split_value,
                                                             weight_unit,
                                                             WeightUnit.GRAMS)
        
        self.testes_length = SheetParser.parse_numerical_attribute(record["testes L"],
                                                             DistanceUnit.split_value,
                                                             distance_unit,
                                                             DistanceUnit.MILLIMETERS)

        self.testes_width = SheetParser.parse_numerical_attribute(record["testes W"],
                                                             DistanceUnit.split_value,
                                                             distance_unit,
                                                             DistanceUnit.MILLIMETERS)
        
        self.crown_rump_length = SheetParser.parse_numerical_attribute(record["emb CR"],
                                                             DistanceUnit.split_value,
                                                             distance_unit,
                                                             DistanceUnit.MILLIMETERS)
        
        self.unformatted_measurements = record["unformatted measurements"]
        
    def export_attributes(self, attribute_date) -> list:
        attributes = []
        unparsed_values = []

        for value, attribute_type in [(self.total_length, "total length"),
                                      (self.tail_length, "tail length"),
                                      (self.hind_foot_with_claw, "hind foot with claw"),
                                      (self.ear_from_notch, "ear from notch"),
                                      (self.ear_from_crown, "ear from crown"),
                                      (self.weight, "weight")]:
            if value[0] is not None:
                attributes.append({
                    "guid": self.guid,
                    "attribute": attribute_type,
                    "attribute_value": str(value[0]),
                    "attribute_units": value[1].value,
                    "attribute_date": attribute_date,
                    "attribute_remark": value[2],
                    "determiner": self.collectors,
                })

            elif value[2] is not None:
                unparsed_values.append(f"\"{attribute_type}\": \"{value[2]}\"")

        if self.unformatted_measurements is not None:
            unparsed_values.append(self.unformatted_measurements)

        if len(unparsed_values) > 0:
            attributes.append({
                "guid": self.guid,
                "attribute": "unformatted measurements",
                "attribute_value": ", ".join(unparsed_values),
                "attribute_date": attribute_date,
                "determiner": self.collectors,
            })

        return attributes


def import_excel(file_name):
    accession_data = pd.read_excel(file_name, dtype=str)
    accession_data = accession_data.to_dict(orient="records")

    if len(accession_data) == 0:
        return

    missing_columns = SheetParser.verify_columns_exist(accession_data[0].keys())
    if len(missing_columns) > 0:
        print(f"Missing columns in {file_name}", missing_columns)

    failures = set()
    attributes = []
    needs_review = []
    for raw_record in accession_data:
        record = SheetParser.extract_record(raw_record)
        specimen = Specimen(record)
        attributes.extend(specimen.export_attributes(None))
    
    if len(failures) != 0:
        for failure in failures:
            print(failure)

    if len(needs_review) > 0:
        for row in needs_review:
            print(row)

    return attributes


def main():
    accession_files = glob.glob(".\\data\\*.xlsx")

    attributes = []
    for accession_file in accession_files:
        print(accession_file)
        attributes.extend(import_excel(file_name=accession_file))

    csv_dataframe = pd.DataFrame.from_records(attributes)
    csv_dataframe.to_csv(f"./output/attributes.csv", index=False)


if __name__ == "__main__":
    main()