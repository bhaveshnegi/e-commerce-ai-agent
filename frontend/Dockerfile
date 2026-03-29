FROM nginx:alpine

# Copy static frontend to Nginx's default public directory
COPY index.html /usr/share/nginx/html/index.html

# Expose Nginx port
EXPOSE 80

# Run Nginx in foreground
CMD ["nginx", "-g", "daemon off;"]
