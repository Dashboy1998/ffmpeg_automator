# hadolint ignore=DL3007
FROM linuxserver/ffmpeg:latest

WORKDIR /
COPY --chown=user:user requirements.txt requirements.txt

# hadolint ignore=DL3008
RUN apt-get update && apt-get install --no-install-recommends -y \
    python-is-python3 \
    pip \
    && apt-get autoremove -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

SHELL ["/bin/bash", "-o", "pipefail", "-c"]
RUN pip install --break-system-packages --no-cache-dir --requirement requirements.txt \
    && rm requirements.txt

RUN mkdir --parents /data/{input_dir,encoded_dir,archive_dir} \
    && chmod 777 -R /data \
    && usermod -u 1000 abc \
    && chown abc:abc -R /data

USER abc
COPY --chown=abc:abc --chmod=755 scripts/ /scripts
WORKDIR /scripts

ENV INPUT_DIR=/data/input_dir \
    ENCODED_DIR=/data/encoded_dir \
    ARCHIVE_DIR=/data/archive_dir \
    VCODEC=libx265 \
    ACODEC=libfdk_aac \
    SCODEC=copy \
    PRESET=fast \
    CRF=22 \
    FIRST_AUDIO_PER_LANG_ONLY="true" \
    AUDIO_LANGUAGES=[ "eng" ] \
    SUBTITLE_LANGUAGES=[ "eng" ]

ENTRYPOINT [ "python", "/scripts/ffmpeg_automator.py" ]
