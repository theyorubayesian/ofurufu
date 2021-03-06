import argparse
import logging
import os
import time

from azure.cognitiveservices.vision.customvision.prediction import CustomVisionPredictionClient
from azure.cognitiveservices.vision.customvision.training import CustomVisionTrainingClient
from msrest.authentication import ApiKeyCredentials

from ofurufu.variables import Variables

v = Variables()

logging.basicConfig(
    filename=f"logs/ofurufu_{time.time()}.log",
    format="%(asctime)s - %(levelname)s - %(name)s - PID: %(process)d -  %(message)s",
    datefmt="%m/%d/%Y %H:%M:%S",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def get_parser():
    parser = argparse.ArgumentParser(
        "CLI for training or using Custom Vision Object Detection models"
    )
    parser.add_argument("--analyse-image", action="store_true")
    parser.add_argument("--images", nargs="+")
    parser.add_argument("--model-iteration-name")
    args = parser.parse_args()

    if args.analyse_image and not args.images:
        raise ValueError("Pass in `images` to be analyzed")
    return args


def authenticate(key: str, training: bool = False):
    """

    :param key: Use Training key if training else prediction key
    :param training: Get client for model training or predictions
    :return: TrainingClient or PredictionClient
    """
    credentials = ApiKeyCredentials(in_headers={"Training-key": key})

    if training:
        logger.info("Getting client for training")
        client = CustomVisionTrainingClient(v.CUSTOM_VISION_TRAINING_ENDPOINT, credentials)
    else:
        logger.info("Getting client for prediction")
        client = CustomVisionPredictionClient(v.CUSTOM_VISION_PREDICTION_ENDPOINT, credentials)
    logger.info("Authenticated successfully")
    return client


def train_model():
    # TODO: Fulfil this optional rubric
    raise NotImplementedError


def make_prediction(
        client: CustomVisionPredictionClient,
        image: str,
        project_id: str,
        model_iteration_name: str
) -> list:
    if any([image.startswith("http"), image.startswith("www.")]):
        results = client.detect_image_url(
            project_id=project_id,
            published_name=model_iteration_name,
            url=image
        )
    elif os.path.exists(image):
        results = client.detect_image(
            project_id=project_id,
            published_name=model_iteration_name,
            image_data=open(image, "rb")
        )
    else:
        msg = "`image` is not a valid local file path or url"
        logger.error(msg)
        raise ValueError(msg)

    items = []
    logger.info(f"--------Detecting objects in image: {image}--------")
    for prediction in results.predictions:
        result_format = "'\t'{0}: probability = {1:.2f}% bbox.left = {2:.2f}, bbox.top = {3:.2f}, " \
                        "bbox.width = {4:.2f}, bbox.height = {5:.2f} "
        prediction_probability = prediction.probability * 100
        prediction_bbox = {
            "left": prediction.bounding_box.left,
            "top": prediction.bounding_box.top,
            "width": prediction.bounding_box.width,
            "height": prediction.bounding_box.height
        }
        logger.info(result_format.format(
            prediction.tag_name,
            prediction_probability,
            prediction_bbox["left"],
            prediction_bbox["top"],
            prediction_bbox["width"],
            prediction_bbox["height"]
        ))
        items.append({
            "source": image,
            "tag": prediction.tag_name,
            "prediction_probability": prediction_probability,
            "bounding_box": prediction_bbox
        })
    return items


if __name__ == "__main__":
    args = get_parser()
    client = authenticate(
        key=v.CUSTOM_VISION_PREDICTION_KEY if args.analyse_image else v.CUSTOM_VISION_TRAINING_KEY,
        training=False if args.analyse_image else True
    )
    if args.analyse_image:
        for image in args.images:
            make_prediction(
                client,
                image,
                v.CUSTOM_VISION_PROJECT_ID,
                args.model_iteration_name or v.CUSTOM_VISION_DEFAULT_MODEL_ITERATION_NAME
            )
