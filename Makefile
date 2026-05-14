input_file=/home/abchtaib/Downloads/maps/easy/02_simple_fork.txt
export PYGAME_HIDE_SUPPORT_PROMPT=1

.PHONY: run install debug clean lint lint-strict

run: install
	@python3 main.py $(input_file)

install:
	@pip install pygame flake8 mypy --break-system-packages --quiet



debug:
	@python3 -m pdb main.py $(input_file)

clean:
	@rm -rf __pycache__ .mypy_cache

lint:
	@flake8 .
	@mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	@flake8 .
	@mypy . --strict