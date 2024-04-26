import sqlite3
import glob
import pandas as pd
import datetime
import math
import re

from dateutil.parser import parse

def none_if_empty(value):
    if isinstance(value, str):
        value = value.strip()

    if value == "" or value == "not recorded" or value == "Not recorded" or (isinstance(value, float) and math.isnan(value)):
        return None
    
    return value

def add_or_none(value1, value2):
    if value1 is not None and value2 is not None:
        return value1 + value2
    elif value1 is not None != value2 is not None:
        raise Exception("One side is None but not the other!!", value1, value2)
    else:
        return None
    
def float_or_none(value):
    if isinstance(value, str):
        if none_if_empty(value) is not None:
            try:
                float(value)
            except:
                print(value)
        value = re.sub(r'[^0-9]', '', value)

    if none_if_empty(value) is None:
        return None
       
    if not isinstance(value, float):
        value = float(value)

    return value

def import_excel(file_name, database):
    accession_data = pd.read_excel(file_name, dtype=str)
    accession_data = accession_data.to_dict(orient="records")

    for specimen in accession_data:
        try:
            record = {
                "catalog_number": int(specimen["MVZ #"])
            }

            if "sci name" in specimen:
                record["scientific_name"] = none_if_empty(specimen["sci name"])
            elif "SCIENTIFIC_NAME" in specimen:
                record["scientific_name"] = none_if_empty(specimen["SCIENTIFIC_NAME"])
            elif "scientific name" in specimen:
                record["scientific_name"] = none_if_empty(specimen["scientific name"])
            elif "scientific_name" in specimen:
                record["scientific_name"] = none_if_empty(specimen["scientific_name"])
            else:
                raise Exception("No scientific name column for specimen", specimen)
            
            if record["scientific_name"] is None:
                raise Exception("No scientific name for specimen", specimen)

            record["country"] = None

            if "state" in specimen:
                record["state_prov"] = none_if_empty(specimen["state"])
            elif "STATE_PROV" in specimen:
                record["state_prov"] = none_if_empty(specimen["STATE_PROV"])
            elif "state_prov" in specimen:
                record["state_prov"] = none_if_empty(specimen["state_prov"])
            else:
                raise Exception("No state_prov column for specimen", specimen)

            if "county" in specimen:
                record["county"] = none_if_empty(specimen["county"])
            elif "COUNTY" in specimen:
                record["county"] = none_if_empty(specimen["COUNTY"])
            else:
                record["county"] = None

            record["latitude"] = None
            record["longitude"] = None

            if "collector" in specimen:
                record["collector"] = specimen["collector"]
            elif "COLLECTORS" in specimen:
                record["collector"] = specimen["COLLECTORS"]

            if "date" in specimen:
                date = specimen["date"]
            elif "VERBATIM_DATE" in specimen:
                date = specimen["VERBATIM_DATE"]
            elif "ended_date" in specimen:
                date = specimen["ended_date"]

            if date == "not recorded" or date == "Unknown":
                record["date"] = None
            elif isinstance(date, datetime.date):
                record["date"] = date.strftime('%Y-%m-%d')
            elif isinstance(date, int) and date > 1000 and date < 2025:
                record["date"] = str(date)
            else:
                record["date"] = parse(date).strftime('%Y-%m-%d')

            record["sex"] = None

            record["total_length"] = float_or_none(specimen["total"])
            record["tail_length"] = float_or_none(specimen["tail"])
            record["hind_foot_with_claw"] = float_or_none(specimen["hf"])
            record["ear_from_notch"] = float_or_none(specimen["ear"]) if none_if_empty(specimen["ear"]) is not None else float_or_none(specimen["Notch"])
            record["ear_from_crown"] = float_or_none(specimen["Crown"])
            record["unit"] = ["unit"] if none_if_empty(specimen["unit"]) is not None else "mm"
            record["weight"] = specimen["wt"]
            record["weight_unit"] = specimen["units"] if none_if_empty(specimen["units"]) != "" else "g"

            if "testis L" in specimen:
                record["testes_length"] = float_or_none(specimen["testis L"])
            elif "testes L" in specimen:
                record["testes_length"] = float_or_none(specimen["testes L"])

            if "testis W" in specimen:
                record["testes_width"] = float_or_none(specimen["testis W"])
            elif "testis W" in specimen:
                record["testes_width"] = float_or_none(specimen["testis W"])
            elif "testis R" in specimen:
                record["testes_width"] = float_or_none(specimen["testis R"])


            record["embryo_count"] = None
            record["embryos_left"] = int(specimen["embs L"]) if none_if_empty(specimen["embs L"]) is not None else None
            record["embryos_right"] = int(specimen["embs R"]) if none_if_empty(specimen["embs R"]) is not None else None
            record["embryo_count"] = add_or_none(record["embryos_left"], record["embryos_right"])

            record["crown_rump_length"] = None

            record["skin_tag_checked"] = specimen["skin tag checked? (or no skin tag available)"]


        except:
            print(file_name)
            print(specimen)
            raise
        
    #     print(specimen)
    #     break
    # #     database.execute("""
    # #         INSERT INTO specimen VALUES (:)
    # # """)


def main():
    conn = sqlite3.connect("ranges.db")

    accession_files = glob.glob(".\\data\\*.xlsx")

    for accession_file in accession_files:
        import_excel(file_name=accession_file, database=conn)


if __name__ == "__main__":
    main()