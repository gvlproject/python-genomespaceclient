#Override HTTPS connection to read socket directly
import requests.packages.urllib3.util.ssl_
requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS = 'ALL'


def fetch(uri, data):
    session = requests.Session()
    req = session.post(uri, data=data)
    return session

def getToken(session):
    return session.cookies

def example():
    data={"openid.ns":"http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0","openid.identity":"http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select","openid.claimed_id":"http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select","openid.mode":"checkid_setup","openid.realm":"https%3A%2F%2Fgenomespace-dev.genome.edu.au%2Fjsui%2FopenIdClient%3Fis_return%3Dtrue","openid.return_to":"https://genomespace-dev.genome.edu.au/jsui/openIdClient?is_return=true","user_name":"devtest","password":"devtest"}
    url = "https://genomespace-dev.genome.edu.au/identityServer/openIdProvider?_action=authorize"
    import urllib
    data = urllib.urlencode(data)
    res= fetch(url,data)
    dump()

def getGenomeSpaceToken(username, password, gsDNS):
    data = { "openid.ns" : "http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0",
            "openid.identity" : "http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select",
            "openid.claimed_id" : "http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select",
            "openid.mode" : "checkid_setup",
            "openid.realm" : "https%3A%2F%2F" + gsDNS + "%2Fjsui%2FopenIdClient%3Fis_return%3Dtrue",
            "openid.return_to" : "https://" + gsDNS + "/jsui/openIdClient?is_return=true",
            "user_name" : username,
            "password" : password
            }
    url = "https://"+gsDNS+"/identityServer/openIdProvider?_action=authorize"
    session = fetch(url,data)
	#print res.headers
    return getToken(session)