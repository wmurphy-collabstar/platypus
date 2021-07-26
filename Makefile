help:
	@echo "Please use 'make <target>' where <target> is one of:"
	@echo "  lint       to run content style checks"
	@echo "  nbclean    to clean diffs with notebooks against origin/main"

lint:
	@echo "Running content style checks"
	bash test/content/code_style.sh
	python3 test/content/goals.py

nbclean:
	@echo "Cleaning notebook diffs relative to origin/main"
	python3 test/content/nbclean.py

nbclean-test:
	@echo "Checking notebooks against origin/main"
	python3 test/content/nbclean.py --check
