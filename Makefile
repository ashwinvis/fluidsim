

develop:
	python setup.py develop

clean_so:
	find fluidsim -name "*.so" -delete

clean_pyc:
	find fluidsim -name "*.pyc" -delete
	find fluidsim -name "__pycache__" -type d | xargs rm -r

clean:
	rm -rf build

cleanall: clean clean_so

tests:
	python -m unittest discover

tests_mpi:
	mpirun -np 2 python -m unittest discover

build_coverage:
	@echo "Warning! Cython extensions with linetrace enabled can make the code slow"
	@echo "Run `make clean_so develop` after coverage tests for practical use"
	python setup.py build_ext --force --inplace --define CYTHON_TRACE_NOGIL

tests_coverage:
	mkdir -p .coverage
	coverage run -p -m unittest discover
	mpirun -np 2 coverage run -p -m unittest discover

report_coverage:
	coverage combine
	coverage report
	coverage html
	coverage xml
	@echo "Code coverage analysis complete. View detailed report:"
	@echo "file://${PWD}/.coverage/index.html"

coverage: build_coverage tests_coverage report_coverage

install:
	python setup.py install
