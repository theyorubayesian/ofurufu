import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Variables:
    # ------------
    # BLOB STORAGE
    # ------------
    BLOB_CONNECTION_STRING: str = os.getenv("BLOB_CONNECTION_STRING")
    BLOB_ACCOUNT_KEY: str = os.getenv("BLOB_ACCOUNT_KEY")
    BLOB_ACCOUNT_NAME: str = os.getenv("BLOB_ACCOUNT_NAME")

    # -------------
    # CUSTOM VISION
    # -------------
    CUSTOM_VISION_TRAINING_ENDPOINT: str = os.getenv("CUSTOM_VISION_TRAINING_ENDPOINT")
    CUSTOM_VISION_PREDICTION_ENDPOINT: str = os.getenv("CUSTOM_VISION_PREDICTION_ENDPOINT")
    CUSTOM_VISION_TRAINING_KEY: str = os.getenv("CUSTOM_VISION_TRAINING_KEY")
    CUSTOM_VISION_PREDICTION_KEY: str = os.getenv("CUSTOM_VISION_PREDICTION_KEY")
    CUSTOM_VISION_PROJECT_ID: str = os.getenv("CUSTOM_VISION_PROJECT_ID")
    CUSTOM_VISION_DEFAULT_MODEL_ITERATION_NAME: str = os.getenv("CUSTOM_VISION_DEFAULT_MODEL_ITERATION_NAME")

    # ---------------
    # FACE RECOGNIZER
    # ---------------
    FACE_RECOGNIZER_ENDPOINT: str = os.getenv("FACE_RECOGNIZER_ENDPOINT")
    FACE_RECOGNIZER_SUBSCRIPTION_KEY: str = os.getenv("FACE_RECOGNIZER_SUBSCRIPTION_KEY")
    
    # ---------------
    # FORM RECOGNIZER
    # ---------------
    FORM_RECOGNIZER_KEY: str = os.getenv("FORM_RECOGNIZER_KEY")
    FORM_RECOGNIZER_ENDPOINT: str = os.getenv("FORM_RECOGNIZER_ENDPOINT")
    FORM_RECOGNIZER_TRAINED_MODEL_ID: str = os.getenv("FORM_RECOGNIZER_TRAINED_MODEL_ID")

    # ----------
    # LABEL TOOL
    # ----------
    LABEL_TOOL_TOKEN_NAME: str = os.getenv("LABEL_TOOL_TOKEN_NAME")
    LABEL_TOOL_PROJECT_KEY: str = os.getenv("LABEL_TOOL_PROJECT_KEY")

    # --------------
    # VIDEO ANALYZER
    # --------------
    VIDEO_ANALYZER_SUBSCRIPTION_KEY: str = os.getenv("VIDEO_ANALYZER_SUBSCRIPTION_KEY")
    VIDEO_ANALYZER_ACCOUNT_ID: str = os.getenv("VIDEO_ANALYZER_ACCOUNT_ID")
    VIDEO_ANALYZER_LOCATION: str = os.getenv("VIDEO_ANALYZER_LOCATION")
