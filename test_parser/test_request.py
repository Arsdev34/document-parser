import requests

url = "http://127.0.0.1:8000/analyze/"
files = {"file": ("test.pdf", open("test.pdf", "rb"), "application/pdf")}

response = requests.post(url, files=files)
print("Status:", response.status_code)
print("Response:", response.json())
