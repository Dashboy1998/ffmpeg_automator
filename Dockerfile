# hadolint ignore=DL3007
FROM python:3-slim-bookworm

WORKDIR /
COPY --chown=user:user requirements.txt requirements.txt

RUN apt-get update && apt-get install --no-install-recommends -y \
    ffmpeg=7:5.1.4-0+deb12u1 \
    && apt-get autoremove -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

SHELL ["/bin/bash", "-o", "pipefail", "-c"]
RUN pip install --no-cache-dir --requirement requirements.txt \
    && rm requirements.txt

RUN groupadd user --gid 1000 \
    && useradd user --uid 1000 --gid 1000 \
    && mkdir --parents /data/{input_dir,encoded_dir,archive_dir} \
    && chmod 777 -R /data \
    && chown user:user -R /data

USER user
COPY --chown=user:user --chmod=755 scripts/ /scripts
WORKDIR /scripts

ENV INPUT_DIR=/data/input_dir \
    ENCODED_DIR=/data/encoded_dir \
    ARCHIVE_DIR=/data/archive_dir \
    VCODEC=libx265 \
    ACODEC=aac \
    SCODEC=copy \
    PRESET=fast \
    CRF=20

ENTRYPOINT [ "tail", "-f", "/dev/null" ]
