import requests
KEY = "wJWW3FonxOEDCtGiXXgjTg"
res = requests.get("http://127.0.0.1:5000/book/058606200")

print(res.status_code)