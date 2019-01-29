port = 8000
tester_version = 1.1.0
npm := npm --prefix .
python = $(shell pipenv --py) # evaluate this once to improve performance in test
npm_bin = $(shell $(npm) bin)
integration_test = $(npm_bin)/take-home-integration-test
log_file = integration-test.log

pip_version = $(word 2,$(shell pipenv run pip --version))
pipenv_version = $(word 3,$(shell pipenv --version))

.PHONY: start
start:
	#pipenv shell;source setenv;python run.py
	pipenv run python run.py

$(integration_test):
	$(npm) install --no-save ./assets/c1-code-test-take-home-tester-$(tester_version).tgz

.PHONY: check-pipenv-version

ifeq ("$(pip_version) $(pipenv_version)","18.1 2018.7.1")
check-pipenv-version:
	@echo "Detected incompatible versions of pip and pipenv. Upgradeing pipenv."
	pip install --user --upgrade pipenv
endif

.PHONY: install
install: check-pipenv-version
	pipenv --bare install --dev

.PHONY: utest
utest:
	pipenv run run_utest
	#pipenv run . ./setenv;pytest ./weathertracker/


.PHONY: test
test: $(integration_test)
	node --no-warnings \
	$(integration_test) \
	features \
	--check-new \
	--command "$(python) run.py" \
	--port $(port) \
	--out-file $(log_file) \
	-- \
	--tags 'not @skip'
