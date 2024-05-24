import glob
import pandas as pd

from decimal import Decimal

from ranges.units import DistanceUnit, WeightUnit
from ranges.sheets import SheetParser

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

    def __init__(self, record):
        self.guid = SheetParser.parse_mvz_guid(record["MVZ #"])
        self.collectors = record["collector"]

        distance_unit = DistanceUnit.from_string(record["unit"])

        self.total_length = SheetParser.parse_numerical_attribute(record["total"],
                                                             distance_unit,
                                                             DistanceUnit.MILLIMETERS)

        self.tail_length = SheetParser.parse_numerical_attribute(record["tail"],
                                                             distance_unit,
                                                             DistanceUnit.MILLIMETERS)

        self.hind_foot_with_claw = SheetParser.parse_numerical_attribute(record["hf"],
                                                             distance_unit,
                                                             DistanceUnit.MILLIMETERS)

        self.ear_from_notch = SheetParser.parse_numerical_attribute(record["Notch"],
                                                             distance_unit,
                                                             DistanceUnit.MILLIMETERS)
        
        self.ear_from_crown = SheetParser.parse_numerical_attribute(record["Crown"],
                                                             distance_unit,
                                                             DistanceUnit.MILLIMETERS)
        
        weight_unit = WeightUnit.from_string(record["units"])

        self.weight = SheetParser.parse_numerical_attribute(record["wt"],
                                                             weight_unit,
                                                             WeightUnit.GRAMS)
        
        self.testes_length = SheetParser.parse_numerical_attribute(record["testes L"],
                                                             distance_unit,
                                                             DistanceUnit.MILLIMETERS)

        self.testes_width = SheetParser.parse_numerical_attribute(record["testes W"],
                                                             distance_unit,
                                                             DistanceUnit.MILLIMETERS)

        self.embryo_count = SheetParser.parse_integer_attribute(record["emb count"])

        self.embryo_count_left = SheetParser.parse_integer_attribute(record["embs L"])

        self.embryo_count_right = SheetParser.parse_integer_attribute(record["embs R"])
        
        self.crown_rump_length = SheetParser.parse_numerical_attribute(record["emb CR"],
                                                             distance_unit,
                                                             DistanceUnit.MILLIMETERS)
        
        self.unformatted_measurements = record["unformatted measurements"]
        self.reproductive_data = record["repro comments"]
        self.scars = record["scars"]

        
    def export_attributes(self, attribute_date) -> list:
        attributes = []
        unitless_attributes = []
        unparsed_values = []

        for value, attribute_type in [(self.total_length, "total length"),
                                      (self.tail_length, "tail length"),
                                      (self.hind_foot_with_claw, "hind foot with claw"),
                                      (self.ear_from_notch, "ear from notch"),
                                      (self.ear_from_crown, "ear from crown"),
                                      (self.weight, "weight"),
                                      (self.crown_rump_length, "crown-rump length"),]:
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
            unitless_attributes.append({
                "guid": self.guid,
                "attribute": "unformatted measurements",
                "attribute_value": ", ".join(unparsed_values),
                "attribute_date": attribute_date,
                "determiner": self.collectors,
            })

        if self.reproductive_data is not None:
            unitless_attributes.append({
                "guid": self.guid,
                "attribute": "reproductive data",
                "attribute_value": self.reproductive_data,
                "attribute_date": attribute_date,
                "determiner": self.collectors,
            })

        return attributes, unitless_attributes
