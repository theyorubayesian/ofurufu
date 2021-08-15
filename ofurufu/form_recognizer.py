import argparse
import logging
import os
import time
from typing import Union

import yaml
from azure.core.exceptions import ResourceNotFoundError
from azure.ai.formrecognizer import FormRecognizerClient
from azure.ai.formrecognizer import FormTrainingClient
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv

load_dotenv()

FORM_RECOGNIZER_KEY = os.getenv("FORM_RECOGNIZER_KEY")
FORM_RECOGNIZER_ENDPOINT = os.getenv("FORM_RECOGNIZER_ENDPOINT")


logging.basicConfig(
    filename=f"logs/ofurufu_{time.time()}.log",
    format="%(asctime)s - %(levelname)s - %(name)s - PID: %(process)d -  %(message)s",
    datefmt="%m/%d/%Y %H:%M:%S",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def get_parser():
    parser = argparse.ArgumentParser("CLI for training Form Recognizer")
    parser.add_argument("--config", default="config.yml")
    parser.add_argument("--train-model", action="store_true")
    parser.add_argument("--analyze-document", action="store_true")
    parser.add_argument("--delete-model", action="store_true")
    parser.add_argument("--document-type", choices=["id", "boarding-pass"])
    parser.add_argument("--documents", nargs="+")
    parser.add_argument("--model-id")
    args, _ = parser.parse_known_args()

    if args.analyze_document and not (args.documents and args.document_type):
        raise ValueError("Pass in `documents` to analyze and/or `document-type`")
    if args.delete_model and not args.model_id:
        raise ValueError("Pass in `model-id` of model to be deleted")
    return args


def authenticate(
        endpoint: str, key: str, training: bool = False
) -> Union[FormRecognizerClient, FormTrainingClient]:
    if training:
        client = FormTrainingClient(endpoint, AzureKeyCredential(key))
    else:
        client = FormRecognizerClient(endpoint, AzureKeyCredential(key))
    logger.info("Authenticated successfully")
    return client


def train_boarding_pass_model(
        client: FormTrainingClient, data_url: str, use_training_labels: bool, **kwargs
) -> None:
    poller = client.begin_training(data_url, use_training_labels=use_training_labels, **kwargs)
    model = poller.result()

    trained_model_id = model.model_id
    logger.info(f"Trained model ID: {trained_model_id}")
    logger.info(f"Status: {model.status}")
    logger.info(f"Training started: {model.training_started_on}")
    logger.info(f"Training completed: {model.training_completed_on}")

    logger.info("Recognized fields:")
    for submodel in model.submodels:
        logger.info(
            f"""The submodel with form type {submodel.form_type} has recognized: {','.join(
                [
                    field.label if field.label else name
                    for name, field in submodel.fields.items()
                ]
            )}"""
        )

    for doc in model.training_documents:
        logger.info("Document name: {}".format(doc.name))
        logger.info("Document status: {}".format(doc.status))
        logger.info("Document page count: {}".format(doc.page_count))
        logger.info("Document errors: {}".format(doc.errors))

    return None


def analyze_id_document(client: FormRecognizerClient, document: str, **kwargs) -> list:
    if any([document.startswith("http"), document.startswith("www.")]):
        poller = client.begin_recognize_identity_documents_from_url(document)
    elif os.path.exists(document):
        poller = client.begin_recognize_identity_documents(open(document, "rb"))
    else:
        msg = "Document is not a valid local file path or url"
        logger.error(msg)
        raise ValueError(msg)

    page = poller.result()

    results = []
    for idx, id in enumerate(page):
        logger.info(f"--------Recognizing ID document #{idx + 1}--------")
        first_name = id.fields.get("FirstName", None)
        last_name = id.fields.get("LastName", None)
        date_of_birth = id.fields.get("DateOfBirth", None)
        address = id.fields.get("Address", None)
        document_info = {
            "source": document,
            "first_name": first_name,
            "last_name": last_name,
            "date_of_birth": date_of_birth,
            "address": address
        }
        for info in document_info:
            logger.info(f"{info}: {document_info[info]}")
        results.append(document_info)

    return results


def analyze_boarding_pass(client: FormRecognizerClient, model_id: str, document: str) -> list:
    if any([document.startswith("http"), document.startswith("www.")]):
        poller = client.begin_recognize_custom_forms_from_url(model_id=model_id, form_url=document)
    elif os.path.exists(document):
        poller = client.begin_recognize_custom_forms(model_id=model_id, form=open(document, "rb"))
    else:
        msg = "Document is not a valid local file path or url"
        logger.error(msg)
        raise ValueError(msg)

    page = poller.result()
    results = []

    for idx, doc in enumerate(page):
        logger.info(f"--------Recognizing Boarding Pass document #{idx + 1}--------")
        first_name = doc.fields.get("firstName", None)
        last_name = doc.fields.get("lastName", None)
        date = doc.fields.get("date", None)
        origin = doc.fields.get("origin", None)
        destination = doc.fields.get("destination", None)
        flight_no = doc.fields.get("flightNo", None)
        boarding_time = doc.fields.get("boardingTime", None)
        document_info = {
            "source": document,
            "first_name": first_name.value,
            "last_name": last_name.value,
            "date": date.value,
            "origin": origin.value,
            "destination": destination.value,
            "flight_no": flight_no.value,
            "boarding_time": boarding_time.value
        }
        for info in document_info:
            logger.info(f"{info}: {document_info[info]}")
        results.append(document_info)

    return results


def delete_trained_model(client: FormTrainingClient, model_id: str) -> None:
    client.delete_model(model_id=model_id)

    try:
        client.get_custom_model(model_id=model_id)
    except ResourceNotFoundError:
        logger.info(f"Successfully deleted model with id: {model_id}")


if __name__ == "__main__":
    args = get_parser()
    config = yaml.load(open(args.config, "r"), Loader=yaml.FullLoader)
    logger.info("--------Configurations--------")
    for k, v in config.items():
        logger.info(f"{k}: {v}")
    client = authenticate(
        FORM_RECOGNIZER_ENDPOINT,
        FORM_RECOGNIZER_KEY,
        training=(args.train_model or args.delete_model) or False
    )

    if args.train_model:
        train_boarding_pass_model(
            client,
            data_url=os.getenv("CONTAINER_SAS_URL"),
            use_training_labels=config["training"]["useLabelFile"],
            prefix=config["training"]["dataFilePrefix"],
            model_name=config["training"]["modelName"]
        )

    if args.analyze_document:
        if args.document_type == "id":
            analyzer = analyze_id_document
        elif args.document_type == "boarding-pass":
            analyzer = analyze_boarding_pass
        else:
            msg = "Document type not supported yet. Document must be `id` or `boarding-pass`"
            logger.error(msg)
            raise ValueError(msg)

        for document in args.documents:
            analyzer(client=client, document=document, model_id=os.getenv("TRAINED_MODEL_ID"))

    if args.delete_model:
        delete_trained_model(client, args.model_id)
