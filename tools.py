import requests


class LngLat:
    def __init__(self):
        self.domain = 'http://restapi.amap.com/v3/geocode/geo?'
        self.key = '7393f73a51c44149dc5d742aea0013dd'

    # 请求某一个地址
    def gaode_api(self, addr):
        url = self.domain + 'key=' + self.key + '&address=' + addr
        req = requests.get(url)
        data = req.json()
        geocode = data['geocodes']
        if geocode:
            lnglat = geocode[0]['location']
            lng, lat = [float(i) for i in lnglat.split(',')]
            return [lng,lat]