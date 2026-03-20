# AWS variables
AWS_REGION := us-east-2
ECR_REPO := 430118846553.dkr.ecr.us-east-2.amazonaws.com/kora/hire
ECS_CLUSTER := kora-cluster-prod

# BFF Variables
BFF_TASK_DEF_FILE := ecs-task-definition-bff.json
BFF_TASK_FAMILY := hire-backend-task
BFF_SERVICE := hire-backend-service

# FE Variables
REACT_DIR := frontend
REACT_BUILD_DIR := $(REACT_DIR)/build
S3_BUCKET := www.my.hirekora.com
CF_DIST_ID := E34Z0MFLFAXMCI

# Internal temp file for task def ARN
BFF_TASK_ARN_FILE := .bff_task_arn.tmp

# --- Auth ---

.PHONY: ecr-login
ecr-login:
	aws ecr get-login-password --region $(AWS_REGION) | docker login --username AWS --password-stdin $(ECR_REPO)

# --- Docker Build & Push ---

.PHONY: build-bff push-bff
build-bff:
	docker-compose -f docker-compose.bff.yml build

push-bff:
	docker-compose -f docker-compose.bff.yml push

.PHONY: push-fe
build-fe:
	cd $(REACT_DIR) && npm run build

.PHONY: sync-fe
sync-fe:
	aws s3 sync $(REACT_BUILD_DIR)/ s3://$(S3_BUCKET) --delete --region $(AWS_REGION)

# --- ECS Deployment Pipeline ---

.PHONY: deploy
deploy: ecr-login build-bff push-bff
	@echo "🎉 BFF Deployment Complete! 🚀"

# Register task and extract ARN
.PHONY: revise-task
revise-task:
	aws ecs register-task-definition \
		--cli-input-json file://$(BFF_TASK_DEF_FILE) \
		--region $(AWS_REGION)

.PHONY: update-service
update-service:
	aws ecs update-service \
		--cluster $(ECS_CLUSTER) \
		--service $(BFF_SERVICE) \
		--task-definition $(BFF_TASK_FAMILY) \
		--region $(AWS_REGION) \
		--force-new-deployment

.PHONY: invalidate-fe
invalidate-fe:
	aws cloudfront create-invalidation \
		--distribution-id $(CF_DIST_ID) \
		--paths "/*" \
		--region $(AWS_REGION)

# Full deploy & update
.PHONY: deploy-update-all
deploy-update-all: deploy revise-task update-service
	@echo "🎉 Full Deployment and Update Complete! 🚀"

.PHONY: deploy-fe
deploy-fe: build-fe sync-fe invalidate-fe
	@echo "✅ React frontend deployed to S3 and cache invalidated!"