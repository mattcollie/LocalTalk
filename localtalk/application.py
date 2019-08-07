from localtalk import create_app, create_server

app = create_app()

server = create_server()
server.start()


if __name__ == '__main__':
    app.run(debug=True, host='localhost')

