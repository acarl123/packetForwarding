from flask import Flask, request
from flask.ext.api import status
import Queue


from sniffThread import SniffThread
from writeThread import WriteThread


inputQ = Queue.Queue()
app = Flask(__name__)
app.config.from_object(__name__)


@app.route('/', defaults={'path': ''},methods=['POST'])
@app.route('/<path:path>',methods=['POST'])
def main(path, *args, **kwargs):
    inputQ.put(request.data)
    return request.data, status.HTTP_200_OK


if __name__ == '__main__':

    sniffer = SniffThread()
    sniffer.setDaemon(True)
    sniffer.start()

    writer = WriteThread(inputQ)
    writer.setDaemon(True)
    writer.start()

    app.debug = False
    app.run(host='0.0.0.0')
