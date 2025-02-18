import datetime
import os
import shutil
import sys

import wandb

from testify_agent.CustomLogger import CustomLogger
from testify_agent.ReportGenerator import ReportGenerator
from testify_agent.UnitTestDB import UnitTestDB
from testify_agent.UnitTestGenerator import UnitTestGenerator
from testify_agent.UnitTestValidator import UnitTestValidator


class TestifyAgent:
    def __init__(self, args):
        """
        Initialize the TestifyAgent class with the provided arguments and run the test generation process.

        Parameters:
            args (Namespace): The parsed command-line arguments containing necessary information for test generation.

        Returns:
            None
        """
        self.args = args
        self.logger = CustomLogger.get_logger(__name__)

        self._validate_paths()
        self._duplicate_test_file()

        # To run only a single test file, we need to modify the test command
        self.parse_command_to_run_only_a_single_test(args)

        self.test_gen = UnitTestGenerator(
            source_file_path=args.source_file_path,
            test_file_path=args.test_file_output_path,
            project_root=args.project_root,
            code_coverage_report_path=args.code_coverage_report_path,
            test_command=args.test_command,
            test_command_dir=args.test_command_dir,
            included_files=args.included_files,
            coverage_type=args.coverage_type,
            additional_instructions=args.additional_instructions,
            llm_model=args.model,
            api_base=args.api_base,
            use_report_coverage_feature_flag=args.use_report_coverage_feature_flag,
        )

        self.test_validator = UnitTestValidator(
            source_file_path=args.source_file_path,
            test_file_path=args.test_file_output_path,
            project_root=args.project_root,
            code_coverage_report_path=args.code_coverage_report_path,
            test_command=args.test_command,
            test_command_dir=args.test_command_dir,
            included_files=args.included_files,
            coverage_type=args.coverage_type,
            desired_coverage=args.desired_coverage,
            additional_instructions=args.additional_instructions,
            llm_model=args.model,
            api_base=args.api_base,
            use_report_coverage_feature_flag=args.use_report_coverage_feature_flag,
            diff_coverage=args.diff_coverage,
            comparison_branch=args.branch,
        )

    def parse_command_to_run_only_a_single_test(self, args):
        test_command = args.test_command
        if hasattr(args, "run_each_test_separately") and args.run_each_test_separately:
            test_file_relative_path = os.path.relpath(
                args.test_file_output_path, args.project_root
            )
            if (
                "pytest" in test_command
            ):  # coverage run -m pytest tests  --cov=/Users/talrid/Git/testify-agent --cov-report=xml --cov-report=term --log-cli-level=INFO --timeout=30
                ind1 = test_command.index("pytest")
                ind2 = test_command[ind1:].index("--")
                args.test_command = f"{test_command[:ind1]}pytest {test_file_relative_path} {test_command[ind1 + ind2:]}"
                print(f"\nRunning only a single test file: '{args.test_command}'")
            elif "unittest" in test_command:  #
                pass  # maybe call an llm to do that ?
            # toDo - add more test runners

    def _validate_paths(self):
        """
        Validate the paths provided in the arguments.

        Raises:
            FileNotFoundError: If the source file or test file is not found at the specified paths.
        """
        # Ensure the source file exists
        if not os.path.isfile(self.args.source_file_path):
            raise FileNotFoundError(
                f"Source file not found at {self.args.source_file_path}"
            )
        # Ensure the test file exists
        if not os.path.isfile(self.args.test_file_path):
            raise FileNotFoundError(
                f"Test file not found at {self.args.test_file_path}"
            )

        # Ensure the project root exists
        if self.args.project_root and not os.path.isdir(self.args.project_root):
            raise FileNotFoundError(
                f"Project root not found at {self.args.project_root}"
            )

        # Create default DB file if not provided
        if not self.args.log_db_path:
            self.args.log_db_path = "testify_agent_unit_test_runs.db"
        # Connect to the test DB
        self.test_db = UnitTestDB(
            db_connection_string=f"sqlite:///{self.args.log_db_path}"
        )

    def _duplicate_test_file(self):
        """
        Initialize the TestifyAgent class with the provided arguments and run the test generation process.

        Parameters:
            args (Namespace): The parsed command-line arguments containing necessary information for test generation.

        Returns:
            None
        """
        # If the test file output path is set, copy the test file there
        if self.args.test_file_output_path != "":
            shutil.copy(self.args.test_file_path, self.args.test_file_output_path)
        else:
            # Otherwise, set the test file output path to the current test file
            self.args.test_file_output_path = self.args.test_file_path

    def run(self):
        """
        Run the test generation process.

        This method performs the following steps:

        1. Initialize the Weights & Biases run if the WANDS_API_KEY environment variable is set.
        2. Initialize variables to track progress.
        3. Run the initial test suite analysis.
        4. Loop until desired coverage is reached or maximum iterations are met.
        5. Generate new tests.
        6. Loop through each new test and validate it.
        7. Insert the test result into the database.
        8. Increment the iteration count.
        9. Check if the desired coverage has been reached.
        10. If the desired coverage has been reached, log the final coverage.
        11. If the maximum iteration limit is reached, log a failure message if strict coverage is specified.
        12. Provide metrics on total token usage.
        13. Generate a report.
        14. Finish the Weights & Biases run if it was initialized.
        """
        # Check if user has exported the WANDS_API_KEY environment variable
        if "WANDB_API_KEY" in os.environ:
            # Initialize the Weights & Biases run
            wandb.login(key=os.environ["WANDB_API_KEY"])
            time_and_date = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            run_name = f"{self.args.model}_" + time_and_date
            wandb.init(project="testify-agent", name=run_name)

        # Initialize variables to track progress
        iteration_count = 0
        test_results_list = []

        # Run initial test suite analysis
        self.test_validator.initial_test_suite_analysis()
        failed_test_runs, language, test_framework, coverage_report = (
            self.test_validator.get_coverage()
        )
        self.test_gen.build_prompt(
            failed_test_runs, language, test_framework, coverage_report
        )

        # Loop until desired coverage is reached or maximum iterations are met
        while (
            self.test_validator.current_coverage
            < (self.test_validator.desired_coverage / 100)
            and iteration_count < self.args.max_iterations
        ):
            # Log the current coverage
            if self.args.diff_coverage:
                self.logger.info(
                    f"Current Diff Coverage: {round(self.test_validator.current_coverage * 100, 2)}%"
                )
            else:
                self.logger.info(
                    f"Current Coverage: {round(self.test_validator.current_coverage * 100, 2)}%"
                )
            self.logger.info(
                f"Desired Coverage: {self.test_validator.desired_coverage}%"
            )

            # Generate new tests
            generated_tests_dict = self.test_gen.generate_tests(
                failed_test_runs, language, test_framework, coverage_report
            )

            # Loop through each new test and validate it
            for generated_test in generated_tests_dict.get("new_tests", []):
                # Validate the test and record the result
                test_result = self.test_validator.validate_test(
                    generated_test, self.args.run_tests_multiple_times
                )
                test_result["prompt"] = self.test_gen.prompt[
                    "user"
                ]  # get the prompt used to generate the test so that it is stored in the database
                test_results_list.append(test_result)

                # Insert the test result into the database
                self.test_db.insert_attempt(test_result)

            # Increment the iteration count
            iteration_count += 1

            # Check if the desired coverage has been reached
            if self.test_validator.current_coverage < (
                self.test_validator.desired_coverage / 100
            ):
                # Run the coverage tool again if the desired coverage hasn't been reached
                self.test_validator.run_coverage()

        # Log the final coverage
        if self.test_validator.current_coverage >= (
            self.test_validator.desired_coverage / 100
        ):
            self.logger.info(
                f"Reached above target coverage of {self.test_validator.desired_coverage}% (Current Coverage: {round(self.test_validator.current_coverage * 100, 2)}%) in {iteration_count} iterations."
            )
        elif iteration_count == self.args.max_iterations:
            if self.args.diff_coverage:
                failure_message = f"Reached maximum iteration limit without achieving desired diff coverage. Current Coverage: {round(self.test_validator.current_coverage * 100, 2)}%"
            else:
                failure_message = f"Reached maximum iteration limit without achieving desired coverage. Current Coverage: {round(self.test_validator.current_coverage * 100, 2)}%"
            if self.args.strict_coverage:
                # User requested strict coverage (similar to "--cov-fail-under in pytest-cov"). Fail with exist code 2.
                self.logger.error(failure_message)
                sys.exit(2)
            else:
                self.logger.info(failure_message)

        # Provide metrics on total token usage
        self.logger.info(
            f"Total number of input tokens used for LLM model {self.test_gen.ai_caller.model}: {self.test_gen.total_input_token_count + self.test_validator.total_input_token_count}"
        )
        self.logger.info(
            f"Total number of output tokens used for LLM model {self.test_gen.ai_caller.model}: {self.test_gen.total_output_token_count + self.test_validator.total_output_token_count}"
        )

        # Generate a report
        # ReportGenerator.generate_report(test_results_list, self.args.report_filepath)
        self.test_db.dump_to_report(self.args.report_filepath)

        # Finish the Weights & Biases run if it was initialized
        if "WANDB_API_KEY" in os.environ:
            wandb.finish()
        if "WANDB_API_KEY" in os.environ:
            wandb.finish()
