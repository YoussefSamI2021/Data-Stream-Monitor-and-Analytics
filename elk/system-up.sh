#!/bin/bash
grep vm.max_map_count /etc/sysctl.conf
sudo vm.max_map_count=262144
sudo sysctl -w vm.max_map_count=262144
#create to director 
#mkdir es_data_dir
#mkdir es_log_dir
# chmod / chown


docker compose up -d
