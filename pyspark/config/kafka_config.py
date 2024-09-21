class KafkaConfig:
    def __init__(self, topics, bootstrap_servers, schema_registry_url):
        self.topics = topics
        self.bootstrap_servers = bootstrap_servers
        self.schema_registry_url = schema_registry_url
        self.schema_subjects = self.generate_schema_subjects()

    def generate_schema_subjects(self):
        """Generate key and value schema subjects for each topic"""
        schema_subjects = {}
        for topic in self.topics:
            schema_subjects[topic] = {
                'key': f"{topic}-key",
                'value': f"{topic}-value"
            }
        return schema_subjects
