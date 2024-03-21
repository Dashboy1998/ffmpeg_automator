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
            ).execute()
        )

    streams = media_info['streams']
    return ['0:v'] + get_audio_maps(streams) + get_subtitle_maps(streams)


def run_ffmpeg(output_path, input_path, map_streams, preset='fast', crf=20):
    # To set bit rate add b='128k'
    # To set stereo audio add ac=2, channel_layout='stereo'
    # ac=2 specifies that the output audio should have 2 channels (stereo).
    # channel_layout='stereo' ensures that the channels are set to stereo.
    ffmpeg = (
        FFmpeg()
        .input(input_path)
        .output(
            output_path,
            vcodec='libx265',
            acodec='aac',
            scodec='copy',
            map=map_streams,
            crf=crf,
            preset=preset,
            )
        )

    ffmpeg.execute()


def create_archive_dir_for_date():
    date = datetime.today().strftime('%Y-%m-%d')
    archive_dir_date = os.path.join(os.environ['archive_dir'], date)

    os.makedirs(archive_dir_date, exist_ok=True)
    return archive_dir_date


def create_directories(root, input_dir, encoded_dir):
    archive_dir_date = create_archive_dir_for_date()
    relpath = os.path.relpath(root, input_dir)
    if relpath != '.':
        save_dir = os.path.join(encoded_dir, relpath)
        os.makedirs(save_dir, exist_ok=True)

    mv_dir = os.path.join(archive_dir_date, relpath)
    os.makedirs(mv_dir, exist_ok=True)

    return relpath, mv_dir


def main():
    input_dir = str(os.environ['input_dir'])
    encoded_dir = str(os.environ['encoded_dir'])
    for root, _, files in os.walk(input_dir):
        relpath, mv_dir = create_directories(root, input_dir, encoded_dir)

        for file_path in files:
            if os.path.splitext(file_path)[-1].lower() == '.mkv':
                video_path = os.path.join(root, file_path)
                sys.stdout.write('{0}\n'.format(video_path))
                output_path = os.path.join(encoded_dir, relpath, file_path)
                map_streams = get_maps(video_path)
                run_ffmpeg(output_path, video_path, map_streams)

                mv_video_path = os.path.join(mv_dir, file_path)
                shutil.move(video_path, mv_video_path)


if __name__ == '__main__':
    main()
