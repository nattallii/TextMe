# TextMe
TextMe is a microservices-based backend application built with FastAPI.
The system is designed as a set of independent services responsible for authentication, user profiles, chats and real-time messages.

## Quick navigation
- [Tech Stack](#tech-stack)
- [Architecture Overview](#architecture-overview)
- [Useful Links](#useful-links)
- [How to Start the Project](#how-to-start-the-project)
- [Public API Endpoints (AWS EKS)](#public-api-endpoints-aws-eks)
- [Deployment Overview](#deployment-overview)

## Tech Stack
### Backend

**FastAPI**  
High-performance Python web framework used to build REST APIs.  
Provides automatic OpenAPI/Swagger documentation, request validation, and async support.

**Pydantic**  
Used for data validation and settings management.

**uv**  
Fast Python package and environment manager written in Rust.  
Used as a modern replacement for pip, pip-tools, and virtualenv.

**SQLAlchemy / Alembic**  
SQLAlchemy is used as the ORM for database interaction.  
Alembic is used for database schema migrations.

---

### Databases

**PostgreSQL**  
Relational database used independently by the Auth Service and Profile Service.  
This follows the database-per-service approach and keeps service data isolated.

**MongoDB**  
NoSQL database used by the Chat Service for storing chat-related data.

---

### Containerization

**Docker**  
Used to containerize each microservice and its dependencies.

**Docker Compose**  
Used for local development to run services and databases in a simple way.

---

### Orchestration

**Kubernetes (Minikube)**  
Local Kubernetes cluster used to simulate a production-like environment.

**Helm**  
Package manager for Kubernetes used to:
- deploy services consistently
- manage configuration through values files
- simplify upgrades and re-deployments

---

### CI/CD

**GitHub Actions**  
Used to automate CI pipelines for:
- building Docker images
- pushing images to Docker Hub

---

## Architecture Overview

The project is built as a microservices-based web application.

### Services

**Auth Service**  
Responsible for user registration, login, and authentication.

**Profile Service**  
Responsible for managing user profile data.

**Chat Service**  
Responsible for chat-related functionality and message handling.

### Databases

**Auth Service → PostgreSQL**  
Stores authentication-related data such as users.

**Profile Service → PostgreSQL**  
Stores user profile information.

**Chat Service → MongoDB**  
Stores chat-related data.

### Infrastructure

**Kubernetes + Helm**  
Used for deploying all services and databases in the `textme` namespace.

**Migration Jobs**  
Alembic migrations are executed as Kubernetes Jobs during deployment for services that use PostgreSQL.

---

## Useful Links

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [Docker Documentation](https://docs.docker.com/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Helm Documentation](https://helm.sh/docs/)
- [Minikube Documentation](https://minikube.sigs.k8s.io/docs/)
- [MongoDB Documentation](https://www.mongodb.com/docs/)

---

## Contributing

Contributors should follow the [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) specification for commit messages.

---

## How to Start the Project

### Run Locally with Docker

#### Requirements

- Docker Desktop
- Docker Compose v2

#### Verify installation

```bash
docker version
docker compose version
```

### Start the Application:
1. From the project **root** (where docker-compose.yml is):


`docker compose up -d --build  `

This command will:

- build all Docker images

- start all services and databases

- expose APIs on localhost


2. Open FastAPI docs:

- http://localhost:8000/docs - auth service

- http://localhost:8002/docs - profile service

- http://localhost:8001/docs - chat service

Register user:

**POST** /api/v1/auth/register


Example body:

```
{
  "username": "Natali",
  "password": "1!Stringst",
  "phone": "+380688186966"
}
```

Login:

**POST** /api/v1/auth/login


Example body:
````
{
  "phone": "+380688186966",
  "password": "1!Stringst"
}

````

### Connect to PostgreSQL (Auth Service)
Check if the user was created:
```
docker exec -it fastapiproject-auth_db-1 psql -U authuser -d authdb
\dt
SELECT * FROM users;
```

### Stop Containers
```
docker compose down
```

## Public API Endpoints (AWS EKS)

The application is deployed on Amazon EKS and exposed via an AWS Application Load Balancer (ALB).

You can access the services using the following URLs:

- **Auth Service (Swagger UI):**  
  http://k8s-textme-textmeal-ab3a253012-1439487044.eu-central-1.elb.amazonaws.com/auth/docs

- **Profile Service (Swagger UI):**  
  http://k8s-textme-textmeal-ab3a253012-1439487044.eu-central-1.elb.amazonaws.com/profile/docs

- **Chat Service (Swagger UI):**  
  http://k8s-textme-textmeal-ab3a253012-1439487044.eu-central-1.elb.amazonaws.com/chat/docs

All services are routed through a single AWS Application Load Balancer using path-based routing via Kubernetes Ingress.


## Deployment Overview

The application is deployed to AWS EKS using a full CI/CD pipeline and Kubernetes-based infrastructure.

### 1. Containerization

Each microservice (`auth`, `chat`, `profile`) is containerized using Docker.

Images are built and pushed to Docker Hub:
- natalii571/textme-auth-service
- natalii571/textme-chat-service
- natalii571/textme-profile-service

---

### 2. CI/CD Pipeline

GitHub Actions is used for automation:

- **CI (Build & Push):**
  - Builds Docker images for all services
  - Pushes images to Docker Hub

- **CD (Deploy):**
  - Authenticates to AWS using OIDC
  - Updates kubeconfig for EKS
  - Deploys application using Helmfile

---

### 3. Kubernetes Deployment

The application is deployed using Helm and Helmfile:

- A reusable `app-chart` is used for all services
- Each service has its own `values.yaml`
- Databases are deployed as subcharts:
  - PostgreSQL (for auth & profile)
  - MongoDB (for chat)

---

### 4. Persistent Storage

- AWS EBS volumes are used for persistent storage
- Provisioned dynamically via **EBS CSI Driver**
- PVCs are created for each database

---

### 5. AWS Infrastructure Setup

The following AWS components were configured:

- **Amazon EKS cluster** (via eksctl)
- **IAM roles and OIDC provider** for secure access
- **EBS CSI Driver** for persistent volumes
- **AWS Load Balancer Controller** for Ingress

---

### 6. Ingress & Load Balancing

- Kubernetes Ingress is used for routing
- AWS Load Balancer Controller creates an **Application Load Balancer (ALB)**
- Path-based routing is configured:

  - `/auth` → auth service  
  - `/chat` → chat service  
  - `/profile` → profile service  

---

## Commands used for deployment

```
aws eks describe-cluster --name textme-cluster --region eu-central-1 --query "cluster.resourcesVpcConfig.vpcId" --output text

helm repo add eks https://aws.github.io/eks-charts
helm repo update

curl -Lo iam_policy.json https://raw.githubusercontent.com/kubernetes-sigs/aws-load-balancer-controller/v2.14.1/docs/install/iam_policy.json
aws iam create-policy --policy-name AWSLoadBalancerControllerIAMPolicy --policy-document file://iam_policy.json

eksctl create iamserviceaccount --cluster=textme-cluster --namespace=kube-system --name=aws-load-balancer-controller --attach-policy-arn=arn:aws:iam::585534523982:policy/AWSLoadBalancerControllerIAMPolicy --override-existing-serviceaccounts --approve --region=eu-central-1

helm install aws-load-balancer-controller eks/aws-load-balancer-controller -n kube-system --set clusterName=textme-cluster --set serviceAccount.create=false --set serviceAccount.name=aws-load-balancer-controller --set region=eu-central-1 --set vpcId=ТУТ_ТВІЙ_VPC_ID

kubectl get deployment -n kube-system aws-load-balancer-controller
helmfile -f ./k8s/helmfile.yaml apply
kubectl get ingress -n textme
```