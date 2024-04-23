# student-rest-api

Check it out [render link](https://student-rest-api-0-0-2.onrender.com/)

[Docker hub](https://hub.docker.com/repository/docker/kurayami07734/student-rest-api/general)

Added **rate limiting** based on ip address of caller

### Run locally

`docker compose up` starts the api at [`http://localhost:8000`](http://localhost:8000)

#### Cold Start Warning

API maybe slow on first request after a while. (It spins down due to inactivity)
Due to being hosting on free tier of render.com