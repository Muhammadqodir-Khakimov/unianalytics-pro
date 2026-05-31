FROM node:20-alpine AS builder

WORKDIR /app

# Build-time args — Railway passes these from env vars automatically
ARG VITE_API_BASE_URL=https://backend-production-9e26.up.railway.app/api/v1
ARG VITE_APP_NAME=RateUP
ARG VITE_DEFAULT_LANG=uz

ENV VITE_API_BASE_URL=$VITE_API_BASE_URL
ENV VITE_APP_NAME=$VITE_APP_NAME
ENV VITE_DEFAULT_LANG=$VITE_DEFAULT_LANG

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

# Production image — nginx serves static files
FROM nginx:alpine

COPY --from=builder /app/dist /usr/share/nginx/html

# Dynamic nginx config — Railway sets $PORT and $BACKEND_URL at runtime
RUN rm -f /etc/nginx/conf.d/default.conf
COPY nginx.conf /etc/nginx/templates/default.conf.template

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
