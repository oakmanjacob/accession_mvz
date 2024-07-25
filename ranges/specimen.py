import glob
import pandas as pd

from decimal import Decimal

from ranges.units import DistanceUnit, WeightUnit
from ranges.sheets import SheetParser

class CommonData:
    total_length: tuple[Decimal, DistanceUnit, str]
    tail_length: tuple[Decimal, DistanceUnit, str]
    hind_foot_with_claw: tuple[Decimal, DistanceUnit, str]
    ear_from_notch: tuple[Decimal, DistanceUnit, str]
    ear_from_crown: tuple[Decimal, DistanceUnit, str]
    weight: tuple[Decimal, WeightUnit, str]
    unformatted_measurements: str

    def __init__(self,
                 total_length,
                 tail_length,
                 hind_foot_with_claw,
                 ear_from_notch,
                 ear_from_crown,
                 weight,
                 unformatted_measurements):
        self.total_length = total_length
        self.tail_length = tail_length
        self.hind_foot_with_claw = hind_foot_with_claw
        self.ear_from_notch = ear_from_notch
        self.ear_from_crown = ear_from_crown
        self.weight = weight
        self.unformatted_measurements = unformatted_measurements

        

class ReproductiveData:
    testes_length: tuple[Decimal, DistanceUnit, str]
    testes_width: tuple[Decimal, DistanceUnit, str]
    embryo_count: tuple[int, str]
    embryo_count_left: tuple[int, str]
    embryo_count_right: tuple[int, str]
    crown_rump_length: tuple[Decimal, DistanceUnit, str]
    scars: str
    repro_comments: str

    def __init__(self,
                 testes_length: tuple[Decimal, DistanceUnit, str],
                 testes_width: tuple[Decimal, DistanceUnit, str],
                 embryo_count: tuple[int, str],
                 embryo_count_left: tuple[int, str],
                 embryo_count_right: tuple[int, str],
                 crown_rump_length: tuple[Decimal, DistanceUnit, str],
                 scars: str,
                 repro_comments: str):
        self.testes_length = testes_length
        self.testes_width = testes_width
        self.embryo_count = embryo_count
        self.embryo_count_left = embryo_count_left
        self.embryo_count_right = embryo_count_right
        self.crown_rump_length = crown_rump_length
        self.scars = scars
        self.repro_comments = repro_comments


class Specimen:
    guid: str
    collectors: str
    collected_date: str

    common_data: CommonData
    reproductive_data: ReproductiveData


    def __init__(self, guid, collectors, collected_date, common_data, reproductive_data):
        self.guid = guid
        self.collectors = collectors
        self.collected_date = collected_date

        self.common_data = common_data
        self.reproductive_data = reproductive_data
    
    def from_raw_record(raw_record):
        record = SheetParser.extract_record(raw_record)
        
        distance_unit = DistanceUnit.from_string(record["distance_unit"])
        weight_unit = WeightUnit.from_string(record["weight_unit"])

        return Specimen(
            guid = SheetParser.parse_mvz_guid(record["mvz_num"]),
            collectors = record["collector"],
            collected_date = record["date"],
            common_data = CommonData(
                total_length = SheetParser.parse_numerical_attribute(record["total_length"], distance_unit, DistanceUnit.MILLIMETERS),
                tail_length = SheetParser.parse_numerical_attribute(record["tail_length"], distance_unit, DistanceUnit.MILLIMETERS),
                hind_foot_with_claw = SheetParser.parse_numerical_attribute(record["hind_foot_with_claw"], distance_unit, DistanceUnit.MILLIMETERS),
                ear_from_notch = SheetParser.parse_numerical_attribute(record["ear_from_notch"], distance_unit, DistanceUnit.MILLIMETERS),
                ear_from_crown = SheetParser.parse_numerical_attribute(record["ear_from_crown"], distance_unit, DistanceUnit.MILLIMETERS),
                weight = SheetParser.parse_numerical_attribute(record["weight"], weight_unit, WeightUnit.GRAMS),
                unformatted_measurements = record["unformatted_measurements"]
            ),
            reproductive_data = ReproductiveData(
                testes_length = SheetParser.parse_numerical_attribute(record["testes_length"], distance_unit, DistanceUnit.MILLIMETERS),
                testes_width = SheetParser.parse_numerical_attribute(record["testes_width"], distance_unit, DistanceUnit.MILLIMETERS),
                embryo_count = SheetParser.parse_integer_attribute(record["embryo_count"]),
                embryo_count_left = SheetParser.parse_integer_attribute(record["embryo_count_left"]),
                embryo_count_right = SheetParser.parse_integer_attribute(record["embryo_count_right"]),
                crown_rump_length = SheetParser.parse_numerical_attribute(record["crown_rump_length"], distance_unit, DistanceUnit.MILLIMETERS),
                scars = record["scars"],
                repro_comments = record["repro_comments"]
            )
        )
        
    def export_attributes(self) -> list:
        attributes = []
        unitless_attributes = []
        unparsed_values = []

        for value, attribute_type in [(self.common_data.total_length, "total length"),
                                      (self.common_data.tail_length, "tail length"),
                                      (self.common_data.hind_foot_with_claw, "hind foot with claw"),
                                      (self.common_data.ear_from_notch, "ear from notch"),
                                      (self.common_data.ear_from_crown, "ear from crown"),
                                      (self.common_data.weight, "weight"),
                                      (self.reproductive_data.crown_rump_length, "crown-rump length")]:
            if value[0] is not None:
                attributes.append({
                    "guid": self.guid,
                    "attribute": attribute_type,
                    "attribute_value": str(value[0]),
                    "attribute_units": value[1].value,
                    "attribute_date": self.collected_date,
                    "attribute_remark": value[2],
                    "determiner": self.collectors,
                })

            elif value[2] is not None:
                unparsed_values.append(f"\"{attribute_type}\": \"{value[2]}\"")

        if self.common_data.unformatted_measurements is not None:
            unparsed_values.append(self.common_data.unformatted_measurements)

        if len(unparsed_values) > 0:
            unitless_attributes.append({
                "guid": self.guid,
                "attribute": "unformatted measurements",
                "attribute_value": ", ".join(unparsed_values),
                "attribute_date": self.collected_date,
                "determiner": self.collectors,
            })

        if self.reproductive_data.repro_comments is not None:
            unitless_attributes.append({
                "guid": self.guid,
                "attribute": "reproductive data",
                "attribute_value": self.reproductive_data.repro_comments,
                "attribute_date": self.collected_date,
                "determiner": self.collectors,
            })

        return attributes, unitless_attributes


class ReviewNeededException(Exception):
    pass
