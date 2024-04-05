import firebase_admin
import json

from firebase_admin import db, credentials

cred = credentials.Certificate("credentials.json")
firebase_admin.initialize_app(cred, {"databaseURL": "https://floor-tiles-vpc-default-rtdb.europe-west1.firebasedatabase.app/" })

ref = db.reference("/Chiese").get()
formatted_ref = json.dumps(ref, indent=4, ensure_ascii=False)
print(formatted_ref)

