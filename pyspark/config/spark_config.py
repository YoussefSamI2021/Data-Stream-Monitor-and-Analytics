from pyspark.conf import SparkConf

class SparkConfig:
    def __init__(self, app_name="DataTransformation", master="local[*]", exec_instances="10", exec_memory="28g", exec_cores="16"):
        self.conf = SparkConf().setAppName(app_name).setMaster(master) \
            .set("spark.executor.instances", exec_instances) \
            .set("spark.executor.memory", exec_memory) \
            .set("spark.executor.cores", exec_cores)
