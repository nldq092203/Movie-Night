FROM node:18-alpine

WORKDIR /PORTFOLIO

COPY package.json .

RUN npm install

COPY . .

ENV PORT=8080

EXPOSE 8080

CMD [ "npm", "run", "dev"]