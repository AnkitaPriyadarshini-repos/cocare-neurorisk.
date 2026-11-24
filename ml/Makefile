.PHONY: all eda train evaluate explain export test retrain

PYTHON ?= python
DATASET ?= oasis
CONFIG ?= ml/config.yaml

all: eda train evaluate explain export test

retrain:
	$(PYTHON) -m ml.src.retrain --dataset $(DATASET) --config $(CONFIG)

eda:
	$(PYTHON) ml/src/generate_figures.py

train:
	$(PYTHON) -m ml.src.run_pipeline

evaluate:
	$(PYTHON) -m ml.src.run_pipeline

explain:
	$(PYTHON) -m pytest ml/tests/test_pipeline.py -k test_explainability

export:
	$(PYTHON) -c "from ml.src.export import export_model_artifacts; print('Export verified')"

test:
	$(PYTHON) -m pytest ml/tests/
