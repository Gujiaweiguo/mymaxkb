# syntax=docker/dockerfile:1

ARG NODE_IMAGE=docker.m.daocloud.io/library/node:24-alpine
ARG PYTHON_IMAGE=docker.m.daocloud.io/library/python:3.11-slim-bookworm

# ---------- frontend build ----------
FROM ${NODE_IMAGE} AS web-build

ARG NPM_REGISTRY=https://registry.npmmirror.com
ARG NODE_OPTIONS=--max-old-space-size=4096

ENV NODE_OPTIONS=${NODE_OPTIONS}

WORKDIR /build/ui

COPY ui/package.json ./
RUN --network=host npm config set registry ${NPM_REGISTRY} && npm install --no-audit --prefer-offline

COPY ui/ ./
RUN npm run build-only && npm run build-only-chat

# ---------- app runtime ----------
FROM ${PYTHON_IMAGE}

ARG PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple
ARG APT_MIRROR=mirrors.tuna.tsinghua.edu.cn

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    MAXKB_CONFIG_TYPE=ENV \
    MAXKB_DB_NAME=maxkb \
    MAXKB_DB_HOST=127.0.0.1 \
    MAXKB_DB_PORT=5432 \
    MAXKB_DB_USER=maxkb \
    MAXKB_DB_PASSWORD=build_placeholder \
    MAXKB_REDIS_HOST=127.0.0.1 \
    MAXKB_REDIS_PORT=6379 \
    MAXKB_REDIS_PASSWORD=build_placeholder \
    MAXKB_REDIS_DB=0 \
    MAXKB_SECRET_KEY=build_placeholder_secret \
    MAXKB_HMAC_SIGNED_SERIALIZER_SECRET_KEY=build_placeholder_hmac

WORKDIR /opt/maxkb-app

COPY pyproject.toml ./
RUN --network=host pip config set global.index-url ${PIP_INDEX_URL} && \
    pip install --no-cache-dir uv && \
    UV_INDEX_URL=${PIP_INDEX_URL} python -m uv pip install --system -r pyproject.toml

COPY . .

COPY --from=web-build /build/ui/dist /opt/maxkb-app/ui/dist

RUN if [ -f /opt/maxkb-app/ui/dist/admin/admin.html ]; then cp /opt/maxkb-app/ui/dist/admin/admin.html /opt/maxkb-app/ui/dist/admin/index.html; fi && \
    if [ -f /opt/maxkb-app/ui/dist/chat/chat.html ]; then cp /opt/maxkb-app/ui/dist/chat/chat.html /opt/maxkb-app/ui/dist/chat/index.html; fi && \
    mkdir -p /opt/maxkb /opt/maxkb/logs /opt/maxkb/local /opt/maxkb/python-packages && \
    chmod -R 700 /opt/maxkb

EXPOSE 8080

CMD ["python", "/opt/maxkb-app/apps/manage.py", "start", "web"]
