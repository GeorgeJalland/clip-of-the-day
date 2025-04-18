# Clip of the Day

Web App that displays Rocket League clips and allows users to rate their favourites. 

## Components

### Web App

Python Flask Web App with Frontend written in **HTML**, **Vanilla JS** and **CSS**. Current setup using **Sqlite** Database.

### File Watcher

File watcher implemented using Python's **Watchdog** library, responsible for populating the database when new videos arrive in the video landing directory.

### Nginx

Nginx is used as a webserver in production for the Flask App, configs in this repo

### Syncthing

Syncthing Open Source app used to sync client filesystems (Windows Game Capture Folder) with the server's video landing directory.

*No Code in this Repo for this.*

## Setup

*Requires: python =~ 3.10*

### Venv

``` bash
python -m venv venv
source venv/bin/activate #bash
source venv/Scripts/activate #git-bash
```

### Environment Variables

- VIDEO_DIRECTORY (user by both Apps)
- SECRET_KEY (used by Flask)


### Install Requirements

#### Flask App

```bash
pip install -r app/requirements.txt
```

#### File-Watcher App

```bash
pip install -r file_watcher/requirements.txt
```

### Database

Create sqlite database under instance/app.db by running

```bash
mkdir ./instance
touch ./instance.db
sqlite3 ./instance/app.db #check
```

### Running Apps Locally

#### Flask

```bash
FLASK_APP=app.app:create_app flask run --debug -p 8000
```

#### File Watcher
```bash
python -u -m file_watcher.file_watcher
```

### Docker

We have to be careful when running docker commands with sudo since we rely on ENV VARS and super user doesn't necessarily have access to the users's. It is easier to run sudo for build and run/up commands as standard user

#### Both
```bash
sudo docker compose build
docker compose up --detach
```


#### Flask App
```bash
sudo docker compose build clip-of-the-day
docker compose up --detach clip-of-the-day
```

#### File Watcher
```bash
sudo docker compose build file_watcher
docker compose up --detach file_watcher
```