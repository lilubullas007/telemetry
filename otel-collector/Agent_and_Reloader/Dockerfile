# Config-reloader image

# bitnami/kubectl image
FROM bitnami/kubectl:latest

# User root (temporally)
USER root

# Install curl
RUN mkdir -p /var/lib/apt/lists/partial && \
    apt-get update && \
    apt-get install -y curl && \
    rm -rf /var/lib/apt/lists/*

# Back to original user
USER 1001