# payments_schema.py
from models.avro_schema_generator import AvroSchemaGenerator

payments_schema = {
    "payment_id":  ["null", "string"],
    "order_id":  ["null", "string"],
    "payment_date":["null", "string", {"type":"int","logicalType":"date"}],
    "amount": ["null", "float"],
    "payment_method":  ["null", "string"]
}
key_payments_schema = {
    "type": "record",
    "name": "KeySchemaPayment",
    "fields": [{"name": "payments", "type": "string"}]
}
payments_avro_schema = AvroSchemaGenerator.generate_schema("Payments", payments_schema)
