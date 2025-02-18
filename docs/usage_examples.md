# Usage Examples
These working examples attempt to add more tests for the code written in this repository. In or order to properly run these examples you will need to set up your development environment by running `poetry install`. See the main README (development section) for more details.

## Example 1: Running a folder, and targeting a specific file inside it
With this example, we run the `tests/test_PromptBuilder.py` file on the entire `testify_agent` folder.
However, in post-processing we will only extract at the coverage of the `PromptBuilder.py` file, so effectively we are targeting only that file.

```shell
testify-agent \
--model "gpt-4o" \
--source-file-path "testify_agent/PromptBuilder.py" \
--test-file-path "tests/test_PromptBuilder.py" \
--code-coverage-report-path "coverage.xml" \
--test-command "poetry run pytest tests/test_PromptBuilder.py --cov=testify_agent --cov-report=xml --cov-report=term --log-cli-level=INFO --timeout=10" \
--coverage-type "cobertura" \
--desired-coverage 90 \
--max-iterations 5
```

## Example 2: Running only on a specific module

With this example, we run the `tests/test_PromptBuilder.py` file only on the `PromptBuilder` module, using a more elaborate test command:
```shell
testify-agent \
--model="gpt-4o" \
--source-file-path "testify_agent/PromptBuilder.py" \
--test-file-path "tests/test_PromptBuilder.py" \
--code-coverage-report-path "tests/coverage_prompt_builder.xml" \
--test-command "poetry run  pytest --cov=testify_agent.PromptBuilder --cov-report=xml:tests/coverage_prompt_builder.xml --cov-report=term tests/test_PromptBuilder.py --timeout=10" \
--coverage-type "cobertura" \
--desired-coverage 90 \
--max-iterations 5
```

## Example 3: Utilizing additional instructions
For complicated test files with multiple classes, it will not be clear for the AI model which class to focus on.

We can use the `--additional-instructions` flag to provide instructions to the model, so it can focus on the specific class we are interested in.

For example, the file [`testify_agent/test_UnitTestGenerator.py`](../tests/test_UnitTestGenerator.py) has two test classes - `TestUnitTestGenerator` and `TestExtractErrorMessage`.
We can use the `--additional-instructions` flag to instruct the model to focus on the `TestUnitTestGenerator` class.

```shell
testify-agent \
--model="gpt-4o" \
--source-file-path "testify_agent/UnitTestGenerator.py" \
--test-file-path "tests/test_UnitTestGenerator.py" \
--code-coverage-report-path "coverage.xml" \
--test-command "poetry run pytest tests/test_UnitTestGenerator.py --cov=testify_agent --cov-report=xml --cov-report=term --log-cli-level=INFO --timeout=5" \
--coverage-type "cobertura" \
--desired-coverage 90 \
--max-iterations 5 \
--additional-instructions="add tests to the class 'TestUnitTestGenerator'"
```

## Example 4: Adding extra context files
In some cases, the AI model may require additional context to understand the code better, in addition to the source and test file.
You can utilize the `--included-files` flag to provide additional context files to the model.

```shell
testify-agent \
--model="gpt-4o" \
--source-file-path "testify_agent/main.py" \
--test-file-path "tests/test_main.py" \
--included-files "testify_agent/TestifyAgent.py" \
--code-coverage-report-path "coverage.xml" \
--test-command "poetry run pytest tests/test_main.py --cov=testify_agent --cov-report=xml --cov-report=term --log-cli-level=INFO --timeout=10" \
--coverage-type "cobertura" \
--desired-coverage 96 \
--max-iterations  8
```

