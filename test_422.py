import urllib.request
import urllib.error
import urllib.parse
import json
import jwt
import warnings
from datetime import datetime, timedelta, timezone

warnings.filterwarnings("ignore")

SECRET_KEY = "SUPER_SECRET_KEY_CHANGE_THIS"
token = jwt.encode({"sub": "1", "exp": datetime.now(timezone.utc) + timedelta(hours=1)}, SECRET_KEY, algorithm="HS256")

with open("out.txt", "w") as f:
    req = urllib.request.Request('http://localhost:8000/api/v1/students/1/stats')
    req.add_header('Authorization', 'Bearer ' + token)
    try:
        response = urllib.request.urlopen(req)
        f.write("SUCCESS stats " + str(response.status) + "\n")
    except urllib.error.HTTPError as e:
        f.write("ERROR stats " + str(e.code) + "\n")
        f.write(e.read().decode() + "\n")
