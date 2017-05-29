# Installs the editable version
install: uninstall package
	pip3 install -e $(CURDIR)

# Installs the packaged version
testpackage: uninstall package
	pip3 install dist/cvloop*.tar.gz

# Packs the package into the dist directory and signs it
package: clean doc
	python3 setup.py sdist
	gpg --detach-sign --armor dist/cvloop*.tar.gz

# Uninstalls the package from a local installation
uninstall:
	pip3 freeze | grep cvloop > /dev/null ; \
	if [ $$? -eq 0 ]; then \
		pip3 uninstall cvloop -y ; \
	fi

# Cleans up: Removes the packed package and sanitizes the examples file.
clean:
	rm -rf dist
	python3 tools/sanitize_ipynb.py examples/cvloop_examples.ipynb

# Creates the documentation and updates the functions ipynb.
doc:
	python3 tools/create_functions_ipynb.py  examples/cvloop_functions.ipynb

# Publishes to pypitest
testpublish: package
	@read -p "Enter the name of this package to verify upload to pypi test: " name ; \
	if [ "$$name" == "cvloop" ]; then \
		twine register -r pypitest $$(ls dist/*.tar.gz) ; \
		twine upload -r pypitest dist/* ; \
	else \
		echo 'Sorry, this was wrong. Please try again.' ; \
	fi

# Publishes to pypi
publish: package
	@read -p "Enter the name of this package to verify upload to pypi: " name ; \
	if [ "$$name" == "cvloop" ]; then \
		twine register -r pypi $$(ls dist/*.tar.gz) ; \
		twine upload -r pypi dist/* ; \
	else \
		echo 'Sorry, this was wrong. Please try again.' ; \
	fi
