from confluent_kafka.schema_registry import SchemaRegistryClient

class SchemaRegistryUtil:
    @staticmethod
    def get_avro_schema(kafka_config):
        """Retrieve the latest schema from Schema Registry"""
        sr_client = SchemaRegistryClient({'url': kafka_config.schema_registry_url})
        latest_version = sr_client.get_latest_version(kafka_config.schema_subject)
        return latest_version.schema.schema_str
