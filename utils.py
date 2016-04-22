import requests


def POST(data):
    try:
        r = requests.post('http://%s:5000/add' % IP_ADDRESS, data=json.dumps(str(data)))#.encode('string-escape'))
        if r.status_code != 200:
            print 'Server returned status: %s' % r.status_code
        else:
            print 'successfully sent 1 packet: length '+str(len(data))
    except requests.ConnectionError:
        print 'Connection error, please check connection to server'
    except UnicodeDecodeError:
        print '\n\ncan\'t decode: %s\n\n' % data
