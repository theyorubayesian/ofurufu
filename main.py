import argparse
import glob
import logging
import os
import sys
import time
import uuid

from msrest.authentication import CognitiveServicesCredentials

from ofurufu.face_recognition import authenticate_face_client
from ofurufu.face_recognition import create_person_group
from ofurufu.face_recognition import detect_faces
from ofurufu.face_recognition import draw_bbox
from ofurufu.face_recognition import match_against_person_group
from ofurufu.face_recognition import verify_face
from ofurufu.variables import Variables
from ofurufu.video_analyzer import authenticate_video_indexer
from ofurufu.video_analyzer import get_sentiment_and_emotion
from ofurufu.video_analyzer import save_face_thumbnails


logging.basicConfig(
    filename=f"logs/ofurufu_{time.time()}.log",
    format="%(asctime)s - %(levelname)s - %(name)s - PID: %(process)d -  %(message)s",
    datefmt="%m/%d/%Y %H:%M:%S",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

v = Variables()


def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("--upload-video", action="store_true")
    parser.add_argument("--get-video-info", action="store_true")
    parser.add_argument("--thumbnail-dir", default="outputs/indexer/thumbnails")
    parser.add_argument("--video-name")
    parser.add_argument("--video-language", default="English")
    parser.add_argument("--video-path")
    parser.add_argument("--video-id")
    parser.add_argument("--person-group-id", default=str(uuid.uuid4()))
    parser.add_argument("--person-group-name")
    parser.add_argument("--create-person-group", action="store_true")
    parser.add_argument("--identity-cards", nargs="+")

    args = parser.parse_args()
    if args.upload_video:
        args.get_video_info = True
    
    return args


def main():
    args = get_parser()
    uploaded_video_id = args.video_id

    indexer = authenticate_video_indexer(
        v.VIDEO_ANALYZER_SUBSCRIPTION_KEY,
        v.VIDEO_ANALYZER_LOCATION,
        v.VIDEO_ANALYZER_ACCOUNT_ID
    )

    face_client = authenticate_face_client(
        v.FACE_RECOGNIZER_ENDPOINT,
        CognitiveServicesCredentials(v.FACE_RECOGNIZER_SUBSCRIPTION_KEY) 
    )

    if args.upload_video:
        logger.info(f"Uploading video: {args.video_path} to indexer")
        uploaded_video_id = indexer.upload_video_to_indexer(
            input_filename=args.video_path,
            video_name=args.video_name,
            video_language=args.video_language
        )
        time.sleep(300) # NOTE: Hack to allow indexing

    person_images = glob.glob(f"{args.thumbnail_dir}/*.jpg")

    if args.get_video_info:
        logger.info(f"Analyzing video with id: {uploaded_video_id}")
        video_info = indexer.get_video_info(uploaded_video_id, video_language=args.video_language)
        logger.info(video_info)
        
        insights = get_sentiment_and_emotion(video_info)
        logger.info(insights)

        thumbnails = save_face_thumbnails(
            video_info, uploaded_video_id, args.thumbnail_dir, indexer
            )
        person_images = [os.path.join(args.thumbnail_dir, x) for x in thumbnails]
        logger.info(f"Saved thumbnails: \n{person_images}")
    
    person_group_faces = detect_faces(face_client, person_images)
    logger.info(person_group_faces)

    if args.create_person_group:
        logger.info(f"Creating Person group: {args.person_group_id}" \
                    f" Ensure that images in {person_images} are of same person"
        )
        create_person_group(face_client, args.person_group_id, args.person_group_name, person_images)
        
        is_identical, _ = verify_face(
            face_client, list(person_group_faces.values())[0], list(person_group_faces.values())[1]
            )
        if not is_identical:
            msg = "Images added to person group may be of different people"
            logger.error(msg)
            sys.exit(msg)

        logger.info(f"Created person group: {args.person_group_id}")

    if args.identity_cards:
        faces_in_ids = detect_faces(face_client, args.identity_cards)
        
        for image, face_id in faces_in_ids.items():
            is_identical, confidence = verify_face(
                face_client, face_id, list(person_group_faces.values())[1]
            )
            if is_identical:
                logger.info(f"Person matched with confidence: {confidence}")
                # draw_bbox(image, faces_in_ids)

            match_against_person_group(face_client, [face_id], args.person_group_id)


if __name__ == "__main__":
    main()
