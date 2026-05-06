FROM node:20-alpine

WORKDIR /app

ENV CHOKIDAR_USEPOLLING=true
ENV WATCHOK_USE_POLLING=true

COPY package*.json ./ 

RUN npm install

COPY . .

EXPOSE 3000

CMD [ "npm", "start" ]