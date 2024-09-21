# products_schema.py
from models.avro_schema_generator import AvroSchemaGenerator

products_schema = {
    "product_id": "string",
    "name":  "string",
    "category":  ["null", "string"],
    "price": ["null", "float"],
}
key_products_schema = {
    "type": "record",
    "name": "KeySchemaProduct",
    "fields": [{"name": "products", "type": "string"}]
}
products_avro_schema = AvroSchemaGenerator.generate_schema("Products", products_schema)
