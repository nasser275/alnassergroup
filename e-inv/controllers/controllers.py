from odoo import http
import json
from odoo.http import request


class Einv_Ping(http.Controller):
    @http.route('/ping', type='json', auth="public", csrf=False)
    def index(self, **args):
        global RIN
        rin = {"Rin": "599580968"}
        apikey = "ApiKey 31a42e5b-9e39-4d14-bca8-cb265a8a2075"
        # _response = {"data": {}, "success": True, "statusCode": 200, "message": "Success"}
        _response = {}
        try:
            headers_auth = request.httprequest.headers.get('Authorization')
            # if apikey == headers:
            print(type(rin))
            # _response["rin"] = rin.encode('ascii')
            print("start")
            print(request.httprequest.headers)
            print(request.httprequest.data)
            RIN = json.dumps(rin).encode('utf-8')

            # y = b'{"Rin":"599580968"}'
            # print(y)
            # else:
            #     _response["data"] = "Please Send A correct APIkey"
            # _response = {"data": {"Rin": "599580968"}, "success": True, "statusCode": 200, "message": "Success"}
        except Exception as e:
            _response = {"data": None, "success": False, "statusCode": 500, "message": str(e)}
        return RIN
