import yaml

from shared.config.types import Config


def parse_config(config_file_path: str = 'shared/config/config.yaml') -> Config:
    """Parse the config file

    Args:
        config_file_path (`str`): path to the config file

    Returns:
        parsed_config (`Config`): parsed config object
    """

    with open(config_file_path, 'r') as f:
        parsed_config = yaml.load(f, Loader=yaml.SafeLoader)
        parsed_config = Config.from_dict(parsed_config)

        print(parsed_config.json())

    return parsed_config
