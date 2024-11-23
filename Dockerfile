FROM linuxserver/ffmpeg:amd64-version-7.1-cli

WORKDIR /
COPY --chown=user:user requirements.txt requirements.txt

RUN apt-get update && apt-get install --no-install-recommends -y \
    python-is-python3=3.11.4-1 \
    python3-pip=24.0+dfsg-1ubuntu1.1 \
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
    VCODEC=libsvtav1 \
    ACODEC=libfdk_aac \
    SCODEC=copy \
    PRESET=6 \
    CRF=32 \
    FIRST_AUDIO_PER_LANG_ONLY="true" \
    AUDIO_LANGUAGES='[ "eng" ]' \
    SUBTITLE_LANGUAGES='[ "eng" ]' \
    PYTHONUNBUFFERED=1

ENTRYPOINT [ "python", "/scripts/ffmpeg_automator.py" ]
