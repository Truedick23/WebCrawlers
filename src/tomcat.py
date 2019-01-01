import requests
url = 'http://192.168.43.91:8081/Experment1/test'
params = {}
for i in range(100):
    r = requests.post(url=url, data=params, timeout = 3)
