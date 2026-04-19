PYTHON ?= python

install:
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -r requirements.txt

serve:
	uvicorn app.api:app --reload

cli:
	$(PYTHON) cli.py "$(PROMPT)"

test:
	$(PYTHON) -m unittest discover -s tests -p "test_*.py"

compile:
	$(PYTHON) -m compileall app cli.py
