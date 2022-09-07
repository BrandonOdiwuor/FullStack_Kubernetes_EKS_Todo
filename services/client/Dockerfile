## Build
FROM node:13-alpine as build
ENV NODE_ENV development

# Add a work directory
WORKDIR /usr/src/app

# Install app dependencies
# A wildcard is used to ensure both package.json AND package-lock.json are copied
COPY package*.json ./
RUN npm ci

# Copy app files
COPY . .

# Build the app
RUN npm run build

# Set up Nginx to serve the build files
FROM nginx:alpine

COPY --from=build /usr/src/app/build /usr/share/nginx/html
COPY --from=build /usr/src/app/nginx/nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]