.PHONY: setup pipeline dashboard

setup:
	pip3 install -r requirements.txt

pipeline:
	python3 load_data.py
	python3 data_overview.py
	python3 stat_analysis.py
	python3 subset_analysis.py

dashboard:
	python3 dashboard.py