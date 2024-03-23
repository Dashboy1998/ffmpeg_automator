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
| INPUT_DIR | Absolute path volume which contains the MKVs | /data/encode_me | Absolute Path |
| ENCODED_DIR | Absolute path volume and is where encoded MKVs are saved | /data/encoded | Absolute Path |
| ARCHIVE_DIR | Absolute path volume where original MKVs are moved to after being encoded | /data/Archive | Absolute Path |
| VCODEC | Video codec | libx265 | See FFMPEG documentation |
| ACODEC | Audio codec | aac | See FFMPEG documentation |
| SCODEC | Subtitle codec | copy | See FFMPEG documentation |
| PRESET | Preset used for compression effciency | fast | Depends on VCODEC, see FFMPEG documentation |
| CRF | Constant Rate Factor used by encoder | 20 | Depends on VCODEC, see FFMPEG documentation |

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
