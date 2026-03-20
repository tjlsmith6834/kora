# ECR repo prefix
ECR_REPO=430118846553.dkr.ecr.us-east-2.amazonaws.com/kora/accounts-service

# AWS
AWS_REGION := us-east-2

# Function image tags
FUNCTIONS=\
	validate-organization-id-function \
	create-user-function \
	get-user-function \
	validate-public-key-function \
	get-public-key-function

IMAGES=\
	$(ECR_REPO):validate-organization-id-function-latest \
	$(ECR_REPO):create-user-function-latest \
	$(ECR_REPO):get-user-function-latest \
	$(ECR_REPO):validate-public-key-function-latest \
	$(ECR_REPO):get-public-key-function-latest

LAMBDA_FILES = \
  validate-organization-id-function.json \
  create-user-function.json \
  get-user-function.json \
  validate-public-key-function.json \
  get-public-key-function.json

.PHONY: ecr-login
ecr-login:
	aws ecr get-login-password --region $(AWS_REGION) | docker login --username AWS --password-stdin $(ECR_REPO)

# Build all functions using docker compose
.PHONY: build
build:
	docker compose -f docker-compose.prod.yml build

# Individual push targets
.PHONY: push-validation-organization-id-function
push-validate-organization-id-function:
	docker push $(ECR_REPO):validate-organization-id-function-latest

.PHONY: push-create-user-function
push-create-user-function:
	docker push $(ECR_REPO):create-user-function-latest

.PHONY: push-get-user-function
push-get-user-function:
	docker push $(ECR_REPO):get-user-function-latest

.PHONY: push-validate-public-key-function
push-validate-public-key-function:
	docker push $(ECR_REPO):validate-public-key-function-latest

.PHONY: push-get-public-key-function
push-get-public-key-function:
	docker push $(ECR_REPO):get-public-key-function-latest

# Push all images
.PHONY: push-all
push-all: \
	push-validate-organization-id-function \
	push-create-user-function \
	push-get-user-function \
	push-validate-public-key-function \
	push-get-public-key-function

.PHONY: deploy-all
deploy-all: ecr-login build push-all
	@echo "✅ All images built and pushed!"

.PHONY: release-validate-organization-id-function
release-validate-organization-id-function:
	@echo "📦 Deploying validate-organization-id-function.json"
	@if ! aws lambda create-function --cli-input-json file://validate-organization-id-function.json 2>/dev/null; then \
		echo "🔁 Updating validate-organization-id-function"; \
		aws lambda update-function-code \
			--function-name validate-organization-id-function \
			--image-uri 430118846553.dkr.ecr.us-east-2.amazonaws.com/kora/accounts-service:validate-organization-id-function-latest; \
	fi

.PHONY: release-create-user-function
release-create-user-function:
	@echo "📦 Deploying create-user-function.json"
	@if ! aws lambda create-function --cli-input-json file://create-user-function.json 2>/dev/null; then \
		echo "🔁 Updating create-user-function"; \
		aws lambda update-function-code \
			--function-name create-user-function \
			--image-uri 430118846553.dkr.ecr.us-east-2.amazonaws.com/kora/accounts-service:create-user-function-latest; \
	fi

.PHONY: release-get-user-function
release-get-user-function:
	@echo "📦 Deploying get-user-function.json"
	@if ! aws lambda create-function --cli-input-json file://get-user-function.json 2>/dev/null; then \
		echo "🔁 Updating get-user-function"; \
		aws lambda update-function-code \
			--function-name get-user-function \
			--image-uri 430118846553.dkr.ecr.us-east-2.amazonaws.com/kora/accounts-service:get-user-function-latest; \
	fi

.PHONY: release-validate-public-key-function
release-validate-public-key-function:
	@echo "📦 Deploying validate-public-key-function.json"
	@if ! aws lambda create-function --cli-input-json file://validate-public-key-function.json 2>/dev/null; then \
		echo "🔁 Updating validate-public-key-function"; \
		aws lambda update-function-code \
			--function-name validate-public-key-function \
			--image-uri 430118846553.dkr.ecr.us-east-2.amazonaws.com/kora/accounts-service:validate-public-key-function-latest; \
	fi

.PHONY: release-get-public-key-function
release-get-public-key-function:
	@echo "📦 Deploying get-public-key-function.json"
	@if ! aws lambda create-function --cli-input-json file://get-public-key-function.json 2>/dev/null; then \
		echo "🔁 Updating get-public-key-function"; \
		aws lambda update-function-code \
			--function-name get-public-key-function \
			--image-uri 430118846553.dkr.ecr.us-east-2.amazonaws.com/kora/accounts-service:get-public-key-function-latest; \
	fi

.PHONY: release-all
release-all: \
	release-validate-organization-id-function \
	release-create-user-function \
	release-get-user-function \
	release-validate-public-key-function \
	release-get-public-key-function
	@echo "✅ All Lambda functions deployed."