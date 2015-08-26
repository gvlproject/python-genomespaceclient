#Override HTTPS connection to read socket directly
import httplib, ssl, urllib2, socket
class HTTPSConnectionV3(httplib.HTTPSConnection):
    def __init__(self, *args, **kwargs):
        httplib.HTTPSConnection.__init__(self, *args, **kwargs)

    def connect(self):
        sock = socket.create_connection((self.host, self.port), self.timeout)
        if self._tunnel_host:
            self.sock = sock
            self._tunnel()
        try:
            self.sock = ssl.wrap_socket(sock, self.key_file, self.cert_file, ssl_version=ssl.PROTOCOL_SSLv3)
        except ssl.SSLError, e:
            print("Trying SSLv3.")
            self.sock = ssl.wrap_socket(sock, self.key_file, self.cert_file, ssl_version=ssl.PROTOCOL_SSLv23)

#This part is necassaru for avoiding erros in SSL3 connection if the server rejects SSL3. SSL3 isknown to be risky
class HTTPSHandlerV3(urllib2.HTTPSHandler):
    def https_open(self, req):
        return self.do_open(HTTPSConnectionV3, req)
# install opener
urllib2.install_opener(urllib2.build_opener(HTTPSHandlerV3()))
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.poolmanager import PoolManager
import ssl
from functools import wraps
def sslwrap(func):
    @wraps(func)
    def bar(*args, **kw):
        kw['ssl_version'] = ssl.PROTOCOL_TLSv1
        return func(*args, **kw)
    return bar

ssl.wrap_socket = sslwrap(ssl.wrap_socket)


#Reading cookie part to get the token
import cookielib
cookies = cookielib.LWPCookieJar()
handlers = [
    urllib2.HTTPHandler(),
    urllib2.HTTPSHandler(),
    urllib2.HTTPCookieProcessor(cookies)
    ]
opener = urllib2.build_opener(*handlers)

def fetch(uri, data):
    req = urllib2.Request(uri, data)
    return opener.open(req)

def dump():
    for cookie in cookies:
        print cookie.name, cookie.value
def getToken():
        tkn=""
        for cookie in cookies:
		#print cookie.name, cookie.value
                tkn+=cookie.name+"="+cookie.value + ";"
	if len(tkn)>0:
		tkn = tkn[0:len(tkn)-1]
        return tkn

def example():
        data={"openid.ns":"http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0","openid.identity":"http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select","openid.claimed_id":"http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select","openid.mode":"checkid_setup","openid.realm":"https%3A%2F%2Fgenomespace-dev.genome.edu.au%2Fjsui%2FopenIdClient%3Fis_return%3Dtrue","openid.return_to":"https://genomespace-dev.genome.edu.au/jsui/openIdClient?is_return=true","user_name":"devtest","password":"devtest"}
        url = "https://genomespace-dev.genome.edu.au/identityServer/openIdProvider?_action=authorize"
        import urllib
        data = urllib.urlencode(data)
        res= fetch(url,data)
        dump()
def getGenomeSpaceToken(username, password):
        data={"openid.ns":"http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0","openid.identity":"http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select","openid.claimed_id":"http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select","openid.mode":"checkid_setup","openid.realm":"https%3A%2F%2Fgenomespace-dev.genome.edu.au%2Fjsui%2FopenIdClient%3Fis_return%3Dtrue","openid.return_to":"https://genomespace-dev.genome.edu.au/jsui/openIdClient?is_return=true","user_name":username,"password":password}
        url = "https://genomespace-dev.genome.edu.au/identityServer/openIdProvider?_action=authorize"
        import urllib
        data = urllib.urlencode(data)
        res= fetch(url,data)
	#print res.headers
	return getToken()

def uploadToGenomeSpaceRequest(folderURL, sourceURL, username, password):
        opener = urllib2.build_opener(urllib2.HTTPHandler)
        request = urllib2.Request(folderURL, data='{"isDirectory":"true"}')
        request.add_header('x-gs-fetch-source', sourceURL)
        request.add_header('Cookie',getGenomeSpaceToken(username, password))
        request.add_header('Content-Type', 'application/json')
        request.get_method = lambda: 'PUT'
	try:
        	resp = opener.open(request)
		print resp.read()	
	except urllib2.HTTPError as e:	
		print e.read()
