FROM node:20-slim AS build
WORKDIR /app
COPY frontend/package.json ./
RUN npm install
COPY frontend/ ./
ARG VITE_API_BASE_URL
ENV VITE_API_BASE_URL=${VITE_API_BASE_URL}
RUN npm run build

# Dev-only stage: runs Vite's own dev server so `docker compose watch` has
# something that actually rebuilds on file changes. Not used in production -
# `docker build` targets the last stage below by default, so this is only
# reached when docker-compose.yml explicitly sets `target: dev`.
FROM node:20-slim AS dev
WORKDIR /app
COPY frontend/package.json ./
RUN npm install
COPY frontend/ ./
EXPOSE 5173
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "5173"]

FROM node:20-slim
WORKDIR /app
RUN npm install -g serve
COPY --from=build /app/dist ./dist
EXPOSE 4173
CMD ["serve", "-s", "dist", "-l", "4173"]