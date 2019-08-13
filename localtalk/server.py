import signal
import sys
import logging
from socket import socket, AF_INET, SOCK_STREAM, SOCK_DGRAM
from threading import Thread

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())


class Server:
    def __init__(self, host='', port=4000, buffer_size=4096):
        self._host = host
        self._port = port
        self._buffer_size = buffer_size
        self._addresses = {}
        self._server = socket(family=AF_INET, type=SOCK_STREAM)
        self._accept_thread = None
        self._voice_server = VoiceServer()
        self._voice_server.start()
        # must handle any signals to kill gracefully
        signal.signal(signal.SIGINT, self._handler)

    @property
    def server(self):
        return self._server

    def start(self):
        logger.debug('Starting server...')
        try:
            self._server.bind((self._host, self._port))
            self._server.listen(2)

            logger.debug('Waiting for connections...')

            self._accept_thread = Thread(target=self._handle_connections)
            self._accept_thread.start()
        except OSError:
            logger.error('Server Busy, Something wrong!')

    def _handle_connections(self):
        while True:
            try:
                socket_client, address = self._server.accept()
                client = Client(
                    address,
                    socket_client,
                    buffer_size=self._buffer_size,
                    broadcast_callback=self._broadcast_sound,
                    disconnected_callback=self._client_disconnected
                )
                logger.debug(f'({client}) is connected..')
                client.listen()
                # Thread(target=self._client_connection, args=(client,)).start()
                self._addresses[address] = client
            except ConnectionAbortedError as e:
                logger.error(f'ERROR: {e.errno}')
                if e.errno == 53:  # Software caused connection abort
                    break
                continue

    def _client_connection(self, client):
        while True:
            data = client.recv(self._buffer_size)
            if len(data) == 0:  # we have a disconnect...
                logger.debug(f'Client: {client.getpeername()} disconnected')
                self._addresses.pop(client.getpeername(), None)
                break
            self._broadcast_sound(client, data)

    def _client_disconnected(self, client):
        logger.debug(f'Client: {client} disconnected')
        self._addresses.pop(str(client), None)

    def _broadcast_sound(self, client_socket, data_to_be_sent):
        for address in self._addresses:
            client = self._addresses[address]
            if client != client_socket:
                client.broadcast(data_to_be_sent)

    def _handler(self, signum, frame):
        if signum == 2:
            self._server.close()
            self._accept_thread.join()
            # I have no idea why it doesn't kill it correctly.. so annoying.. thread if dead
            # print(self._accept_thread.isAlive())
            # time.sleep(.5)
            sys.exit(0)

    def get_clients(self):
        return self._addresses


class VoiceServer:
    def __init__(self, host='', port=6666, buffer_size=4096):
        self._host = host
        self._port = port
        self._buffer_size = buffer_size
        self._server = socket(family=AF_INET, type=SOCK_DGRAM)
        self._accept_thread = None

    def start(self):
        logger.debug('Starting voice server...')
        try:
            self._server.bind((self._host, self._port))

            logger.debug('Waiting for connections...')

            self._accept_thread = Thread(target=self._handle)
            self._accept_thread.start()
        except OSError as e:
            logger.error('Server Busy, Something wrong!')

    def _handle(self):
        while True:
            # get the data sent to us
            data, ip = self._server.recvfrom(1024)

            # display
            print("{}: {}".format(ip, data.decode(encoding="utf-8").strip()))

            # echo back
            self._server.sendto(data, ip)


class Client:
    def __init__(self, address, client, buffer_size=4096, broadcast_callback=None, disconnected_callback=None):
        self.address = address
        self.client = client
        self.disconnected = False
        self._buffer_size = buffer_size
        self._broadcast_callback = broadcast_callback
        self._disconnected_callback = disconnected_callback

    def __str__(self):
        return str(self.address)

    def listen(self,):
        Thread(target=self._listen).start()

    def broadcast(self, data):
        self.client.sendall(data)

    def _listen(self):
        while True:
            try:
                data = self.client.recv(self._buffer_size)
                if len(data) == 0:  # we have a disconnect...
                    self.disconnected = True
                    self.client.close()
                    if self._disconnected_callback is not None:
                        self._disconnected_callback(self)
                    break
                if self._broadcast_callback is not None:
                    self._broadcast_callback(self, data)
            except ConnectionResetError as e:
                self.disconnected = True
                if self._disconnected_callback is not None:
                    self._disconnected_callback(self)
                if e.errno == 54:
                    logger.error('ERR: 54 Connection reset by peer')
