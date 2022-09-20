all: generate parse cleanup

generate:
	python generate.py --zip=500 --xml=500

parse:
	python parse.py
	head -n5 levels.csv
	head -n11 objects.csv

cleanup:
	rm *.zip
	rm *.csv
