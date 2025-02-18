<div align="center">
<div align="center">
<h1>TESTIFY</h1>
<br/>
Testify from Codimate aims to help efficiently increasing code coverage, by automatically generating qualified tests to enhance existing test suites.
</div>
</div>

## Codimate
Codimate's mission is to enable busy dev teams to increase and maintain their code integrity.

We offer various tools, including "Pro" versions of our open-source tools, which are meant to handle enterprise-level code complexity and are multi-repo codebase aware.

## Testify
Welcome to testify-agent. This focused project utilizes Generative AI to automate and enhance the generation of tests (currently mostly unit tests), aiming to streamline development workflows. testify-agent can run via a terminal, and is planned to be integrated into popular CI platforms.

We invite the community to collaborate and help extend the capabilities of Testify Agent, continuing its development as a cutting-edge solution in the automated unit test generation domain. We also wish to inspire researchers to leverage this open-source tool to explore new test-generation techniques.


## Table of Contents
- [News and Updates](#news-and-updates)
- [Overview](#overview)
- [Installation and Usage](#installation-and-usage)
- [Development](#development)
- [Roadmap](#roadmap)


## Overview
This tool is part of a broader suite of utilities designed to automate the creation of unit tests for software projects. Utilizing advanced Generative AI models, it aims to simplify and expedite the testing process, ensuring high-quality software development. The system comprises several components:
1. **Test Runner:** Executes the command or scripts to run the test suite and generate code coverage reports.
2. **Coverage Parser:** Validates that code coverage increases as tests are added, ensuring that new tests contribute to the overall test effectiveness.
3. **Prompt Builder:** Gathers necessary data from the codebase and constructs the prompt to be passed to the Large Language Model (LLM).
4. **AI Caller:** Interacts with the LLM to generate tests based on the prompt provided.

## Installation and Usage
### Requirements
Before you begin, make sure you have the following:
- `OPENAI_API_KEY` set in your environment variables, which is required for calling the OpenAI API.
- Code Coverage tool: A Cobertura XML code coverage report is required for the tool to function correctly.
  - For example, in Python one could use `pytest-cov`. Add the `--cov-report=xml` option when running Pytest.
  - Note: We are actively working on adding more coverage types but please feel free to open a PR and contribute to `testify_agent/CoverageProcessor.py`

If running directly from the repository you will also need:
- Python installed on your system.
- Poetry installed for managing Python package dependencies. Installation instructions for Poetry can be found at [https://python-poetry.org/docs/](https://python-poetry.org/docs/).

### Standalone Runtime
The Testify Agent can be installed as a Python Pip package or run as a standalone executable.

#### Python Pip
To install the Python Pip package directly via GitHub run the following command:
```shell
pip install git+https://github.com/PhamVuThuNguyet/ai-for-software-testing.git
```

### Repository Setup
Run the following command to install all the dependencies and run the project from source:
```shell
poetry install
```

### Running the Code
After downloading the executable or installing the Pip package you can run the Testify Agent to generate and validate unit tests. Execute it from the command line by using the following command:
```shell
testify-agent \
  --source-file-path "<path_to_source_file>" \
  --test-file-path "<path_to_test_file>" \
  --project-root "<path_to_project_root>" \
  --code-coverage-report-path "<path_to_coverage_report>" \
  --test-command "<test_command_to_run>" \
  --test-command-dir "<directory_to_run_test_command>" \
  --coverage-type "<type_of_coverage_report>" \
  --desired-coverage <desired_coverage_between_0_and_100> \
  --max-iterations <max_number_of_llm_iterations> \
  --included-files "<optional_list_of_files_to_include>"
```

You can use the example code below to try out the Testify Agent.
(Note that the [usage_examples](docs/usage_examples.md) file provides more elaborate examples of how to use the Testify Agent)

#### Python

Follow the steps in the README.md file located in the `testing_templates/python_fastapi/` directory to setup an environment, then return to the root of the repository, and run the following command to add tests to the **python fastapi** example:
```shell
testify-agent \
  --source-file-path "testing_templates/python_fastapi/app.py" \
  --test-file-path "testing_templates/python_fastapi/test_app.py" \
  --project-root "testing_templates/python_fastapi" \
  --code-coverage-report-path "testing_templates/python_fastapi/coverage.xml" \
  --test-command "pytest --cov=. --cov-report=xml --cov-report=term" \
  --test-command-dir "testing_templates/python_fastapi" \
  --coverage-type "cobertura" \
  --desired-coverage 70 \
  --max-iterations 10
```

#### Go

For an example using **go** `cd` into `testing_templates/go_webservice`, set up the project following the `README.md`.
To work with coverage reporting, you need to install `gocov` and `gocov-xml`. Run the following commands to install these tools:
```shell
go install github.com/axw/gocov/gocov@v1.1.0
go install github.com/AlekSi/gocov-xml@v1.1.0
```
and then run the following command:
```shell
testify-agent \
  --source-file-path "app.go" \
  --test-file-path "app_test.go" \
  --code-coverage-report-path "coverage.xml" \
  --test-command "go test -coverprofile=coverage.out && gocov convert coverage.out | gocov-xml > coverage.xml" \
  --test-command-dir $(pwd) \
  --coverage-type "cobertura" \
  --desired-coverage 70 \
  --max-iterations 1
```

#### Java
For an example using **java** `cd` into `testing_templates/java_gradle`, set up the project following the [README.md](testing_templates/java_gradle/README.md).
To work with jacoco coverage reporting, follow the [README.md](testing_templates/java_gradle/README.md) Requirements section:
and then run the following command:
```shell
testify-agent \
  --source-file-path="src/main/java/com/davidparry/cover/SimpleMathOperations.java" \
  --test-file-path="src/test/groovy/com/davidparry/cover/SimpleMathOperationsSpec.groovy" \
  --code-coverage-report-path="build/reports/jacoco/test/jacocoTestReport.csv" \
  --test-command="./gradlew clean test jacocoTestReport" \
  --test-command-dir=$(pwd) \
  --coverage-type="jacoco" \
  --desired-coverage=70 \
  --max-iterations=1
```

### Outputs
A few debug files will be outputted locally within the repository (that are part of the `.gitignore`)
* `run.log`: A copy of the logger that gets dumped to your `stdout`
* `test_results.html`: A results table that contains the following for each generated test:
  * Test status
  * Failure reason (if applicable)
  * Exit code, 
  * `stderr`
  * `stdout`
  * Generated test

### Additional logging
If you set an environment variable `WANDB_API_KEY`, the prompts, responses, and additional information will be logged to [Weights and Biases](https://wandb.ai/).

### Using other LLMs
This project uses LiteLLM to communicate with OpenAI and other hosted LLMs (supporting 100+ LLMs to date). To use a different model other than the OpenAI default you'll need to:
1. Export any environment variables needed by the supported LLM [following the LiteLLM instructions](https://litellm.vercel.app/docs/proxy/quick_start#supported-llms).
2. Call the name of the model using the `--model` option when calling Testify Agent.

For example (as found in the [LiteLLM Quick Start guide](https://litellm.vercel.app/docs/proxy/quick_start#supported-llms)):
```shell
export VERTEX_PROJECT="hardy-project"
export VERTEX_LOCATION="us-west"

testify-agent \
  ...
  --model "vertex_ai/gemini-pro"
```

#### OpenAI Compatible Endpoint
```shell
export OPENAI_API_KEY="<your api key>" # If <your-api-base> requires an API KEY, set this value.

testify-agent \
  ...
  --model "openai/<your model name>" \
  --api-base "<your-api-base>"
```

#### Azure OpenAI Compatible Endpoint
```shell
export AZURE_API_BASE="<your api base>" # azure api base
export AZURE_API_VERSION="<your api version>" # azure api version (optional)
export AZURE_API_KEY="<your api key>" # azure api key

testify-agent \
  ...
  --model "azure/<your deployment name>"
```

## News and Updates

### 2024-11-05:
New mode - scan an entire repo, auto identify the test files, auto collect context for each test file, and extend the test suite with new tests.
How to run:

1) Install testify-agent on your existing project venv

2) If your project doesn't have a `pyproject.toml` file, create one with:
```
[tool.poetry]
name = "testify-agent"
version = "0.0.0" # Placeholder
description = "Testify"
authors = ["pvtnguyet"]
license = "AGPL-3.0 license"
readme = "README.md"
```
3) Create a branch in your repo (we want to extend the tests on a dedicated branch)
4) cd to your repo root
5) Run the following command:
```shell

export AWS_ACCESS_KEY_ID=...
export AWS_SECRET_ACCESS_KEY=...
export AWS_REGION_NAME=...

poetry run testify-agent-full-repo \
  --project-language="python" \
  --project-root="<path_to_your_repo>" \
  --code-coverage-report-path="<path_to_your_repo>/coverage.xml" \
  --test-command="coverage run -m pytest <relative_path_to_unittest_folder> --cov=<path_to_your_repo> --cov-report=xml --cov-report=term --log-cli-level=INFO" \
  --model=bedrock/anthropic.claude-3-5-sonnet-20241022-v2:0
```

Alternatively, if you dont want to use `poetry`, replace:

`poetry run testify-agent-full-repo`

with:

`python ./venv/lib/python3.10/site-packages/testify_agent/main_full_repo.py`
(Give the path to your actual installation)

Notes:
  - `<relative_path_to_unittest_folder>` is optional, but will prevent running e2e test files if exists, which may take a long time"
  - You can use other models, like 'gpt-4o' or 'o1-mini', but recommended to use 'sonnet-3.5' as this is currently the best code model in the world.

Additional configuration options:
- `--max-test-files-allowed-to-analyze` - The maximum number of test files to analyze. Default is 20 (to avoid long running times).
- `--look-for-oldest-unchanged-test-files` - If set, the tool will sort the test files by the last modified date and analyze the oldest ones first. This is useful to find the test files that are most likely to be outdated, and for multiple runs. Default is False.


### 2024-09-29:
We are excited to announce the latest series of updates to Testify, delivering significant improvements to functionality, documentation, and testing frameworks. These updates reflect our ongoing commitment to enhancing the developer experience, improving error handling, and refining the testing processes.

#### New Features and Enhancements
* Enhanced Database Usage: Introduced a new database_usage.md document outlining the expanded capabilities of logging test results to a structured database.
* Comprehensive System Diagrams: Added a top_level_sequence_diagram.md, providing a clear visual overview of Testify's processes and workflows.
* Docker and Multi-Language Support: Several new Docker configurations and templated tests were introduced for various programming languages, including C#, TypeScript, C, and React, ensuring streamlined testing environments across multiple platforms.
* UnitTestDB Integration: The UnitTestDB.py file was added to support robust logging of test generation attempts, improving error tracking and debugging.

#### Refinements and Modifications
* Coverage Processing: Key improvements to CoverageProcessor.py modularized coverage parsing and expanded support for different coverage report formats (LCOV, Cobertura, Jacoco).
* PromptBuilder Enhancements: New CLI arguments were introduced, including options for running tests multiple times (--run-tests-multiple-times) and a report coverage feature flag for more granular control over coverage behavior.
* CI/CD Pipeline Improvements: Several GitHub workflows were modified to improve pipeline efficiency, including nightly regression tests and templated test publishing pipelines.

#### Improved Documentation
* Detailed Usage Examples: The usage_examples.md file was updated to provide more comprehensive guidance on how to effectively use Testify's features, ensuring that developers can quickly get up to speed with the latest updates.
* Configuration and Template Updates: Configuration files, such as test_generation_prompt.toml, were refined to better support the test framework and eliminate redundant instructions.

These updates signify a major leap forward in improving the ease of use, flexibility, and overall performance of Testify. We are committed to continuing to enhance the tool and providing regular updates based on feedback from our community.

### 2024-06-05:
The logic and prompts for adding new imports for the generated tests have been improved.

We also added a [usage examples](docs/usage_examples.md) file, with more elaborate examples of how to use the Testify Agent.

### 2024-06-01:
Added support for comprehensive logging to [Weights and Biases](https://wandb.ai/). Set the `WANDB_API_KEY` environment variable to enable this feature.

### 2024-05-26:
Testify now supports nearly any LLM model in the world, using [LiteLLM](#using-other-llms) package.

Notice that GPT-4 outperforms almost any open-source model in the world when it comes to code tasks and following complicated instructions.

However, we updated the post-processing scripts to be more comprehensive, and were able to successfully run the [baseline script](#running-the-code) with `llama3-8B` and `llama3-70B models`, for example.

### 2024-05-09: 
This repository is created to reproduce the implementation of TestGen-LLM, described in the paper [Automated Unit Test Improvement using Large Language Models at Meta](https://arxiv.org/abs/2402.09171).


## Development
This section discusses the development of this project.

### Versioning
Before merging to main make sure to manually increment the version number in `testify_agent/version.txt` at the root of the repository.

### Running Tests
Set up your development environment by running the `poetry install` command as you did above. 

Note: for older versions of Poetry you may need to include the `--dev` option to install Dev dependencies.

After setting up your environment run the following command:
```shell
poetry run pytest --junitxml=testLog.xml --cov=testing_templates --cov=testify_agent --cov-report=xml --cov-report=term --log-cli-level=INFO
```
This will also generate all logs and output reports that are generated in `.github/workflows/ci_pipeline.yml`.

### Running the app locally from source

#### Prerequisites
- Python3
- Poetry

#### Steps
1. If not already done, install the dependencies
    ```shell
    poetry install
    ```

2. Let Poetry manage / create the environment
    ```shell
   poetry shell
   ```

3. Run the app
    ```shell
   poetry run testify-agent \
     --source-file-path <path_to_source_file> \
     [other_options...]
    ```

Notice that you're prepending `poetry run` to your `testify-agent` command. Replace `<path_to_your_source_file>` with the
actual path to your source file. Add any other necessary options as described in
the [Running the Code](#running-the-code) section.

### Building the binary locally
You can build the binary locally simply by invoking the `make installer` command. This will run PyInstaller locally on your machine. Ensure that you have set up the poetry project first (i.e. running `poetry install`).

## Roadmap
Below is the roadmap of planned features, with the current implementation status:

- [x] Automatically generates unit tests for your software projects, utilizing advanced AI models to ensure comprehensive test coverage and quality assurance. (similar to Meta)
  - [x] Being able to generate tests for different programming languages
  - [ ] Being able to deal with a large variety of testing scenarios
  - [ ] Generate a behavior analysis for the code under test, and generate tests accordingly
  - [x] Check test flakiness, e.g. by running 5 times as suggested by TestGen-LLM
- [ ] Cover more test generation pains
  - [ ] Generate new tests that are focused on the PR changeset
  - [ ] Run over an entire repo/code-base and attempt to enhance all existing test suites
- [ ] Improve usability
  - [ ] Connectors for GitHub Actions, Jenkins, CircleCI, Travis CI, and more
  - [ ] Integrate into databases, APIs, OpenTelemetry and other sources of data to extract relevant i/o for the test generation
  - [ ] Add a setting file