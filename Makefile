flake:
	flake8 . --config .flake8.ini


clean-pyc:
	rm -f `find . -type f -name '*.py[co]' `


clean: clean-pyc
	rm -rf `find . -name __pycache__`
	rm -f `find . -type f -name '*~' `
	rm -f `find . -type f -name '.*~' `
	rm -f `find . -type f -name '@*' `
	rm -f `find . -type f -name '#*#' `
	rm -f `find . -type f -name '*.orig' `
	rm -f `find . -type f -name '*.rej' `
	rm -f .coverage
	rm -rf coverage
	rm -rf build
	rm -rf cover
	rm -rf dist
