# orders_schema.py
from models.avro_schema_generator import AvroSchemaGenerator

orders_schema = {
    "order_id":  ["null", "string"],
    "customer_id":  ["null", "string"],
    "order_date": ["null", "string", {"type":"int","logicalType":"date"}],
    "total_amount": "float"
}
key_orders_schema = {
    "type": "record",
    "name": "KeySchemaOrder",
    "fields": [{"name": "orders", "type": "string"}]
}
orders_avro_schema = AvroSchemaGenerator.generate_schema("Orders", orders_schema)
