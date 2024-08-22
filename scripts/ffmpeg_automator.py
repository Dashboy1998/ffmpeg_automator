#!/bin/python

import json
import os
import shutil
import sys
from datetime import datetime

from ffmpeg import FFmpeg


def get_audio_maps(streams):
    audio_map = []
    audio_languages = ['eng', 'jpn']

    index = -1
    for stream in streams:
        if stream['codec_type'] == 'audio':
            index = index + 1
            if stream['tags']['language'] in audio_languages:
                audio_map.append('0:a:{0}'.format(str(index)))

    return audio_map


def get_subtitle_maps(streams):
    subtitle_map = []
    subtitle_languages = ['eng']
    index = -1
    for stream in streams:
        if stream['codec_type'] == 'subtitle':
            index = index + 1
            if stream['tags']['language'] in subtitle_languages:
                subtitle_map.append('0:s:{0}'.format(str(index)))

    return subtitle_map


def get_maps(file_path):
    media_info = json.loads(
        FFmpeg(executable='ffprobe').input(
            file_path,
            print_format='json',
            show_streams=None,
            ).execute(),
        )

    streams = media_info['streams']
    return ['0:v'] + get_audio_maps(streams) + get_subtitle_maps(streams)


def run_ffmpeg(input_path, output_path):
    # To set bit rate add b='128k'
    # To set stereo audio add ac=2, channel_layout='stereo'
    # ac=2 specifies that the output audio should have 2 channels (stereo).
    # channel_layout='stereo' ensures that the channels are set to stereo.
    map_streams = get_maps(input_path)
    ffmpeg = (
        FFmpeg().input(input_path).output(
            output_path,
            vcodec=os.environ['VCODEC'],
            acodec=os.environ['ACODEC'],
            scodec=os.environ['SCODEC'],
            map=map_streams,
            crf=os.environ['CRF'],
            preset=os.environ['PRESET'],
            )
        )

    ffmpeg.execute()


def create_directories(root):
    date = datetime.today().strftime('%Y-%m-%d')
    relpath = os.path.relpath(root, os.environ['INPUT_DIR'])

    mv_dir = os.path.join(os.environ['ARCHIVE_DIR'], date, relpath)
    os.makedirs(mv_dir, exist_ok=True)

    encoded_dir = os.path.join(os.environ['ENCODED_DIR'], date, relpath)
    os.makedirs(encoded_dir, exist_ok=True)

    return mv_dir, encoded_dir


def main():
    for root, _, files in os.walk(os.environ['INPUT_DIR']):
        mv_dir, encoded_dir = create_directories(root)

        for file_path in files:
            if os.path.splitext(file_path)[-1].lower() == '.mkv':
                video_path = os.path.join(root, file_path)
                sys.stdout.write('{0}\n'.format(video_path))
                output_path = os.path.join(encoded_dir, file_path)
                run_ffmpeg(video_path, output_path)

                mv_video_path = os.path.join(mv_dir, file_path)
                shutil.move(video_path, mv_video_path)


if __name__ == '__main__':
    main()
