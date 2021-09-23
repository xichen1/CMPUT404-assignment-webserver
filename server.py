#  coding: utf-8 
import socketserver
from os import getcwd, path
import os

# Copyright 2013 Abram Hindle, Eddie Antonio Santos, Xichen Pan
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/


error404 = '''
        <!DOCTYPE html>
        <html>
            <body>404 Not Found</body>
        </html>
'''

class MyWebServer(socketserver.BaseRequestHandler):
    response = ""

    #reference: https://security.openstack.org/guidelines/dg_using-file-paths.html
    def is_safe_path(self, basedir, path):
        # resolves symbolic links
        matchpath = os.path.realpath(path)
        return basedir == os.path.commonpath((basedir, matchpath))

    def status404(self):
        self.response = "HTTP/1.1 404 Not Found\r\nContent-Type: text/html; charset=utf-8\r\n\r\n" + error404 + "\r\n"
        return

    # When the request item type is file
    def handleFile(self, filePath):
        # identify it requires .html or .css
        _name, extension = os.path.splitext(filePath)
        webFile = open(filePath)
        if(extension == ".html"):
            self.response = "HTTP/1.1 200 OK\r\nContent-Type: text/html; charset=utf-8\r\n\r\n" + webFile.read() + "\r\n"
        elif(extension == ".css"):
            self.response = "HTTP/1.1 200 OK\r\nContent-Type: text/css; charset=utf-8\r\n\r\n" + webFile.read() + "\r\n"
        else:
            self.response = "HTTP/1.1 200 OK\r\nContent-Type: application/octet-stream\r\n\r\n" + webFile.read() + "\r\n"
        webFile.close()
        return
    
    # When the request item type is dir
    def handleDir(self, filePath, requestUrl):
        # redirect the the url end with /
        if(requestUrl[-1] != "/"):
            newLocation = "http://127.0.0.1:8080" + requestUrl + "/"
            self.response = "HTTP/1.1 301 Moved Permanently\r\nLocation: " + newLocation + "\r\n\r\n"
        else:
            if(path.isfile(filePath+"index.html")):
                htmlFile = open(filePath+"index.html")
                self.response = "HTTP/1.1 200 OK\r\nContent-Type: text/html; charset=utf-8\r\n\r\n" + htmlFile.read() + "\r\n"
                htmlFile.close()
            else:
                self.status404()
        return

    def handleUrl(self, requestList):
        requestUrl = requestList[0].split()[1]
        filePath = "www" + requestUrl
        # if it goes outside ./www dir
        if(self.is_safe_path(path.join(getcwd(), "www"), path.join(getcwd(), "www" + requestUrl)) == False):
            self.status404()
            return
        if(path.isdir(filePath)):
            self.handleDir(filePath, requestUrl)
        elif(path.isfile(filePath)):
            self.handleFile(filePath)
        else:
            self.status404()
        return

    def handleRequestType(self, requestList):
        requestType = requestList[0].split()[0]
        if (requestType != "GET"):
            self.response = "HTTP/1.1 405 Method Not Allowed\r\n\r\n"
            return
        else:
            self.handleUrl(requestList)
            return


    def handle(self):
        self.data = self.request.recv(1024).strip()

        # only send response when request is valid
        if(len(self.data) > 0):
            requestList = self.data.decode("utf-8").split('\n')
            self.handleRequestType(requestList)
            self.request.sendall(bytearray(self.response,'utf-8'))
        else:
            print("Bad request")

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
