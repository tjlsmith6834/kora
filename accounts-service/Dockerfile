# Stage 1: Build TypeScript
FROM node:18 AS build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# Stage 2: Runtime image
FROM public.ecr.aws/lambda/nodejs:18
WORKDIR /var/task

# Copy build output
COPY --from=build /app/dist ./

# Copy necessary support files
COPY --from=build /app/package*.json ./
COPY --from=build /app/node_modules ./node_modules/