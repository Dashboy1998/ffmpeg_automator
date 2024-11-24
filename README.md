# FFMPEG Automator

## Required Directory Structure

```sh
data
├── archive
│   └── my_video.mkv
├── encoded
└── input_dir
```

## How does it work

This program will use FFMPEG (FFPROBE) on every MKV to find the audio and subtitles in english or japanese.

then using FFMPEG it will encode the videos to you the settings you defined

## Enviromental Variables

| Variable | Info | Default Values | Allowed Values |
|-|-|-|-|
| INPUT_DIR | Absolute path volume which contains the MKVs | /data/archive_dir | Absolute Path |
| ENCODED_DIR | Absolute path volume and is where encoded MKVs are saved | /data/encoded_dir | Absolute Path |
| ARCHIVE_DIR | Absolute path volume where original MKVs are moved to after being encoded | /data/archive_dir | Absolute Path |
| VCODEC | Video codec | libsvtav1, HDR only works for AV1 | See FFMPEG documentation |
| ACODEC | Audio codec | libfdk_aac | See FFMPEG documentation |
| SCODEC | Subtitle codec | copy | See FFMPEG documentation |
| PRESET | Preset used for compression effciency | 6 | Depends on VCODEC, see FFMPEG documentation |
| CRF | Constant Rate Factor used by encoder | 32 | Depends on VCODEC, see FFMPEG documentation |
| DATE_SUBDIR | Creates subdirectories in for archive and encoded files | false | boolean |
| FIRST_AUDIO_PER_LANG_ONLY | Set to get only the first audio track of a given language | true | boolean |
| AUDIO_LANGUAGES | Array with list of languages to save audio tracks. "all" is used for all languages | [ "eng" ] | Array of strings ex. [ "eng", "jpn" ] |
| SUBTITLE_LANGUAGES | Array with list of langiages to save for subtitles | [ "eng" ] | Array of strings ex. [ "eng", "jpn" ] |
| HIGHEST_CHANNELS | Will only grab the highest audio channel each language or listed language | false | boolean |

## Volume Mounts

### /data/

> [!TIP]
> For better performance do not use separate volumes in docker for [input_dir](#datainput_dir) &
> [archive_dir](#dataarchive_dir) as this will result in a copy then delete instead of a rename.

Please mount your directory containing [input_dir](#datainput_dir) & [archive_dir](#dataarchive_dir)

### /data/input_dir

Directory with MKV to be encoded.

### /data/encoded

Directory where the encoded MKVs will be saved.

### /data/archive_dir/

Directory will original MKVs will be moved after being encoded

## Running program

Start the container and it'll just run
