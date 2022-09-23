all: lint generate parse clean test

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

test:
	python -m unittest parse_test.py

docker:
	docker build -t test_parse .
	docker run --memory="20m" --rm test_parse sh -c  "python generate.py --zip=50 --xml=1000; python parse.py"
	docker run --tmpfs /restricted:rw,size=10M --rm test_parse sh -c  "cp -r * /restricted/; cd /restricted/; python generate.py --zip=100 --xml=100; python parse.py"

lint:
	flake8 --max-line-length 120
	mypy *.py
