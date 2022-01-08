import csv
import os
import time

from msrest.authentication import CognitiveServicesCredentials
import yaml

import ofurufu.feedback as f
from ofurufu.blob import authenticate_blob_client
from ofurufu.blob import download_blob
from ofurufu.face_recognition import authenticate_face_client
from ofurufu.face_recognition import create_person_group
from ofurufu.face_recognition import match_against_person_group
from ofurufu.face_recognition import detect_faces
from ofurufu.form_recognizer import authenticate_form_client
from ofurufu.form_recognizer import analyze_boarding_pass
from ofurufu.form_recognizer import analyze_id_document
from ofurufu.variables import Variables
from ofurufu.video_analyzer import authenticate_video_indexer
from ofurufu.video_analyzer import get_sentiment_and_emotion
from ofurufu.video_analyzer import save_face_thumbnails

v = Variables()


def get_clients():
    form_client = authenticate_form_client(
        v.FORM_RECOGNIZER_ENDPOINT, v.FORM_RECOGNIZER_KEY, training=False)

    face_client = authenticate_face_client(
        v.FACE_RECOGNIZER_ENDPOINT,
        CognitiveServicesCredentials(v.FACE_RECOGNIZER_SUBSCRIPTION_KEY) 
    )

    indexer = authenticate_video_indexer(
        v.VIDEO_ANALYZER_SUBSCRIPTION_KEY,
        v.VIDEO_ANALYZER_LOCATION,
        v.VIDEO_ANALYZER_ACCOUNT_ID
    )

    blob_service_client = authenticate_blob_client(
        v.BLOB_ACCOUNT_NAME, v.BLOB_ACCOUNT_KEY
    )
    return form_client, face_client, indexer, blob_service_client


def clean_text(text: str):
    return text.strip().lower().replace(" ", "_")


def get_pii_from_id_card(id_card, form_client=None):
    if form_client is None:
        form_client = authenticate_form_client(
            v.FORM_RECOGNIZER_ENDPOINT, v.FORM_RECOGNIZER_KEY, training=False
        )
    
    results = analyze_id_document(form_client, id_card)
    return results[0]


def get_pii_from_boarding_pass(boarding_pass, form_client=None):
    if form_client is None:
        form_client = authenticate_form_client(
            v.FORM_RECOGNIZER_ENDPOINT, v.FORM_RECOGNIZER_KEY, training=False
        )
    
    results = analyze_boarding_pass(
        form_client, 
        model_id=v.FORM_RECOGNIZER_TRAINED_MODEL_ID,
        document=boarding_pass
    )
    return results[0]


def get_passenger_manifest_info(path):
    with open(path, "r") as f:
        reader = csv.reader(f)
        header = next(reader)
    
        passengers = [
            {clean_text(x): y for x, y in zip(header, row)} for row in reader
        ]
    return header, passengers


def validate_name(manifest_info, boarding_pass_info, id_card_info):
    if (
        clean_text(manifest_info["First Name"]) != clean_text(id_card_info["first_name"])
        | clean_text(manifest_info["Last Name"]) != clean_text(id_card_info["last_name"])
    ):
        return f.PII_MISMATCH_MESSAGE.format(document="ID card")

    if (
        clean_text(manifest_info["First Name"]) != clean_text(boarding_pass_info["first_name"])
        | clean_text(manifest_info["Last Name"]) != clean_text(boarding_pass_info["last_name"])
    ):
        return f.PII_MISMATCH_MESSAGE.format(document="boarding pass")
    
    return None


def validate_dob(manifest_info, id_card_info):
    if clean_text(manifest_info["DateofBirth"]) != clean_text(id_card_info["date_of_birth"]):
        return f.PII_MISMATCH_MESSAGE.format(document="ID card")
    
    return None


def validate_boarding_pass(manifest_info, boarding_pass_info):
    if (
        clean_text(manifest_info["Flight No"]) != clean_text(boarding_pass_info["flight_no"])
        | manifest_info["Origin"] != boarding_pass_info["origin"]
        | manifest_info["Destination"] != boarding_pass_info["destination"]
        | manifest_info["Time"] != boarding_pass_info["boarding_time"]
        | manifest_info["Date"] != boarding_pass_info["date"]
    ):
        return f.FLIGHT_INFO_MISMATCH
    
    return None


def validate_person(
    manifest_info, 
    person_video, 
    id_card, 
    face_client, 
    indexer, 
    threshold=0.65, 
    thumbnail_dir="outputs/indexer/thumbnails"
):
    person_id = f"{manifest_info['First Name']}_{manifest_info['Last Name']}_{time.strftime('%Y%m%d-%H%M%S')}"
    
    uploaded_video_id = indexer.upload_video_to_indexer(
            input_filename=person_video,
            video_name=f"{person_id}_video",
            video_language="English"
        )
    time.sleep(300)

    face_in_id_card = detect_faces(face_client, [id_card])
    face_id = list(face_in_id_card.values())[0]

    video_info = indexer.get_video_info(uploaded_video_id, video_language="English")
    kiosk_experience_insight = get_sentiment_and_emotion(video_info)
    print(kiosk_experience_insight)

    thumbnails = save_face_thumbnails(
            video_info, uploaded_video_id, thumbnail_dir, indexer
            )
    person_images = [os.path.join(thumbnail_dir, x) for x in thumbnails]
    create_person_group(face_client, person_id, person_id, person_images)

    match_results = match_against_person_group(face_client, [face_id], person_id)
    for result in match_results:
        for candidate in result.candidates:
            confidence = float(candidate.confidence)

    if confidence <= threshold:
        return f.FACE_ID_FAILS_MESSAGE.format(
            first_name=manifest_info["First Name"],
            last_name=manifest_info["Last Name"],
            flightno=manifest_info["Flight No"],
            origin=manifest_info["Origin"],
            destination=manifest_info["Destination"]
        )
    
    return None


def validate_luggage():
    # TODO: This is not currently in use but will be implemented
    pass


def validate_passenger(
    manifest_info, id_card, boarding_pass, person_video, form_client, face_client, indexer
):
    id_card_info = get_pii_from_id_card(id_card, form_client)
    boarding_pass_info = get_pii_from_boarding_pass(boarding_pass)
    validated_manifest_info = {**manifest_info}
 
    boarding_pass_issue = validate_boarding_pass(manifest_info, boarding_pass_info)
    if not boarding_pass_issue:
        validated_manifest_info["BoardingPassValidation"] = True

    passenger_name_issue = validate_name(manifest_info, boarding_pass_info, id_card_info)
    if not passenger_name_issue:
        validated_manifest_info["NameValidation"] = True
    
    passenger_dob_issue = validate_dob(manifest_info, id_card_info)
    if not passenger_dob_issue:
        validated_manifest_info["DoBValidation"] = True
    
    person_identity_issue = validate_person(manifest_info, person_video, id_card, face_client, indexer)
    if not person_identity_issue:
        validated_manifest_info["PersonValidation"] = True
    
    # NOTE: This is not in use because no passenger luggages to validate
    # All passenger's validation are set to True currrently 
    # validate_luggage()
    validated_manifest_info["LuggageValidation"] = True

    return validated_manifest_info


def main():
    info = yaml.safe_load(open("passengers.yml", "r"))
    form_client, face_client, indexer, blob_service_client = get_clients()

    header, manifest_info = get_passenger_manifest_info(info["manifest"])
    manifest_info = sorted(manifest_info, key=lambda x: x["First Name"]+x["Last Name"])
    validated_manifest_info = []

    for passenger_documents, passenger_info in zip(info["passengers"], manifest_info):
        validated_passenger_info = validate_passenger(
            manifest_info=passenger_info,
            id_card=passenger_documents["id_card"],
            boarding_pass=passenger_documents["boarding_pass"],
            person_video=passenger_documents["video"],
            form_client=form_client,
            face_client=face_client,
            indexer=indexer
        )
        validated_manifest_info.append(validated_passenger_info)

    validated_manifest_path = info["manifest"].replace("manifest", "validated_manifest")
    with open(validated_manifest_path, "w") as f:
        writer = csv.DictWriter(f, fieldnames=header)
        writer.writeheader()
        writer.writerows(validated_manifest_info)


if __name__ == "__main__":
    main()
