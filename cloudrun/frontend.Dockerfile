# Frontend Dockerfile optimized for Google Cloud Run
# Multi-stage build for smaller image

# Build stage
FROM node:20-alpine AS build

WORKDIR /app

# Copy package files
COPY frontend/package*.json ./

# Install dependencies
RUN npm install --legacy-peer-deps

# Copy source code
COPY frontend/ .

# Build argument for API URL (will be set during build)
ARG VITE_API_URL
ARG VITE_WS_URL

ENV VITE_API_URL=$VITE_API_URL
ENV VITE_WS_URL=$VITE_WS_URL

# Build the app
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built files
COPY --from=build /app/dist /usr/share/nginx/html

# Copy nginx config for SPA routing
COPY cloudrun/nginx.conf /etc/nginx/conf.d/default.conf

# Cloud Run uses PORT environment variable
# We need to update nginx to use it
COPY cloudrun/nginx-entrypoint.sh /docker-entrypoint.d/40-nginx-port.sh
RUN chmod +x /docker-entrypoint.d/40-nginx-port.sh

EXPOSE 8080

CMD ["nginx", "-g", "daemon off;"]
