# Running Django Server via Docker

This guide will walk you through the steps to run  Demo Social Media Manager server using Docker. 

## Prerequisites

- Docker installed on your system. You can download and install Docker from [https://www.docker.com/get-started](https://www.docker.com/get-started).
- Basic understanding of Django and Docker concepts.

## Steps

### 1. Clone Your Django Project

Clone the project repository to your local machine if you haven't already done so.

```bash
git clone <repository_url>
cd <project_directory>
```

### 2. Buid Docker Image

```bash
sudo docker build -t demo_sm_manager .
```

### 3. Run Docker Image on local port 8000

```bash
docker run -it -p 8000:8000 -d demo_sm_manager
```
Bravo. That's it. Now lets test if it is running or not

Search this link http://localhost:8000/admin/ on any browser. If you are able to see login page of Django Admin, Then it done. You can test your APIs in POSTMAN
