from argparse import ArgumentParser
from configparser import ConfigParser
from typing import Optional


class Config:
    __conf: Optional[ConfigParser] = None

    @staticmethod
    def config() -> ConfigParser:
        if Config.__conf is None:
            Config.__conf = ConfigParser()
            parser = ArgumentParser(prog="blackjack-simulator")
            parser.add_argument(
                "--config",
                "-c",
                type=str,
                help="path to config file",
                default="config.ini",
            )
            args = parser.parse_args()
            Config.__conf.read(args.config)
        return Config.__conf
