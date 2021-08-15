import argparse
import json
import logging
import os
import time

import requests
import yaml
from dotenv import load_dotenv
from requests.api import get

load_dotenv()

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(name)s - PID: %(process)d -  %(message)s",
    datefmt="%m/%d/%Y %H:%M:%S",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

ENDPOINT_SUFFIX = "/formrecognizer/v2.1/custom/models"
headers = {
    'Content-Type': 'application/json',
    "Ocp-Apim-Subscription-Key": os.getenv("SUBSCRIPTION_KEY")
}


def get_parser():
    parser = argparse.ArgumentParser("CLI for training Form Recognizer")
    parser.add_argument("--endpoint-suffix", default=ENDPOINT_SUFFIX)
    parser.add_argument("--use-training-labels", action="store_true")
    parser.add_argument("--data-url")
    args = parser.parse_known_args()
    return args

"""
def train(url: str, body: dict, headers=headers):
    try:
        response = requests(url, json=body, headers=headers)
        if response.status_code != 201:
            logger.error(f'POST model failed ({response.status_code})): {json.dumps(response.json())}')
            quit()
        logger.info(f"POST model succeeded:\n{response.headers}")
        get_url = response.headers["location"]
    except Exception as e:
        logger.error(f"POST mode failed:\n{str(e)}")
        quit()
"""



if __name__ == "__main__":
    args = get_parser()
    config = yaml.load(open(args.config, "r"), loader=yaml.FullLoader)
    """
    train(
        url=os.getenv("ENDPOINT") + args.endpoint_suffix,
        body={
            "source": os.getenv("BLOB_SAS_URL"),
            "sourceFilter": {
                "prefix": config["SOURCE_PREFIX"],
                "includeSubFolders": config["INCLUDE_SUBFOLDERS"]
                },
            "useLabelFile": config["USE_LABEL_FILE"]
        },
        headers=headers
    )
    """

