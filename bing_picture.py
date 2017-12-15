import http.client, urllib.request, urllib.parse, urllib.error
import json
import random

headers = {
    # Request headers
    'Ocp-Apim-Subscription-Key': '04c7bd61632f460ba42504b2d88f66c1',
}

params = urllib.parse.urlencode({
    # Request parameters
    'q': 'cats',
    'count': '10',
    'offset': '0',
    'mkt': 'en-us',
    'safeSearch': 'Moderate',
})


def find_picture(query):

    params = urllib.parse.urlencode({
        # Request parameters
        'q': query,
        'count': '10',
        'offset': '0',
        'mkt': "ru-RU",
        'safeSearch': 'Moderate',
    })

    conn = http.client.HTTPSConnection('api.cognitive.microsoft.com')
    conn.request("GET", "/bing/v7.0/images/search?%s" % params, "{body}", headers)
    response = conn.getresponse()

    data = json.load(response)
    lenght = len(data["value"])
    try:
        minimum =  min(10, lenght - 1)
        return data["value"][random.randint(0, minimum)]["thumbnailUrl"]
    except Exception:
        return
