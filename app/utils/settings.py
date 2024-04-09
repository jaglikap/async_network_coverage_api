import argparse
import io
import os

import jinja2
from yaml import load, Loader


def parse_args() -> argparse.Namespace:
    """
    Parser for command-line options,
    arguments and sub-commands.

    :return: an object with actions and the config path
    :rtype: Namespace
    """
    custom_parser = argparse.ArgumentParser()
    custom_parser.add_argument(
        "-config",
        "--config",
        action="store",
        required=True,
        type=str,
        default="config/config.yaml",
        help="Path to the yaml configuration file",
    )

    return custom_parser.parse_args()


def load_settings(filename: str) -> dict:
    """Load the application settings."""

    def load_jinja_template(jinja_filepath: str) -> str:
        # Render Jinja configuration template
        # (convert variables with env vars)
        with open(os.path.realpath(jinja_filepath), "r") as fd:
            data = fd.read()
            template = jinja2.Environment(
                loader=jinja2.BaseLoader()
            ).from_string(data)
            return template.render(env=os.environ)

    # Load yaml configuration into variable
    return load(io.StringIO(load_jinja_template(filename)), Loader)


def check_config(config: dict) -> None:
    """
    Perform checks on configuration.
    Check each configuration variable: value

    :param config: the configuration
    :type config: dict
    :return: None
    :raises AssertionError: Raises on configuration issue
    """
    assert config["ntw_towers_gps_coordinates"]
    assert config["ntw_towers_l93_coordinates"]
    assert config["cache_file"]


def get_config_dict() -> dict:
    args = parse_args()
    config_vars = load_settings(filename=args.config)
    check_config(config_vars)

    return config_vars
