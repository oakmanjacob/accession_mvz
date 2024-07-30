import sqlparse

attributes = ["total length", "tail length", "hind foot with claw", "ear from notch", "ear from crown", "weight", "reproductive data", "unformatted measurements"]
guid_prefix = "MVZ:Mamm"
species = "Peromyscus maniculatus"

fields = ["flat.guid", "flat.subspecies", "CAST(flat.cat_num as INTEGER) as catalognumberint", "flat.collectors", "state_prov", "county", "flat.spec_locality", "collectornumber","verbatim_date", "parts", "sex"]
fields.extend([f"a{key}.attribute_value as \"{value}\"" for key, value in enumerate(attributes)])

tables = ["flat"]
tables.extend([f"LEFT OUTER JOIN (SELECT * FROM attributes WHERE attribute_type = '{value}') as a{key} ON flat.collection_object_id = a{key}.collection_object_id" for key, value in enumerate(attributes)])

query = "SELECT * FROM (SELECT " + ", ".join(fields) + " FROM " + " ".join(tables) + " WHERE guid_prefix LIKE '" + guid_prefix + "' AND species LIKE '" + species + "' AND country in ('United States','Mexico','Canada', 'NULL') AND state_prov in ('Alaska','Alberta','Arizona','Arkansas','British Columbia','California','Colorado','Idaho','Illinois','Kansas','Mexico','Michigan','Montana','Nebraska','New Mexico','North Dakota','Nevada','Oregon', 'Oklahoma','Saskatchewan','South Dakota','Texas','Utah','Washington','Wyoming', 'Aguascalientes', 'Baja California','Baja California Sur','Campeche', 'Chiapas','Chihuahua','Coahuila','Colima', 'Durango', 'Guanajuato', 'Guerrero','Hidalgo','Jalisco','México','México City','Michoacán','Morelos','Nayarit','Nuevo León','Oaxaca','Puebla','Querétaro', 'Quintana Roo','Sinaloa','Sonora','San Luis Potosi', 'Tamaulipas','Tlaxcala', 'Veracruz','Yucatán','Zacatecas')) as specimen_data"

print(sqlparse.format(query, reindent=True, keyword_case='upper'))
