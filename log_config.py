import json
import logging
import logging.handlers
import logging.config

def setup_logging():
    with open("logging.json") as f:
        json_config = json.load(f)
    logging.config.dictConfig(config=json_config)

logger = logging.getLogger("logger")

if __name__ == '__main__':
    setup_logging()
