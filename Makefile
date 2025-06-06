.PHONY: test-init-db
test-init-db:
	ENV=test python -m app.init_db

.PHONY: test
test:
	$(MAKE) test-init-db
	ENV=test PYTHONPATH=. pytest

.PHONY: init-db
init-db:
	python -m app.init_db

.PHONY: run
run:
	uvicorn app.main:app --reload
