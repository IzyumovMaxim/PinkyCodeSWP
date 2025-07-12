FROM harbor.pg.innopolis.university/docker-hub-cache/debian:11-slim

RUN apt update && apt install --no-install-recommends -y nginx && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

CMD ["nginx", "-g", "daemon off;"]
