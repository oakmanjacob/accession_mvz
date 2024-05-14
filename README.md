# MVZ Accession Processing for Arctos
Utility scripts to process accession spreadsheets from the UC Berkeley MVZ into an uploadable format for ArctosDB

## Setup
```
pip install -r requirements.txt
```

## Usage
```
python process_accession.py
```

## Output Format (CSV)
Uploading to Arctos requires attributes to be split into two files.
 1. The first contains all numerical values and the corresponding units.
 2. The second contains all other attributes which are stored as plain text and don't have units.

For example:

14609_numerical_attributes.csv

| guid            | attribute    | attribute_value | attribute_units | attribute_date | determiner      |
| --------------- | ------------ | --------------- | --------------- | -------------- | --------------- |
| MVZ:Mamm:224127 | total length | 192             | mm              | 2009-09-15     | James L. Patton |
| MVZ:Mamm:224127 | weight       | 41              | g               | 2009-09-15     | James L. Patton |
| MVZ:Mamm:224227 | total length | 216             | mm              | 2009-09-15     | James L. Patton |

14609_text_attributes.csv

| guid            | attribute         | attribute_value             | attribute_date | determiner      |
| --------------- | ----------------- | --------------------------- | -------------- | --------------- |
| MVZ:Mamm:224127 | reproductive data | t=3x2 mm                    | 2009-09-15     | James L. Patton |
| MVZ:Mamm:224226 | reproductive data | post lactating, scars 2R-2L | 2009-09-15     | James L. Patton |
| MVZ:Mamm:224227 | reproductive data | post lactating, scars 2R-1L | 2009-09-15     | James L. Patton |

## Contributors
- Jacob Oakman
- Tokay Alberts