all: generate parse clean

generate:
	python generate.py --zip=5000 --xml=1000

parse:
	time python parse.py --cpu=1
	time python parse.py
	head -n5 levels.csv
	head -n11 objects.csv

clean:
	rm *.zip
	rm *.csv
