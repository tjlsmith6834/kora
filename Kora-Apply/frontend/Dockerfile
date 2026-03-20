FROM node:20-alpine

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY ./src/ ./src
COPY tsconfig.json .
##COPY webpack.common.js ignore_dev ./
COPY webpack.config.js ./

EXPOSE 3001

CMD ["npm", "run", "start"]