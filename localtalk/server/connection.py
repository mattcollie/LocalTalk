import threading


class Connections(threading.Thread):

    def __init__(self, server):
        super().__init__()
        self.kill = False
        self._server = server.server
        self._addresses = server._addresses
        self._client_connection_sound = server.client_connection_sound

        self._run()

    def _run(self):
        while True:
            try:
                print("trying to find a client")
                client, addr = self._server.accept()
                print("{} is connected!!".format(addr))
                self._addresses[client] = addr
                threading.Thread(target=self._client_connection_sound, args=(client,)).start()
            except ConnectionAbortedError as e:
                if e.errno == 53:  # Software caused connection abort
                    break
                continue
