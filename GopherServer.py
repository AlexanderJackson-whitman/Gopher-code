'''
A simple Gopher server
'''
import sys, socket
import re
import pandas as pd
import os
# Specification #
# - Each line ends with CRLF
# - Response to empty argument: ls /
#   - 0 line start will be interpreted as a document by client
#   - 1 " directory
#   - 7 " search service
# Tab-denoted blocks
#   #0 user-facing description
#   #1 string client must send to server to retrieve item
#   #2 denote the domain-name of the host that has the do
#   #3 port on which to connect
#   #4+ ignore
#  CR LF (\r\n) denotes end of line

#Open with 'lynx gopher://localhost:5000' (or 'telnet localhost 50000', or
# 'python3 SimpleGopherServer.py' localhost 50000' for simple operations.)
class GopherServer:
    def __init__(self, port=50000):
        self.port = port
        self.host = ""
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))
    def listen(self):
        self.sock.listen(5)
        while True:
            clientSock, clientAddr = self.sock.accept()
            print("Connection received from", clientSock.getpeername())
            request = clientSock.recv(1024) # removed while loop, assuming all reqs <1KiB
            parameters = self.parse(request)
            reply = self.construct(parameters)
            clientSock.sendall(reply)
            clientSock.close()
        print("exiting gopher")
    def parse(self, req): #turn string recvd from Client into actionable instructions
        path = ''
        if req == b'\r\n':
            path = '.'
        else:
            print('req:',req)
            #req=req.decode()
            path = req.decode('utf8').replace('\r\n','')
        return path 

    def construct(self, path): # act on results of decode, turn server state into a string of lines
        rstring = ''
        if path == '.' or path[-1] == '/' or path == '/': #directory
            # link_lines = pd.read_csv(os.path.join('Content',path,'links'), names=['disp_name', 'filename', 'host', 'port'], delimiter='\t')
            # rstring = re.sub(' +', '\t', re.sub('\n +', '\r\n', link_lines.to_string(index=False, header=False)))
            with open(os.path.join('Content',path,'links'), 'r') as link_file:
                links = link_file.read()
            rstring = links.replace('\n', '\r\n')
        else:
            #file
            with open(os.path.join('Content', path), 'r') as txt_file:
                rstring = txt_file.read()

        return bytes(rstring+'.','utf8')

def main():

    if len(sys.argv) > 1:
        try:
            server = GopherServer(int(sys.argv[1]))
        except ValueError as e:
            print("Error in specifying port. Creating server on default port.")
            server = GopherServer()
    else:
        server = GopherServer()

    print("Listening on port", str(server.port))
    server.listen()

if __name__ == '__main__':
    main()
