#! /bin/bash
docker-compose up -d
docker-compose exec mysql_udf cp /mysqludf/clip_api.so /usr/lib/mysql/plugin/
docker-compose exec mysql_udf cp /mysqludf/sim_api.so /usr/lib/mysql/plugin/
docker-compose exec mysql_udf python3 /mysqludf/pyserver.py