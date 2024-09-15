# *** PySpark-ec2 ***

* Configurations:- 
* user : ubuntu
* PySpark ip is : 54.157.252.103
* spark ui : 54.157.252.103:9090


## For connect ssh remote 

- ssh -i keys/pyspark.pem ubuntu@54.157.252.103

## For upload files/Dir to server 

- scp -i ../keys/pyspark.pem -r dirYouwantUpload ubuntu@54.157.252.103:/home/ubuntu/
- scp -i ../keys/pyspark.pem  fileYouwantUpload ubuntu@54.157.252.103:/home/ubuntu/PySpark 

## For download files/Dir to server 

- scp -i ../keys/pyspark.pem -r ubuntu@54.157.252.103:/home/ubuntu/*  ./pyspark
- scp -i ../keys/pyspark.pem  ubuntu@54.157.252.103:/home/ubuntu/PySpark     # fileYou want Upload 

## Command used for put app in server and run it 

- spark-submit --master spark://spark-master:7077 --packages com.github.jnr:jnr-posix:3.1.15,org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1 spark_stream.py

- docker exec -it spark-master bash #to login container

- docker exec -it spark-master bash spark-submit --master spark://spark-master:7077 --packages com.github.jnr:jnr-posix:3.1.15,org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0 spark_stream.py 

- docker exec -it spark-master spark-submit --master spark://spark-master:7077 --packages com.github.jnr:jnr-posix:3.1.15,org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0,org.apache.hadoop:hadoop-aws:3.3.4,com.amazonaws:aws-java-sdk-bundle:1.12.464  spark_stream_v2.py

- docker exec -it spark-master spark-submit --master spark://spark-master:7077 --packages com.github.jnr:jnr-posix:3.1.15,org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0,org.apache.spark:spark-avro_2.13:3.5.0,org.apache.hadoop:hadoop-aws:3.3.4,com.amazonaws:aws-java-sdk-bundle:1.12.464  spark_stream.py

- docker exec -it spark-master bash spark-submit --master spark://spark-master:7077 --packages   test.py 

- docker cp spark_stream.py spark-master:/opt/bitnami/spark

=======================================================================================================

# *** ELK-stack-ec2 ***

* Configurations:
* user : ubuntu
* elk ip is : 107.22.119.65
* els : 107.22.119.65:9200
* kibana : 107.22.119.65:5601
* els-user : admin
* els-password : admin

### for connect ssh remote 

- ssh -i keys/elk.pem ubuntu@107.22.119.65

### for upload files/Dir to server 

- scp -i ../keys/elk.pem -r # dir You want Upload  ubuntu@107.22.119.65:/home/ubuntu/elk
- scp -i ../keys/elk.pem    # file You want Upload ubuntu@107.22.119.65:/home/ubuntu/elk 

### for download files/Dir to server 

- scp -i ../keys/elk.pem -r ubuntu@107.22.119.65:/home/ubuntu/* ./elk  
- scp -i ../keys/elk.pem  ubuntu@107.22.119.65:/home/ubuntu/elk     # file You want Upload 

=======================================================================================================

#  *** Airflow-ec2 *** 

* Configurations:
* user : ubuntu
* airflow ip is : 98.82.44.70
* airflow webserver is : 98.82.44.70:8080
* Promotheus Dashboard is : 98.82.44.70:9090
* Grafana Dashboard is : 98.82.44.70:3000
* airflow statsD is : 98.82.44.70:9123
* flower UI is :    
* user : admin
* password : admin

### for connect ssh remote 

- ssh -i ./keys/airflow-pk.pem ubuntu@98.82.44.70
  
### for upload files/Dir to server 

- scp -i ../keys/airflow-pk.pem -r dirYouwantUpload ubuntu@98.82.44.70:/home/ubuntu/airflow-celery
- scp -i ../keys/airflow-pk.pem  fileYouwantUpload ubuntu@98.82.44.70:/home/ubuntu/airflow-celery 

### for download files/Dir to server 

- scp -i ../keys/airflow-pk.pem -r ubuntu@98.82.44.70:/home/ubuntu/*  ./airflow
- scp -i ../keys/airflow-pk.pem  ubuntu@98.82.44.70:/home/ubuntu/airflow-celery  fileYouwantUpload 

- mkdir -p ./dags ./logs ./plugins ./config
- echo -e "AIRFLOW_UID=$(id -u)" > .env
- docker compose up airflow-init -d
- docker compose up -d
- docker compose --profile flower up

=======================================================================================================

# *** Kafka-ec2 ***

* Configurations:
* user : ubuntu
* Kafka ip is : 18.189.79.27
* control center url is : 18.189.79.27:9021
* schema registry url is : 18.189.79.27:8081


### for connect ssh remote 

- ssh -i ./keys/kafka.pem ubuntu@18.189.79.27

### for upload files/Dir to server 

- scp -i ../keys/kafka.pem -r . ubuntu@18.189.79.27:/home/ubuntu/
- scp -i ../keys/kafka.pem  . ubuntu@18.189.79.27:/home/ubuntu/ 

### for download files/Dir to server 

- scp -i ../keys/kafka.pem -r ubuntu@18.189.79.27:/home/ubuntu/*  ./airflow   


=======================================================================================================

# *** Another important commands ***    

pip install pipreqs  # to get requirements

docker container ps -a --format "table \t{{.Names}}\t{{.Status}}"


# Build the Docker image
docker build -t metrics-scraper .

# Run the container
docker run -d --name metrics-scraper metrics-scraper


docker exec -it airflow-celery-airflow-webserver-1 pip3 install confluent-kafka fastavro ; \
docker exec -it airflow-celery-airflow-worker-1 pip3 install confluent-kafka fastavro ; \
docker exec -it airflow-celery-airflow-scheduler-1 pip3 install confluent-kafka fastavro



chmod -R 777 logs

sudo chown root:root metricbeat.yml                 # to change main user for this file 
sudo chmod 644 metricbeat.yml                       # to change permisssions 
docker volume prune                                 # to delete all volumes unused
docker container rm -f $(docker container ps -a -q) # to delete all containers even running container











