import requests
from confluent_kafka import Producer
import json
import time
import math

# Kafka configuration
kafka_brokers = '18.189.79.27:9092,18.189.79.27:9093,18.189.79.27:9094'
kafka_topic = 'statsd-metrics'

# StatsD Exporter configuration
statsd_exporter_url = 'http://98.82.44.70:9123/metrics'

# Create Kafka producer
producer = Producer({'bootstrap.servers': kafka_brokers})

def delivery_report(err, msg):
    """Callback for Kafka message delivery."""
    if err is not None:
        print(f"Message delivery failed: {err}")
    else:
        print(f"Message delivered to {msg.topic()} [{msg.partition()}]")

def scrape_and_send_metrics():
    try:
        # Scrape metrics from statsd-exporter
        response = requests.get(statsd_exporter_url)
        response.raise_for_status()  # Raise an error if the request failed
        metrics = response.text

        # Initialize dictionary to hold the metrics in JSON format
        metrics_data = {}

        # List of metrics to include
        include_metrics = [
            "af_agg_dag_processing_import_errors",
            "airflow_job_start",
            "af_agg_ti_start",
            "af_agg_ti_failures",
            "af_agg_ti_successes",
            "af_agg_ti_finish",
            "airflow_ti_finish",
            "af_agg_dagbag_size",
            "af_agg_dag_task_duration_"
        ]

        # Process each line of metrics
        for line in metrics.splitlines():
            if line.startswith('#') or not line.strip():
                continue  # Skip comments and empty lines

            metric_name, metric_value = line.split(' ', 1)

            # Check if metric name is in the list of metrics to include
            if not any(metric_name.startswith(name) for name in include_metrics):
                continue

            # Extract labels if they exist (between curly braces)
            if '{' in metric_name:
                metric_name, labels_str = metric_name.split('{', 1)
                labels_str = labels_str.rstrip('}')
                labels = dict(label.split('=') for label in labels_str.split(','))
                labels = {k: v.strip('"') for k, v in labels.items()}  # Remove quotes from label values
            else:
                labels = {}

            # Handle "NaN" or null values by replacing them with 0
            try:
                value = float(metric_value.strip())
                if math.isnan(value):  # Check if the value is NaN
                    value = 0
            except (ValueError, TypeError):
                value = 0  # Handle cases where the value is not a valid float

            # Add the metric to the dictionary
            if metric_name not in metrics_data:
                metrics_data[metric_name] = []
            metrics_data[metric_name].append({
                'labels': labels,
                'value': value
            })

        # Convert the collected metrics to JSON format
        metrics_json = json.dumps(metrics_data)

        # Send the entire JSON message to Kafka as one record
        producer.produce(kafka_topic, metrics_json.encode('utf-8'), callback=delivery_report)
        producer.poll(0)

    except requests.exceptions.RequestException as e:
        print(f"Failed to scrape metrics: {e}")

if __name__ == '__main__':
    while True:
        scrape_and_send_metrics()
        producer.flush()  # Ensure all messages are sent
        time.sleep(20)  # Scrape every 1 second

