# Packs the package into the dist directory
package: clean doc
	python setup.py sdist

# Uninstalls the package from a local installation
uninstall:
	pip freeze | grep cvloop > /dev/null; if [ $$? -eq 0 ]; then pip uninstall cvloop -y ; fi

# Installs the package locally
install: uninstall package
	pip install dist/cvloop-0.1.0.tar.gz

# Cleans up: Removes the packed package and sanitizes the examples file.
clean:
	rm -rf dist
	python tools/sanitize_ipynb.py examples/cvloop_examples.ipynb

# Creates the documentation and updates the functions ipynb.
doc:
	python tools/create_functions_ipynb.py  examples/cvloop_functions.ipynb
