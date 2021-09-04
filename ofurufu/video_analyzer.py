import argparse
import logging
import os
import time
from typing import Optional
from typing import List

import requests

import ofurufu.blob as blob
from ofurufu import apiformat as api_fmt
from ofurufu.variables import Variables

logging.basicConfig(
    filename=f"logs/ofurufu_{time.time()}.log",
    format="%(asctime)s - %(levelname)s - %(name)s - PID: %(process)d -  %(message)s",
    datefmt="%m/%d/%Y %H:%M:%S",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

v = Variables()
BASE_URL = api_fmt.BASE.format(
    location=v.VIDEO_ANALYZER_LOCATION,
    accountId=v.VIDEO_ANALYZER_ACCOUNT_ID
)


def get_access_token(
        location: str,
        account_id: str,
        permission: str,
        headers: dict
) -> Optional[str]:
    """

    :param location:
    :param account_id:
    :param permission:
    :param headers:
    :return:
    """
    url = api_fmt.ACCESS_TOKEN_WITH_PERMISSION.format(
        location=location, account_id=account_id, permission=permission)

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        logger.info("Obtained Access Token successfully")
        return response.json()
    else:
        logger.error("Error obtaining access token")
        logger.error(f"API Response: {response.status_code} {response.reason}")
    return None


def create_person_model(
        location: str,
        account_id: str,
        model_name: str,
        access_token: str,
        headers: dict
) -> Optional[str]:
    """

    :param location:
    :param account_id:
    :param model_name:
    :param access_token:
    :param headers:
    :return:
    """
    url = BASE_URL + api_fmt.CREATE_PERSON_MODEL.format(
        location=location, accountId=account_id, name=model_name)
    headers["Authorization"] = f"Bearer {access_token}"

    response = requests.post(url, headers=headers)
    if response.status_code == 201:
        logger.info("Person Model created successfully")
        return response.json()
    else:
        logger.error(f"Error creating Person Model: {model_name}")
        logger.error(f"API Response: {response.status_code} {response.reason}")
    return None


def create_person(
    person_model_id: str,
    person_name: str,
    headers: str
):
    url = BASE_URL + api_fmt.CREATE_PERSON.format(
        personModelId=person_model_id,
        name=person_name
    )
    response = requests.post(url, headers=headers)
    if response.status_code == 201:
        logger.info(f"Person: {person_name} created successfully in Person Model: {person_model_id}")
        return response.json()
    else:
        logger.error(f"Error creating Person: {person_name} in Person Model: {person_model_id}")
        logger.error(f"API Response: {response.status_code} {response.reason}")
    return None


def send_video_to_indexer(
        video_name: str,
        video_url: str,
        privacy: str,
        indexing_preset: str,
        send_success_email: bool,
        streaming_preset: str,
        person_model_id: str,
        headers: dict
):
    """

    :param video_name:
    :param video_url:
    :param privacy:
    :param indexing_preset:
    :param send_success_email:
    :param streaming_preset:
    :param headers:
    :return:
    """
    headers["Content-Type"] = "multipart/form-data"

    url = BASE_URL + api_fmt.INDEX_VIDEO.format(
        videoName=video_name,
        privacy=privacy,
        url=video_url,
        indexingPreset=indexing_preset,
        successEmail=send_success_email,
        streamingPreset=streaming_preset
    )
    if person_model_id:
        logger.info(f"Using Person Model with Id: {person_model_id}")
        url += f"&personModelId={person_model_id}"

    response = requests.post(url=url, headers=headers)
    if response.status_code == 201:
        logger.info("Video indexed successfully")
        return response.json()
    else:
        logger.error("Error indexing video")
        logger.error(f"API Response: {response.status_code} {response.reason}")
    return None


def get_video_index(
    video_id: str,
    headers: dict
) -> Optional[str]:
    """"
    
    :param video_id:
    :param headers:
    :return:
    """
    url = BASE_URL + api_fmt.GET_VIDEO_INDEX(
        videoId=video_id
    )

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        logger.info(f"Retrieved index for Video with ID: {video_id}")
        return response.json()
    else:
        logger.error("Error retrieving index for Video with ID: {video_id}")
        logger.error(f"API Response: {response.status_code} {response.reason}")
    return None


def get_video_thumbnail(
    video_id: str, 
    thumbnail_id: str, 
    thumbnail_fmt: str,
    output_dir: str,
    headers: dict
):
    """
    
    :param video_id:
    :param thumbnail_id:
    :param thumbnail_fmt:
    :param output_dir:
    :param headers:
    :return:
    """
    url = BASE_URL + api_fmt.GET_VIDEO_THUMBNAIL.format(
        videoId=video_id,
        thumbnailId=thumbnail_id,
        fmt=thumbnail_fmt
    )
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        logger.info(f"Retrieved index for Video with ID: {video_id}")
        thumbnail = response.content

        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, "thumbnail" + thumbnail_id + ".jpeg")
        with open(output_file, "wb") as f:
            f.write(thumbnail)
        logger.info(f"Thumbnail has been written to {output_file}")
    else:
        logger.error("Error retrieving index for Video with ID: {video_id}")
        logger.error(f"API Response: {response.status_code} {response.reason}")
    return None


def create_face_for_person(
    person_model_id: str,
    person_id: str,
    faces: List[str],
    headers: dict
):
    """
    
    :param person_model_id:
    :param person_id:
    :param faces:
    param headers:
    """
    url = BASE_URL + api_fmt.CREATE_FACE.format(
        personModelId=person_model_id,
        personId=person_id
    )
    data = {"urls": faces}
    headers["Content-Type"] = "application/json"

    response = requests.post(url, headers=headers, data=data)


def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--index-video"
    )


def main():
    args = get_parser()
    headers = {
        "Ocp-Apim-Subscription-Key": v.VIDEO_ANALYZER_AUTH_PKEY
    }
    get_access_token("trial", v.VIDEO_ANALYZER_ACCOUNT_ID, "Owner", headers)


if "__name__" == "__main__":
    main()
