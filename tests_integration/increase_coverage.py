import os
import sys

# Add the parent directory to the sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from testify_agent.TestifyAgent import TestifyAgent

# List of source/test files to iterate over:
SOURCE_TEST_FILE_LIST = [
    # ["testify_agent/AICaller.py", "tests/test_AICaller.py"],
    # ["testify_agent/TestifyAgent.py", "tests/test_TestifyAgent.py"],
    # ["testify_agent/CoverageProcessor.py", "tests/test_CoverageProcessor.py"],
    # ["testify_agent/CustomLogger.py", ""],
    # ["testify_agent/FilePreprocessor.py", "tests/test_FilePreprocessor.py"],
    # ["testify_agent/PromptBuilder.py", "tests/test_PromptBuilder.py"],
    # ["testify_agent/ReportGenerator.py", "tests/test_ReportGenerator.py"],
    # ["testify_agent/Runner.py", "tests/test_Runner.py"],
    # ["testify_agent/UnitTestDB.py", "tests/test_UnitTestDB.py"],
    # ["testify_agent/UnitTestGenerator.py", "tests/test_UnitTestGenerator.py"],
    # ["testify_agent/main.py", "tests/test_main.py"],
    # ["testify_agent/settings/config_loader.py", ""],
    ["testify_agent/utils.py", "tests/test_load_yaml.py"],
    # ["testify_agent/version.py", "tests/test_version.py"],
]


class Args:
    def __init__(self, source_file_path, test_file_path):
        self.source_file_path = source_file_path
        self.test_file_path = test_file_path
        self.test_file_output_path = ""
        self.code_coverage_report_path = "coverage.xml"
        self.test_command = f"poetry run pytest --cov=testify_agent --cov-report=xml  --timeout=30 --disable-warnings"
        self.test_command_dir = os.getcwd()
        self.included_files = None
        self.coverage_type = "cobertura"
        self.report_filepath = "test_results.html"
        self.desired_coverage = 100
        self.max_iterations = 5
        self.additional_instructions = "Do not indent the tests"
        # self.model = "gpt-4o"
        self.model = "o1-mini"
        self.api_base = "http://localhost:11434"
        self.prompt_only = False
        self.strict_coverage = False
        self.run_tests_multiple_times = 1
        self.use_report_coverage_feature_flag = False
        self.log_db_path = "increase_project_coverage.db"


if __name__ == "__main__":
    # Iterate through list of source and test files to run Testify Agent
    for source_file, test_file in SOURCE_TEST_FILE_LIST:
        # Print a banner for the current source file
        banner = f"Testing source file: {source_file}"
        print("\n" + "*" * len(banner))
        print(banner)
        print("*" * len(banner) + "\n")

        args = Args(source_file, test_file)
        agent = TestifyAgent(args)
        agent.run()
