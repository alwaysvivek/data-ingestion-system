# Stage 1: Build the React application
FROM node:20-alpine as build-stage

WORKDIR /app

# Copy package.json and install dependencies
COPY package*.json ./
RUN npm install

# Copy source code and build
COPY . .
RUN npm run build

# Stage 2: Serve with Nginx
FROM nginx:alpine

# Create a non-root user and setup directories
RUN addgroup -S appgroup && adduser -S appuser -G appgroup \
    && touch /var/run/nginx.pid \
    && chown -R appuser:appgroup /var/run/nginx.pid /var/cache/nginx /var/log/nginx /etc/nginx/conf.d

# Copy build artifacts from stage 1
COPY --from=build-stage /app/dist /usr/share/nginx/html
RUN chown -R appuser:appgroup /usr/share/nginx/html

# Copy custom Nginx config for non-root user
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Switch to non-root user
USER appuser

# Expose the Nginx port (using 8080 for non-root compliance)
EXPOSE 8080

# Healthcheck for automated monitoring
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD wget -q -O - http://localhost:8080/ || exit 1

# Run Nginx
CMD ["nginx", "-g", "daemon off;"]
