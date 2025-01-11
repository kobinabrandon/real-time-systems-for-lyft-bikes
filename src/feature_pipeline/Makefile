server:
	poetry run python server.py --city_name portland --feed_name free-bikes 

client:
	poetry run python client.py


station-data:
	poetry run python server.py --city_name portland --feed_name station_information 


produce-station-info-portland:
	poetry run python producer.py --city_name portland --feed_name station_information  

produce-station-info-dc:
	poetry run python producer.py --city_name washington_dc --feed_name station_information  

produce-station-info-chicago:
	poetry run python producer.py --city_name chicago --feed_name station_information  

produce-station-info-columbus:
	poetry run python producer.py --city_name columbus --feed_name station_information  


produce-free-bikes-portland:
	poetry run python producer.py --city_name portland --feed_name free_bike_status 

produce-free-bikes-dc:
	poetry run python producer.py --city_name washington_dc --feed_name free_bike_status  

produce-free-bikes-chicago:
	poetry run python producer.py --city_name chicago --feed_name free_bike_status 

produce-free-bikes-columbus:
	poetry run python producer.py --city_name columbus --feed_name free_bike_status 

