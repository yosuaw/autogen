import asyncio
import importlib
import sys
import yaml

from autogen_ext.task_centric_memory import PageLogger, Apprentice
from ame.clients._client_creator import ClientCreator


async def perform_evaluations(config, logger) -> None:
    """
    Perform the evaluations as specified in the config file.
    """
    logger.enter_function()

    # Create the client.
    client_creator = ClientCreator(config=config["client"], logger=logger)
    client = client_creator.create_client()

    # Create the apprentice.
    apprentice_config = config["Apprentice"]
    apprentice = Apprentice(
        client=client,
        config=apprentice_config,
        logger=logger)

    # Execute each evaluation.
    for evaluation_config in config["evaluations"]:
        # Import the function.
        function_config = evaluation_config["eval_function"]
        module_path = function_config["module_path"]
        try:
            module = importlib.import_module(module_path)
        except ModuleNotFoundError:
            print("Failed to import {}".format(module_path))
            raise
        function_name = function_config["function_name"]
        try:
            eval_function = getattr(module, function_name)
        except AttributeError:
            print("Failed to import {}.{}".format(module_path, function_name))
            raise

        # Call the eval function for each listed run.
        for run_dict in evaluation_config["runs"]:
            results = await eval_function(apprentice, client, logger, function_config, run_dict)
            print(results)

    if hasattr(client, "finalize"):
        # If this is a client wrapper, it needs to be finalized.
        client.finalize()

    logger.flush(finished=True)
    logger.leave_function()


async def run(config_filepath):
    # Load the config from yaml.
    with open(config_filepath, "r") as file:
        config = yaml.load(file, Loader=yaml.FullLoader)
        logger = PageLogger(config["PageLogger"])

        # Perform the evaluations.
        await perform_evaluations(config, logger)


if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) != 1:
        print("Usage:  amt.py <path to *.yaml file>")
    else:
        asyncio.run(run(config_filepath=args[0]))
