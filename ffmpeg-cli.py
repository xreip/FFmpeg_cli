"""
1. List all .mp4 files in current dir v
2. Select the file v
3. Select the output resolution v
4. Select Codec v
5. Select CPU or GPU v
5.1 Select Quality v
5.2 Name of the file v
    5.2.1 Include date yes/no v
6. Process. v 
7. Again or quit. v
ffmpeg -h encoder=hevc_nvenc -hide_banner
"""
import subprocess
from datetime import date
from enum import Enum
from pathlib import Path

import inquirer
from rich import pretty, print


def list_all_mp4_or_mkv_files_in_current_dir() -> list:
    path = Path.cwd()
    videos: list = [video for video in path.glob(str("*.mp4" or "*.mkv"))]
    return videos


def video_selector(videos: list) -> str:
    if not videos:
        videos = ["There's no video .mp4 or .mkv in this directory"]
    question = [
        inquirer.List(
            "video", message="Select the video you want to process", choices=videos
        )
    ]

    answer = inquirer.prompt(question)
    # print(answer)
    return answer["video"]


def select_output_resolution():
    choices = [
        "3840x2160",
        "2560x1440",
        "default",
        "1920x1080",
        "1280x720",
        "854x480",
        "640x360",
    ]
    question = [
        inquirer.List(
            "resolution",
            message="Select if you want to use CPU or GPU",
            choices=choices,
            default="1920x1080",
        )
    ]

    answer = inquirer.prompt(question)
    # print(answer)
    return answer["resolution"]


def select_cpu_or_gpu():
    choices = ["CPU", "Nvidia GPU"]
    question = [
        inquirer.List(
            "device", message="Select if you want to use CPU or GPU", choices=choices
        )
    ]

    answer = inquirer.prompt(question)
    # print(answer)
    return answer["device"]


def select_video_codec():
    choices = ["H264", "H265"]
    question = [
        inquirer.List(
            "codec", message="Select the video codec you want", choices=choices
        )
    ]

    answer = inquirer.prompt(question)
    # print(answer)
    return answer["codec"]


def select_quality():
    class Quality(Enum):
        VERY_LOW = "Very Low"
        LOW = "Low"
        MEDIUM = "Medium"
        HIGH = "High"
        VERY_HIGH = "Very High"

    question = [
        inquirer.List(
            "quality",
            message="Select the video quality you want",
            choices=[e.value for e in Quality],
            default="High",
        )
    ]

    answer = inquirer.prompt(question)
    # print(answer)
    return answer["quality"]


def define_file_name():
    question = [inquirer.Text("filename", message="Choose the filename?")]
    answer = inquirer.prompt(question)
    # print(answer)
    return answer["filename"]


def select_include_date():
    question = [
        inquirer.Confirm(
            "date",
            message="Do you want to include today's date in the filename ?",
            default=True,
        ),
    ]
    answer = inquirer.prompt(question)
    # print(answer)
    return answer["date"]


def ask_continue():
    question = [
        inquirer.Confirm(
            "continue",
            message="Do you want to process another file ?",
            default=False,
        ),
    ]
    answer = inquirer.prompt(question)
    # print(answer)
    return answer["continue"]


def define_ffmpeg_string(
    video, resolution, codec, device, quality, filename_out, include_date: bool
):
    class device_type(Enum):
        NVIDIAGPU = "Nvidia GPU"
        CPU = "CPU"

    class Quality(Enum):
        VERY_LOW = "Very Low"
        LOW = "Low"
        MEDIUM = "Medium"
        HIGH = "High"
        VERY_HIGH = "Very High"

    class CRF_Quality(Enum):
        VERY_LOW = 35
        LOW = 29
        MEDIUM = 23
        HIGH = 19
        VERY_HIGH = 16

    class x26x_Quality(Enum):
        VERY_LOW = "faster"
        LOW = "fast"
        MEDIUM = "medium"
        HIGH = "slow"
        VERY_HIGH = "slower"

    class gpu_Quality(Enum):
        VERY_LOW = "p2"
        LOW = "fast"
        MEDIUM = "medium"
        HIGH = "slow"
        VERY_HIGH = "p7"

    class nvidia_gpu_codec(Enum):
        H264 = "h264_nvenc"
        H265 = "hevc_nvenc"

    class cpu_codec(Enum):
        H264 = "libx264"
        H265 = "libx265"

    quality_map = {
        device_type.CPU.value: {
            Quality.VERY_LOW.value: (
                CRF_Quality.VERY_LOW.value,
                x26x_Quality.VERY_LOW.value,
            ),
            Quality.LOW.value: (CRF_Quality.LOW.value, x26x_Quality.LOW.value),
            Quality.MEDIUM.value: (CRF_Quality.MEDIUM.value, x26x_Quality.MEDIUM.value),
            Quality.HIGH.value: (CRF_Quality.HIGH.value, x26x_Quality.HIGH.value),
            Quality.VERY_HIGH.value: (
                CRF_Quality.VERY_HIGH.value,
                x26x_Quality.VERY_HIGH.value,
            ),
        },
        device_type.NVIDIAGPU.value: {
            Quality.VERY_LOW.value: gpu_Quality.VERY_LOW.value,
            Quality.LOW.value: gpu_Quality.LOW.value,
            Quality.MEDIUM.value: gpu_Quality.MEDIUM.value,
            Quality.HIGH.value: gpu_Quality.HIGH.value,
            Quality.VERY_HIGH.value: gpu_Quality.VERY_HIGH.value,
        },
    }

    codec_device_map = {
        "H264": {
            device_type.CPU.value: cpu_codec.H264.value,
            device_type.NVIDIAGPU.value: nvidia_gpu_codec.H264.value,
        },
        "H265": {
            device_type.CPU.value: cpu_codec.H265.value,
            device_type.NVIDIAGPU.value: nvidia_gpu_codec.H265.value,
        },
    }

    if include_date:
        todays_date = date.today()
        filename_out = f"{filename_out}-{todays_date}"

    command_start = f"ffmpeg -i {video}"

    encode_codec = codec_device_map[codec][device]

    resolution_str = f" -s {resolution}" if resolution != "default" else ""

    if device == device_type.CPU.value:
        crf, preset = quality_map[device][quality]
        final_string = f"{command_start} -c:v {encode_codec} -crf {crf} -preset {preset} {resolution_str} {filename_out}.mp4"
    if device == device_type.NVIDIAGPU.value:
        preset = quality_map[device][quality]
        final_string = f"{command_start} -c:v {encode_codec} -preset {preset} {resolution_str} {filename_out}.mp4"
    return final_string


def main():
    pretty.install()
    run = True
    while run:
        videos = list_all_mp4_or_mkv_files_in_current_dir()
        # Video
        video = video_selector(videos)
        # Parameters
        resolution = select_output_resolution()
        codec = select_video_codec()
        device = select_cpu_or_gpu()
        quality = select_quality()
        filename = define_file_name()
        include_date = select_include_date()
        ffmpeg_string = define_ffmpeg_string(
            video, resolution, codec, device, quality, filename, include_date
        )
        # Run
        subprocess.run(ffmpeg_string)

        run = ask_continue()

    print("[bold magenta]Bye Bye[/bold magenta]")


if __name__ == "__main__":
    main()
