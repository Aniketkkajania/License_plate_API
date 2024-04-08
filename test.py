import requests

url = 'http://localhost:5001/api/detect_plate'
files = {'image': open('ford.jpg', 'rb')}

response = requests.post(url, files=files)

if response.status_code == 200:
    with open('detected_plate.jpg', 'wb') as f:
        f.write(response.content)
    print('License plate detected and saved as detected_plate.jpg')
else:
    print('Error:', response.json()['error'])
