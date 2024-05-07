FROM node:18.20.2-bullseye-slim AS app
WORKDIR /app
COPY sea_app/package.json package.json
COPY sea_app/yarn.lock yarn.lock
RUN yarn install --frozen-lockfile
COPY sea_app/ .
RUN yarn run build


FROM python:3.11-slim-bullseye
EXPOSE 80

# Fixes a bug that prevents SSL connections to the DB from being established;
# see https://github.com/nginx/unit/issues/834#issuecomment-1410297997>
ENV PGSSLCERT /tmp/postgresql.crt

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        curl htop tmux \
        build-essential \
        libproj-dev gdal-bin \
        poppler-utils \
        tesseract-ocr \
        gettext-base \
        nginx \
        redis-server \
        supervisor

# Set up NGINX
RUN ln -sf /dev/stdout /var/log/nginx/access.log \
	&& ln -sf /dev/stderr /var/log/nginx/error.log

# Install Python dependencies
COPY requirements.txt /
RUN pip install -r requirements.txt

# Copying Vue app
COPY --from=app /app/dist/ /public/

# Copy runtime config files
COPY nginx.conf /etc/nginx/nginx.conf
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Copy remaining files
COPY docker_start.sh /
COPY sea.sh /
COPY sea /sea
COPY sea_server /sea_server

# Set up Django application and boot Gunicorn
CMD /bin/bash docker_start.sh
