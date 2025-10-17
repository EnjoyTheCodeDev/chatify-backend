# ChatApp

A full-stack **chat application** built with **FastAPI** (backend) and **React + Vite** (frontend).

The project is containerized with Docker and designed for easy local development via `docker compose`.

## Overview

The goal of this project is to create a modern real-time chat app using a clean and maintainable full-stack setup.  
It includes separate services for frontend, backend, and database, all orchestrated through Docker.

## ⚙️ Tech Stack

### Frontend
- **React + Vite** — fast and modern dev environment
- **TypeScript** for type safety
- **ESLint** for linting and code quality

### Backend
- **FastAPI (Python)** — high-performance API framework
- **Uvicorn** — ASGI server
- **PostgreSQL** — relational database

### Infrastructure
- **Docker & Docker Compose** — container orchestration
- **Nginx** *(planned for production)* — serving static frontend build

## ⚙️ Getting Started (via Docker)

### Clone the repository
```bash
git clone https://...
```
### Build and run
```bash
docker compose up --build
```

### Frontend
``` bash
cd frontend
npm install
npm run dev
```


### Backend
``` bash
cd backend
docker exec -it meduz-chat-backend-1 bash
source .venv/bin/activate
alembic revision --autogenerate -m "init"
alembic upgrade head
``````
