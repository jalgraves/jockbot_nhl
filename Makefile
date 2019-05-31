.PHONY: all test clean

test:
		nosetests test/test_jockbot_nhl.py

clean:
		rm -rf build/
		rm -rf dist/
		rm -rf *.egg-info/

dist:
		python37 setup.py sdist bdist_wheel

upload:
		twine upload --repository pypi dist/*

rebase:
		git checkout master && git fetch origin && git rebase origin/master
