python -m ofurufu.form_recognizer --analyze-document --document-type id --documents identity_cards/babatundesimpson.png

python -m ofurufu.form_recognizer --analyze-document --document-type boarding-pass --documents boarding_pass/usmanaderibigbe.pdf

python main.py --create-person-group --person-group-name ofurufu-passenger --identity-cards identity_cards/jidejackson.png