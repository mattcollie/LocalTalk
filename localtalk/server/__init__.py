import signal
import sys
from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread

from localtalk.server.connection import Connections


class Server:
    def __init__(self, host='127.0.0.1', port=4000, buffer_size=4096):
        self._host = host
        self._port = port
        self._buffer_size = buffer_size
        self._addresses = {}
        self._server = socket(family=AF_INET, type=SOCK_STREAM)
        self._accept_thread = None
        # must handle any signals to kill gracefully
        signal.signal(signal.SIGINT, self._handler)

    @property
    def server(self):
        return self._server

    def start(self):
        print('starting server...')
        try:
            self._server.bind((self._host, self._port))
            self._server.listen(2)

            print("Waiting for connection..")

            self._accept_thread = Thread(target=Connections, args=(self,))
            self._accept_thread.start()
        except OSError:
            print('Server Busy!! Something wrong')

    def _handler(self, signum, frame):
        if signum == 2:
            self._server.close()
            self._accept_thread.join()
            # I have no idea why it doesn't kill it correctly.. so annoying.. thread if dead
            # print(self._accept_thread.isAlive())
            # time.sleep(.5)
            sys.exit(0)

    def client_connection_sound(self, client):
        while True:
            try:
                data = client.recv(self._buffer_size)
                self._broadcast_sound(client, data)
            except:
                continue

    def _broadcast_sound(self, client_socket, data_to_be_sent):
        for client in self._addresses:
            if client != client_socket:
                client.sendall(data_to_be_sent)

    def get_clients(self):
        return self._addresses
