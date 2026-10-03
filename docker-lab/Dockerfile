# Base image: lightweight Nginx web server on Alpine Linux
FROM nginx:alpine

# Metadata about the image author
LABEL maintainer="Ayush Patel (202301084)"

# Copy our web page into Nginx's default web root
COPY app/index.html /usr/share/nginx/html/index.html

# Document that the container listens on port 80
EXPOSE 80

# Start Nginx in the foreground so the container keeps running
CMD ["nginx", "-g", "daemon off;"]
