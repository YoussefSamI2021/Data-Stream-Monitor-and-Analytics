import csv
import time
from datetime import datetime
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry import Schema
from confluent_kafka import SerializingProducer
from confluent_kafka.schema_registry.avro import AvroSerializer

class KafkaClient:
    def __init__(self, topic, file_path, schema_str, **kwargs):
        self.topic = topic
        self.schema_str = schema_str
        self.kwargs = kwargs.get('kafka_args')
        self.file_path = file_path

    def configure_schema_registry(self):
        sr_client = SchemaRegistryClient({"url": self.kwargs['schema_registry_url']})
        schema = Schema(self.schema_str, schema_type="AVRO")
        try:
            latest_schema = sr_client.get_latest_version(self.topic)
            if schema.schema_str != latest_schema.schema.schema_str:
                sr_client.register_schema(self.topic, schema)
        except Exception:
            sr_client.register_schema(self.topic, schema)
        return sr_client

    def write_avro_serializer(self, sr_client):
        return AvroSerializer(sr_client, self.schema_str, conf={'auto.register.schemas': True})

    def configure_kafka_producer(self, serializer):
        return SerializingProducer({
            'bootstrap.servers': self.kwargs['bootstrap_servers'],
            'value.serializer': serializer,
            'security.protocol': 'plaintext',
            'delivery.timeout.ms': 120000,
            'enable.idempotence': 'true'
        })

    def parse_row(self, row):
        return {
            'index': int(row['index']),
            'Order_ID': row['Order ID'],
            'Date': datetime.strptime(row['Date'], '%m-%d-%y').date(),
            'Status': row['Status'],
            'Fulfilment': row['Fulfilment'],
            'Sales_Channel': row['Sales Channel '],
            'ship_service_level': row['ship-service-level'],
            'Style': row['Style'],
            'SKU': row['SKU'],
            'Category': row['Category'],
            'Size': row['Size'],
            'ASIN': row['ASIN'],
            'Courier_Status': row['Courier Status'],
            'Qty': int(row['Qty']) if row['Qty'] else None,
            'Amount': float(row['Amount']) if row['Amount'] else None,
            'ship_city': row['ship-city'],
            'ship_state': row['ship-state'],
            'ship_postal_code': str(row['ship-postal-code']) if row['ship-postal-code'] else None,
            'promotion_ids': row['promotion-ids'],
            'B2B': row['B2B'].lower() == 'true' if row['B2B'] else None,
        }

    def send_file_to_kafka(self, producer):
        with open(self.file_path, 'r', encoding="ISO-8859-1") as csvfile:
            reader = csv.DictReader(csvfile)
            batch = []
            batch_size = 10

            for row in reader:
                batch.append(self.parse_row(row))
                if len(batch) == batch_size:
                    for data in batch:
                        producer.produce(self.topic, value=data)
                    producer.flush()
                    batch.clear()
                    time.sleep(0.5)

            if batch:
                for data in batch:
                    producer.produce(self.topic, value=data)
                producer.flush()
        return "File sent"

def send_data_to_kafka(topic, file_path, schema_str, **kwargs):
    kafka_client = KafkaClient(topic, file_path, schema_str, **kwargs)
    sr_client = kafka_client.configure_schema_registry()
    avro_serializer = kafka_client.write_avro_serializer(sr_client)
    producer = kafka_client.configure_kafka_producer(avro_serializer)
    kafka_client.send_file_to_kafka(producer)
    return "Process completed"
