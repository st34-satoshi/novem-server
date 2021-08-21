# novem-server
Novem server for playing

## Play
Click [Play Novem](https://novem.stu345.com/play-novem)


## Run
### Local
1. `pip install -r requirements.txt`
2. `gunicorn -b 127.0.0.1:8080 -k flask_sockets.worker server:app`

### Deploy on Google App Engine
1. Create you GCP project
2. `gcloud app deploy --project <project ID>`

#### check your GCP project list
- `gcloud projects list`
- `gcloud app versions list`

### Deploy on VPS
1. `sudo gunicorn -b :PORT -k flask_sockets.worker server:app`