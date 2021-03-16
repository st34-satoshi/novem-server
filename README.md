# novem-server
Novem server for playing

## Run
### local
`gunicorn -b 127.0.0.1:8080 -k flask_sockets.worker server:app`
