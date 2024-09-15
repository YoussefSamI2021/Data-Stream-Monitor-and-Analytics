import json

Schema_STR="""
{
  "type": "record",
  "name": "OrderRecord",
  "fields": [
    {"name": "index", "type": "int"},
    {"name": "Order_ID", "type": "string"},
    {"name":"Date","type":["null", "string", {"type":"int","logicalType":"date"}],"default":null},
    {"name": "Status", "type": "string"},
    {"name": "Fulfilment", "type": "string"},
    {"name": "Sales_Channel", "type": "string"},
    {"name": "ship_service_level", "type": "string"},
    {"name": "Style", "type": "string"},
    {"name": "SKU", "type": "string"},
    {"name": "Category", "type": "string"},
    {"name": "Size", "type": "string"},
    {"name": "ASIN", "type": "string"},
    {"name": "Courier_Status", "type": "string"},
    {"name": "Qty", "type": ["null", "int"], "default": null},
    {"name": "Amount", "type": ["null", "float"], "default": null},
    {"name": "ship_city", "type": "string"},
    {"name": "ship_state", "type": "string"},
    {"name": "ship_postal_code", "type": ["null", "string"], "default": null},
    {"name": "promotion_ids", "type": "string"},
    {"name": "B2B", "type": ["null", "boolean"], "default": null}
  ]
}
"""




kafka_kwargs={
        'schema_registry_url' : 'http://18.189.79.27:8081' , 
        'bootstrap_servers':'18.189.79.27:9092,18.189.79.27:9093,18.189.79.27:9094'
}

