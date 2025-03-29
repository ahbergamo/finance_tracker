FROM nginx:latest

# Copy your local nginx.conf into the container
COPY nginx.conf /etc/nginx/conf.d/default.conf

