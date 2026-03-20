#General variables
AWS_REGION := us-east-2
ECR_REPO := 430118846553.dkr.ecr.us-east-2.amazonaws.com/kora/jobs-service
ECS_CLUSTER := kora-cluster-prod

# Celery Worker Variables
CELERY_TASK_FAMILY := jobs-celery-task
CELERY_TASK_DEF_FILE := ecs-task-definition-celery.json
CELERY_SERVICE_DEF_FILE := ecs-service-definition-celery.json
CELERY_SERVICE := applications-celery-service

# AI Gateway Variables
API_TASK_FAMILY := jobs-api-task
API_TASK_DEF_FILE := ecs-task-definition-API.json
API_SERVICE := jobs-api-service


# Production
.PHONY: ecr-login
ecr-login:
	aws ecr get-login-password --region $(AWS_REGION) | docker login --username AWS --password-stdin $(ECR_REPO)

# Update ECR Image
.PHONY: build-celery push-celery
build-celery:
	docker-compose -f docker-compose.celery.yml build

push-celery:
	docker-compose -f docker-compose.celery.yml push

.PHONY: build-api push-api
build-api:
	docker-compose -f docker-compose.api.yml build

push-api:
	docker-compose -f docker-compose.api.yml push

# Update ECS Task Definitions
.PHONY: update-task-celery update-task-api
update-task-celery:
	@echo "Registering new ECS task definition for Celery Worker..."
	aws ecs register-task-definition --family $(CELERY_TASK_FAMILY) --cli-input-json file://$(CELERY_TASK_DEF_FILE)

update-task-api:
	@echo "Registering new ECS task definition for API..."
	aws ecs register-task-definition --family $(API_TASK_FAMILY) --cli-input-json file://$(API_TASK_DEF_FILE)

# Update ECS Services
.PHONY: update-service-celery update-service-gateway
update-service-celery:
	@echo "🚀 Updating ECS service for Celery Worker..."
	aws ecs update-service --cluster $(ECS_CLUSTER) --service $(CELERY_SERVICE) --task-definition $(CELERY_TASK_FAMILY) --force-new-deployment

update-service-api:
	@echo "🚀 Updating ECS service for API..."
	aws ecs update-service --cluster $(ECS_CLUSTER) --service $(API_SERVICE) --task-definition $(API_TASK_FAMILY) --force-new-deployment

# Full Deployment Pipelines
.PHONY: deploy-celery deploy-api deploy-all
deploy-celery: ecr-login build-celery push-celery
	@echo "🎉 Celery Deployment Complete! 🚀"

deploy-api: ecr-login build-api push-api
	@echo "🎉 API Deployment Complete! 🚀"

deploy-all: deploy-celery deploy-api
	@echo "🎉 Full Deployment Complete! 🚀"

# Full update pipelines
.PHONY: update-celery update-api update-all
update-celery: update-task-celery update-service-celery
	@echo "🎉 Celery Update Complete! 🚀"

update-api: update-task-api update-service-api
	@echo "🎉 API Update Complete! 🚀"

update-all: update-celery update-api
	@echo "🎉 Full Update Complete! 🚀"

# Full deploy & update
.PHONY: deploy-update-all
deploy-update-all: deploy-all update-all
	@echo "🎉 Full Deployment and Update Complete! 🚀"