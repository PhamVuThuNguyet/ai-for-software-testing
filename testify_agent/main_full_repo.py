import asyncio
import copy
import os

from testify_agent.AICaller import AICaller
from testify_agent.lsp_logic.utils.utils_context import (
    analyze_context,
    find_test_file_context,
    initialize_language_server,
)
from testify_agent.TestifyAgent import TestifyAgent
from testify_agent.utils import find_test_files, parse_args_full_repo


async def run():
    args = parse_args_full_repo()

    # scan the project directory for test files
    test_files = find_test_files(args)
    print("Test files found:\n" + "".join(f"{f}\n" for f in test_files))

    # initialize the language server
    print("\nInitializing language server...")
    lsp = await initialize_language_server(args)

    # start the language server
    async with lsp.start_server():
        print("LSP server initialized.")

        ai_caller = AICaller(model=args.model)

        # main loop for analyzing test files
        for test_file in test_files:
            # Find the context files for the test file
            context_files = await find_test_file_context(args, lsp, test_file)
            print(
                "Context files for test file '{}':\n{}".format(
                    test_file, "".join(f"{f}\n" for f in context_files)
                )
            )

            # Analyze the test file against the context files
            print("\nAnalyzing test file against context files...")
            source_file, context_files_include = await analyze_context(
                test_file, context_files, args, ai_caller
            )

            if source_file:
                try:
                    # Run the TestifyAgent for the test file
                    args_copy = copy.deepcopy(args)
                    args_copy.source_file_path = source_file
                    args_copy.test_command_dir = args.project_root
                    args_copy.test_file_path = test_file
                    args_copy.included_files = context_files_include
                    agent = TestifyAgent(args_copy)
                    agent.run()
                except Exception as e:
                    print(
                        f"Error running TestifyAgent for test file '{test_file}': {e}"
                    )
                    pass


def main():
    asyncio.run(run())


if __name__ == "__main__":
    main()


if __name__ == "__main__":
    main()
