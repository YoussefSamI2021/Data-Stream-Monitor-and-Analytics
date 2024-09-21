# avro_schema_generator.py

class AvroSchemaGenerator:
    @staticmethod
    def generate_schema(name, fields):
        schema = {
            "type": "record",
            "name": name,
            "fields": [{"name": k, "type": v} for k, v in fields.items()]
        }
        return schema
