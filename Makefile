.PHONY: setup activate run-fifo run-lifo verify clean

# Create venv and install deps
setup:
	python3 -m venv .venv
	. .venv/bin/activate; python -m pip install --upgrade pip; pip install -r requirements.txt

# Echo activation command (can't persist env from make)
activate:
	@echo "Run: source .venv/bin/activate"

# Verify imports
verify:
	. .venv/bin/activate; python verify_imports.py

# Run examples
run-fifo:
	. .venv/bin/activate; python calculate_pnl.py trades.csv fifo

run-lifo:
	. .venv/bin/activate; python calculate_pnl.py trades.csv lifo

clean:
	rm -rf .venv __pycache__ .pytest_cache

test:
	. .venv/bin/activate; pytest -q
