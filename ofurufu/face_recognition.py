import logging
import os
import sys
import time
from pathlib import Path

from azure.cognitiveservices.vision.face import FaceClient
from azure.cognitiveservices.vision.face.models import TrainingStatusType
from PIL import Image
from PIL import ImageDraw

from ofurufu.variables import Variables

logging.basicConfig(
    filename=f"logs/ofurufu_{time.time()}.log",
    format="%(asctime)s - %(levelname)s - %(name)s - PID: %(process)d -  %(message)s",
    datefmt="%m/%d/%Y %H:%M:%S",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

v = Variables()


def authenticate_face_client(endpoint, credentials):
    client = FaceClient(endpoint, credentials)
    print(f"FaceClient API Version: {client.api_version}")

    return client


def create_person_group(client: FaceClient, person_group_id: str, person_group_name: str, images: list = None):
    client.person_group.create(person_group_id=person_group_id, name=person_group_id)
    
    person = client.person_group_person.create(person_group_id, person_group_name)

    for image in images:
        with open(image, "rb") as f:
            client.person_group_person.add_face_from_stream(person_group_id, person.person_id, f)

    client.person_group.train(person_group_id)

    while True:
        training_status = client.person_group.get_training_status(person_group_id)
        if training_status.status is TrainingStatusType.succeeded:
            break
        elif training_status.status is TrainingStatusType.failed:
            client.person_group.delete(person_group_id)
            msg = "Training person group failed"
            logger.error(msg)
            sys.exit(msg)
        time.sleep(10)


def detect_faces(client: FaceClient, image_list: list):
    face_ids = {}
    for image_path in image_list:
        image = open(image_path, "rb")

        faces = client.face.detect_with_stream(image)

        for face in faces:
            logging.info(f"Face ID: {face.face_id} found in image: {image_path}")
            face_ids[image.name] = face.face_id

    return face_ids


def verify_face(client: FaceClient, face_1: str, face_2: str):
    verification = client.face.verify_face_to_face(face_1, face_2)
    return verification.is_identical, verification.confidence


def get_bounding_box(face):
    bbox = face.face_rectangle
    top_left = (bbox.left, bbox.top)
    bottom_right = (bbox.right, bbox.bottom)
    return top_left, bottom_right


def draw_bbox(image_path, detected_faces, output_dir="outputs/faces/captures", outline="red", width=5):
    p = Path(image_path)
    img = Image.open(image_path)
    draw = ImageDraw.Draw(img)

    for face in detected_faces:
        draw.rectangle(get_bounding_box(face), outline=outline, width=width)

    filename = p.stem + "_bbox" + p.suffix
    img.save(os.path.join(output_dir, filename))
    logger.info(f"Saved image with bounding box to: {output_dir}")


def match_against_person_group(client: FaceClient, face_ids: list, person_group_id: str):
    results = client.face.identify(face_ids, person_group_id)
    
    for result in results:
        for candidate in result.candidates:
            logger.info(f"Candidate matched Person Group: {person_group_id} with confidence {candidate.confidence}")
