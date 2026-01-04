# Build stage
FROM node:20-alpine AS builder 
# Note: Recommending Node 20 (LTS) for stability over v25

WORKDIR /app

# 1. Copy only dependency files first
COPY package.json package-lock.json ./

# 2. Install ALL dependencies (including devDeps so we can build)
# We use --legacy-peer-deps for that ngx-monaco-editor version mismatch
RUN npm ci --legacy-peer-deps

# 3. Copy the rest of the source code (skipped by cache if package.json hasn't changed)
COPY . .

# 4. Run the build
RUN npm run build -- --configuration=production
# Add this line temporarily after 'RUN npm run build'
RUN ls -R /app/dist
# Production stage
FROM docker.io/library/nginx:1.27-alpine
# Adjust this path based on where Angular 18 actually outputs files 
# (Usually dist/frontend/browser)
COPY --from=builder /app/dist/frontend /usr/share/nginx/html

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]