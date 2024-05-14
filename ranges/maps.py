import csv
import json
import os

import requests

import pandas as pd
import numpy as np

API_KEY = os.environ["GOOGLE_MAPS_API_KEY"]

CACHED_LOCATIONS = {}

def get_location_info(latitude: float, longitude: float) -> dict:
    keyname = f"{latitude}_{longitude}"

    if keyname not in CACHED_LOCATIONS:
        response = requests.get(f"https://maps.googleapis.com/maps/api/geocode/json?latlng={latitude},{longitude}&key={API_KEY}")
        CACHED_LOCATIONS[keyname] = response.json()

    return CACHED_LOCATIONS[keyname]

def extract_location_of_type(location_info, location_type) -> str:
    for location in location_info["results"]:
        for component in location["address_components"]:
            if location_type in component["types"]:
                return component["long_name"]

    raise ValueError(f"Could not find {location_type} in location info", location_type, location_info)


def pull_raw_locations():
    specimens = pd.read_csv("misplaced_specimens.csv")
    specimens = specimens.replace({np.nan: None}).to_dict(orient="records")

    results = []

    for specimen in specimens:
        print(specimen["guid"], specimen["dec_lat"], specimen["dec_long"])
        specimen["location_info"] = get_location_info(specimen["dec_lat"], specimen["dec_long"])
        results.append(specimen)
        
    with open("raw_located_specimens.json", "w", encoding="utf8") as out_file:
        json.dump(results, out_file, indent=4)

def process_raw_locations():
    with open("raw_located_specimens.json", "r", encoding="utf8") as in_file:
        specimens = json.load(in_file)
    
    results = []

    for specimen in specimens:
        if specimen["country"] is None:
            try:
                specimen["country"] = extract_location_of_type(specimen["location_info"], "country")
            except ValueError as err:
                print("No country found for guid", specimen["guid"])

        if specimen["state_prov"] is None:
            try:
                specimen["state_prov"] = extract_location_of_type(specimen["location_info"], "administrative_area_level_1")
            except ValueError as err:
                print("No state_prov found for guid", specimen["guid"])

        del specimen["location_info"]

        results.append(specimen)

    csv_dataframe = pd.DataFrame.from_records(results)
    csv_dataframe.to_csv(f"./found_specimens.csv", index=False)
    


if __name__ == "__main__":
    process_raw_locations()
