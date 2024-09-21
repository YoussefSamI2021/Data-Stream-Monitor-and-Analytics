from pyspark.conf import SparkConf

class SparkConfig:
    def __init__(self, 
                 app_name="DataTransformation", 
                 master="spark://spark-master:7077", 
                 exec_instances="2", 
                 exec_memory="2g", 
                 exec_cores="2",
                 dynamic_allocation=True,
                 enable_event_logging=True,
                 event_log_dir="/opt/bitnami/spark/spark-events",
                 log_level="INFO",
                 custom_conf=None):
        
        self.conf = SparkConf().setAppName(app_name).setMaster(master) \
            .set("spark.executor.instances", exec_instances) \
            .set("spark.executor.memory", exec_memory) \
            .set("spark.executor.cores", exec_cores) \
            .set("spark.executor.logs.rolling.maxRetainedFiles", "5") \
            .set("spark.executor.logs.rolling.strategy", "time") \
            .set("spark.executor.logs.rolling.time.interval", "daily") \
            .set("spark.driver.extraJavaOptions", f"-Dlog4j.logLevel={log_level}") \
            .set("spark.executor.extraJavaOptions", f"-Dlog4j.logLevel={log_level}")
        
        # Dynamic Allocation
        if dynamic_allocation:
            self.conf.set("spark.dynamicAllocation.enabled", "true") \
                     .set("spark.dynamicAllocation.initialExecutors", exec_instances) \
                     .set("spark.dynamicAllocation.minExecutors", "2") \
                     .set("spark.dynamicAllocation.maxExecutors", exec_instances)

        # Event Logging
        if enable_event_logging:
            self.conf.set("spark.eventLog.enabled", "true") \
                     .set("spark.eventLog.dir", event_log_dir)

        # Apply custom configurations
        if custom_conf:
            for key, value in custom_conf.items():
                self.conf.set(key, value)
    
    def get_spark_conf(self):
        return self.conf

