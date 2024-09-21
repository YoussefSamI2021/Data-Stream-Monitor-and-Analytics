from confluent_kafka.schema_registry import SchemaRegistryClient

class SchemaRegistryUtil:
    @staticmethod
    def get_avro_schema(kafka_config, topic, is_key=False):
        """Retrieve the latest schema for key or value for a given topic"""
        sr_client = SchemaRegistryClient({'url': kafka_config.schema_registry_url})
        subject = kafka_config.schema_subjects[topic]['key' if is_key else 'value']
        latest_version = sr_client.get_latest_version(subject)
        return latest_version.schema.schema_str
