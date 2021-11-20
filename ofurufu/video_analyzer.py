import argparse
import io
import logging
import os
import sys
import time
from typing import Type

from PIL import Image
from video_indexer import VideoIndexer

from ofurufu.variables import Variables

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
    parser.add_argument("--video-name")
    parser.add_argument("--video-language", default="English")
    parser.add_argument("--video-path")
    parser.add_argument("--video-id")
    parser.add_argument("--thumbnail-dir", default="outputs/indexer/thumbnails")

    args = parser.parse_args()
    return args


def authenticate_video_indexer(subscription_id, location, account_id):
    indexer = VideoIndexer(
        vi_subscription_key=subscription_id,
        vi_location=location,
        vi_account_id=account_id
    )

    indexer.check_access_token()
    return indexer


def save_face_thumbnails(video_info, video_id: str, thumbnail_dir: str, indexer: VideoIndexer):
    images = []
    img_raw = []
    img_strs = []
    thumbnail_filenames = []

    os.makedirs(thumbnail_dir, exist_ok=True)

    thumbnails = video_info['videos'][0]['insights']['faces'][0]['thumbnails']

    logger.info(f"Getting thumbnails in video: {video_id}")

    for thumb in thumbnails:
        logger.info(thumb)
        thumbnail_filenames.append(thumb['fileName'])
        thumbnail_id = thumb['id']
        img_code = indexer.get_thumbnail_from_video_indexer(video_id, thumbnail_id)

        img_strs.append(img_code)
        img_stream = io.BytesIO(img_code)
        img_raw.append(img_stream)
        img = Image.open(img_stream)
        images.append(img)

    for filename, image in zip(thumbnail_filenames, images):
        image.save(f"{thumbnail_dir}/{filename}")

    return thumbnail_filenames


def get_sentiment_and_emotion(video_info):
    return {
        "sentiments": video_info['summarizedInsights']['sentiments'],
        "emotions": video_info['summarizedInsights']["emotions"]
    }


def main():
    args = get_parser()
    uploaded_video_id = args.video_id

    indexer = authenticate_video_indexer(
        v.VIDEO_ANALYZER_SUBSCRIPTION_KEY,
        v.VIDEO_ANALYZER_LOCATION,
        v.VIDEO_ANALYZER_ACCOUNT_ID
    )
    
    if args.upload_video:
        logger.info(f"Uploading video: {args.video_path} to indexer")
        uploaded_video_id = indexer.upload_to_video_indexer(
            input_filename=args.video_path,
            video_name=args.video_name,
            video_language=args.video_language
        )
        time.sleep(300) # NOTE: Hack to allow indexing
    
    video_info = indexer.get_video_info(uploaded_video_id, video_language=args.video_language)

    logger.info(video_info)

    thumbnails = save_face_thumbnails(
        video_info, uploaded_video_id, args.thumbnail_dir, indexer
        )
    logger.info(f"Saved thumbnails: \n{thumbnails}")

    sentiment_and_emotion = get_sentiment_and_emotion(video_info)
    logger.info(sentiment_and_emotion)


if __name__ == "__main__":
    main()
