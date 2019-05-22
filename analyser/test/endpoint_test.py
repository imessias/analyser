import unittest
import httplib, urllib, base64

class LUISEndpointTest(unittest.TestCase):

    def testEndpoint(self):

        headers = {
            # Request headers
            'Ocp-Apim-Subscription-Key': '{subscription key}',
        }

        params = urllib.urlencode({
            # Request parameters
            'timezoneOffset': '{number}',
            'verbose': '{boolean}',
            'spellCheck': '{boolean}',
            'staging': '{boolean}',
            'bing-spell-check-subscription-key': '{string}',
            'log': '{boolean}',
        })

        try:
            conn = httplib.HTTPSConnection('westus.api.cognitive.microsoft.com')
            conn.request("GET", "/luis/v2.0/apps/{appId}?q={q}&%s" % params, "{body}", headers)
            response = conn.getresponse()
            data = response.read()
            print(data)
            conn.close()
        except Exception as e:
            print("[Errno {0}] {1}".format(e.errno, e.strerror))

        ####################################

        ########### Python 3.2 #############
        import http.client, urllib.request, urllib.parse, urllib.error, base64

        headers = {
            # Request headers
            'Ocp-Apim-Subscription-Key': '{subscription key}',
        }

        params = urllib.parse.urlencode({
            # Request parameters
            'timezoneOffset': '{number}',
            'verbose': '{boolean}',
            'spellCheck': '{boolean}',
            'staging': '{boolean}',
            'bing-spell-check-subscription-key': '{string}',
            'log': '{boolean}',
        })

        try:
            conn = http.client.HTTPSConnection('westus.api.cognitive.microsoft.com')
            conn.request("GET", "/luis/v2.0/apps/{appId}?q={q}&%s" % params, "{body}", headers)
            response = conn.getresponse()
            data = response.read()
            print(data)
            conn.close()
        except Exception as e:
            print("[Errno {0}] {1}".format(e.errno, e.strerror))

        ####################################


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(LUISEndpointTest)
    unittest.TextTestRunner().run(suite)
