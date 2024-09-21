# customer_schema.py
from models.avro_schema_generator import AvroSchemaGenerator

customer_schema = {
    "customer_id": "string",
    "name":  ["null", "string"],
    "email": ["null", "string"],
    "phone":  ["null", "string"],
    "address":  ["null", "string"],
    "signup_date":["null", "string", {"type":"int","logicalType":"date"}]
}
key_customer_schema = {
    "type": "record",
    "name": "KeySchemaCustomer",
    "fields": [{"name": "customers", "type": "string"}]
}
customer_avro_schema = AvroSchemaGenerator.generate_schema("Customer", customer_schema)
