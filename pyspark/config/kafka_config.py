class KafkaConfig:
    def __init__(self, topic, bootstrap_servers, schema_registry_url, schema_subject):
        self.topic = topic
        self.bootstrap_servers = bootstrap_servers
        self.schema_registry_url = schema_registry_url
        self.schema_subject = schema_subject
