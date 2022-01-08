ALL_SUCCESSFUL_MESSAGE = \
    """
    Dear {first_name} {last_name},
    You are welcome to flight {flightno} leaving at {flight_time} from {origin} to {destination}.
    Your seat number is A5, and it is confirmed.
    We did not find a prohibited item (lighter) in your carry-on baggage, 
    thanks for following the procedure.
    Your identity is verified so please board the plane.
    """

FACE_ID_FAILS_MESSAGE = \
    """
    Dear {first_name} {last_name},
    You are welcome to flight {flightno} leaving at {flight_time} from {origin} to {destination}.
    Your seat number is A5, and it is confirmed.
    We did not find a prohibited item (lighter) in your carry-on baggage. 
    Thanks for following the procedure.
    Your identity could not be verified. Please see a customer service representative.
    """

LIGHTER_DECTECTED_MESSAGE = \
    """
    Dear {first_name} {last_name},
    You are welcome to flight {flightno} leaving at {flight_time} from {origin} to {destination}.
    Your seat number is A5, and it is confirmed.
    We have found a prohibited item in your carry-on baggage, and it is flagged for removal. 

    Your identity is verified. However, your baggage verification failed, so please see a customer service representative.
    """

FLIGHT_INFO_MISMATCH = \
    """
    Dear Sir/Madam,
    Some of the information in your boarding pass does not match the flight manifest data, so you cannot board the plane.
    Please see a customer service representative.
    """

# PII - Personal Identification Information
PII_MISMATCH_MESSAGE = \
    """
    Dear Sir/Madam,
    Some of the information on your {document} does not match the flight manifest data, so you cannot board the plane.
    Please see a customer service representative.
    """