#!/usr/bin/env python3

import argparse
import os
import subprocess
import sys
from pathlib import Path

def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Change audio speed using ffmpeg",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "input",
        type=str,
        help="Input audio file"
    )
    parser.add_argument(
        "-s", "--speed",
        type=float,
        default=1.0,
        help="Speed (e.g. 1.2 = 20%% faster, 0.8 = 20%% slower)"
    )
    parser.add_argument(
        "-r", "--reciprocal",
        action="store_true",
        default=False,
        help="Reciprocal (e.g. 1.2 becomes 1/1.2 as the multiplier)"
    )

    return parser.parse_args()

def get_sample_rate(input_path):
    try:
        ffprobe_cmd = [
            "ffprobe",
            "-v", "error",
            "-show_entries", "stream=sample_rate",
            "-of", "default=noprint_wrappers=1:nokey=1",
            str(input_path)
        ]

        result = subprocess.run(
            ffprobe_cmd,
            capture_output=True,
            text=True,
            check=True
        )

        sample_rate = result.stdout.strip()

        if sample_rate:
            return int(sample_rate)
        else:
            return None

    except subprocess.CalledProcessError as e:
        print("ffprobe failed:", e.stderr.strip())
        return None

    except FileNotFoundError:
        print("Error: ffprobe not found. Is ffmpeg installed?")
        return None

def main():
    args = parse_arguments()

    input_path = Path(args.input)
    if not input_path.is_file():
        print(f"Error: File not found: {input_path}", file=sys.stderr)
        return 1

    speed = args.speed
    if speed <= 0:
        print("Error: Speed factor must be > 0", file=sys.stderr)
        return 1

    reciprocal = args.reciprocal
    if reciprocal:
        speed = 1 / speed

    sample_rate = get_sample_rate(input_path)
    stem = input_path.stem
    suffix = f" [{speed}x]"
    speed_str = f"{1 / speed}" if reciprocal else f"{speed}"
    output_path = Path.cwd() / (stem + suffix + ".flac")

    ffmpeg_cmd = [
        "ffmpeg",
        "-i", str(input_path),
        "-af", f"asetrate={speed}*{sample_rate}",
        str(output_path)
    ]

    try:
        subprocess.run(ffmpeg_cmd, check=True)
        return 0

    except subprocess.CalledProcessError as e:
        print(f"\nffmpeg failed with exit code {e.returncode}", file=sys.stderr)
        return 1

    except FileNotFoundError:
        print(f"Error: '{args.ffmpeg}' not found. Is ffmpeg installed?", file=sys.stderr)
        return 127

if __name__ == "__main__":
    sys.exit(main())
