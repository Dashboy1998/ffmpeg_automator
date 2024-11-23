#!/bin/python

import json
import os
import shutil
import sys
from datetime import datetime

from ffmpeg import FFmpeg, FFmpegError, Progress


def get_audio_maps(streams):  # noqa: WPS231
    audio_map = []
    audio_map_backup = []
    audio_languages = json.loads(os.environ['AUDIO_LANGUAGES'])

    get_first_audio_per_lang_only = os.environ['FIRST_AUDIO_PER_LANG_ONLY'].lower() == 'true'
    lang_found = []
    index = -1

    for stream in streams:
        if stream['codec_type'] == 'audio':
            index = index + 1
            audio_map_backup.append('0:a:{0}'.format(str(index)))  # Used if no matching languages are found
            language = stream.get('tags', {}).get('language')
            language_lower = language.lower()
            if language_lower in audio_languages:
                if not get_first_audio_per_lang_only or (get_first_audio_per_lang_only and language_lower not in lang_found):  # noqa: E501, WPS337, WPS408
                    audio_map.append('0:a:{0}'.format(str(index)))
                    lang_found.append(language)

    if not audio_map:
        sys.stdout.write('No audio tracks found for given languages: {0}\n'.format(str(audio_languages)))
        sys.stdout.write('Ignoring audio track languages\n')
        audio_map = audio_map_backup

    return audio_map


def get_subtitle_maps(streams):
    subtitle_map = []
    subtitle_languages = json.loads(os.environ['SUBTITLE_LANGUAGES'])

    index = -1
    for stream in streams:
        if stream['codec_type'] == 'subtitle':
            index = index + 1
            if stream['tags'].get('language', '').lower() in subtitle_languages:
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

    map_list = ['0:v']
    streams = media_info['streams']

    audio_maps = get_audio_maps(streams)
    if audio_maps:
        map_list += audio_maps

    subtitle_map = get_subtitle_maps(streams)
    if subtitle_map:
        map_list += subtitle_map

    return map_list


def check_hdr(file_path):
    media_info = json.loads(
        FFmpeg(executable='ffprobe').input(
            file_path,
            print_format='json',
            show_streams=None,
            ).execute(),
        )

    hdr = False

    # Assume there is only one video stream
    for stream in media_info['streams']:
        if stream['codec_type'] == 'video':
            if 'color_space' in stream:
                hdr = stream.get('color_space') == 'bt2020nc'
            break

    return hdr


def get_hdr_setings(file_path):
    media_info = json.loads(
        FFmpeg(executable='ffprobe').input(
            file_path,
            print_format='json',
            select_streams='v',
            read_intervals='%+#1',
            show_frames=None,
            show_entries='frame=color_space,color_primaries,color_transfer,side_data_list,pix_fmt',
            ).execute(),
        )

    hdr_settings = {}

    for frame in media_info['frames']:
        hdr_settings['color_space'] = frame['color_space']
        hdr_settings['color_primaries'] = frame['color_primaries']
        hdr_settings['color_transfer'] = frame['color_transfer']
        hdr_settings['pix_fmt'] = frame['pix_fmt']
        for side_data in frame['side_data_list']:
            if side_data['side_data_type'] == 'Mastering display metadata':
                hdr_settings['red_x'] = side_data['red_x']
                hdr_settings['red_y'] = side_data['red_y']
                hdr_settings['green_x'] = side_data['green_x']
                hdr_settings['green_y'] = side_data['green_y']
                hdr_settings['blue_x'] = side_data['blue_x']
                hdr_settings['blue_y'] = side_data['blue_y']
                hdr_settings['white_point_x'] = side_data['white_point_x']
                hdr_settings['white_point_y'] = side_data['white_point_y']
                hdr_settings['min_luminance'] = side_data['min_luminance']
                hdr_settings['max_luminance'] = side_data['max_luminance']
            if side_data['side_data_type'] == 'Content light level metadata':
                hdr_settings['max_content'] = side_data['max_content']
                hdr_settings['max_average'] = side_data['max_average']

    return hdr_settings


def run_ffmpeg(input_path, output_path):
    map_streams = get_maps(input_path)
    encode_settings = {
        'vcodec': os.environ['VCODEC'],
        'acodec': os.environ['ACODEC'],
        'scodec': os.environ['SCODEC'],
        'map': map_streams,
        'crf': os.environ['CRF'],
        'preset': os.environ['PRESET'],
    }

    if check_hdr(input_path):
        hdr_settings = get_hdr_setings(input_path)
        encode_settings['libsvtav1-params'] = 'hdr-opt=1:repeat-headers=1:colorprim={color_primaries}:transfer={color_transfer}:colormatrix={color_space}:master-display=R({red_x},{red_y})G({green_x},{green_y})B({blue_x},{blue_y})WP({white_point_x},{white_point_y})L({max_luminance},{min_luminance}):max-cll={max_content},{max_average} -pix_fmt {pix_fmt}'.format(**hdr_settings)  # noqa: E501

    ffmpeg = (
        FFmpeg().input(input_path).output(
            output_path,
            encode_settings,
            )
        )

    @ffmpeg.on('progress')
    def on_progress(progress: Progress):  # noqa: WPS430
        sys.stdout.write('{0}\r'.format(str(progress)))

    try:
        ffmpeg.execute()
    except FFmpegError as exception:
        sys.stdout.write('An exception has been occurred!')
        sys.stdout.write('- Message from ffmpeg: {0}\n'.format(str(exception.message)))
        sys.stdout.write('- Arguments to execute ffmpeg: {0}\n'.format(str(exception.arguments)))
        return False

    sys.stdout.write('\n')
    return True


def create_directories(root):
    date = datetime.today().strftime('%Y-%m-%d')
    relpath = os.path.relpath(root, os.environ['INPUT_DIR'])

    mv_dir = os.path.join(os.environ['ARCHIVE_DIR'], date, relpath)
    os.makedirs(mv_dir, exist_ok=True)

    encoded_dir = os.path.join(os.environ['ENCODED_DIR'], date, relpath)
    os.makedirs(encoded_dir, exist_ok=True)

    return mv_dir, encoded_dir


def main():  # noqa: WPS231
    for root, _, files in sorted(os.walk(os.environ['INPUT_DIR'])):
        mv_dir, encoded_dir = create_directories(root)

        for file_path in sorted(files):
            extension = os.path.splitext(file_path)[-1]
            if extension.lower() in {'.mkv', '.mp4', '.avi', '.m4v', '.ts', '.f4v', '.webm'}:
                video_path = os.path.join(root, file_path)
                sys.stdout.write('{0}\n'.format(video_path))
                output_path = os.path.join(encoded_dir, file_path.replace(extension, '.mkv'))

                # Check if output file exists
                if os.path.isfile(output_path):
                    sys.stdout.write('File already exists in destination, unable to encode video: {0}\n'.format(video_path))  # noqa: E501
                else:
                    encode_success = run_ffmpeg(video_path, output_path)

                    if encode_success:
                        mv_video_path = os.path.join(mv_dir, file_path)  # noqa: WPS220
                        shutil.move(video_path, mv_video_path)  # noqa: WPS220
                    else:
                        sys.stdout.write('Unable to encode video: {0}\n'.format(video_path))  # noqa: WPS220


if __name__ == '__main__':
    main()
