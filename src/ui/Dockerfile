# Build configuration 
FROM node:22-alpine AS builder

WORKDIR /app
COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

# Production server via Nginx
FROM nginx:alpine

# Copy the static output
COPY --from=builder /app/dist /usr/share/nginx/html

# Expose standard port
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
