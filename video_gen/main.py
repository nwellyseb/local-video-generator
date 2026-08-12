"""
CLI: python -m video_gen "your prompt here"
"""
import argparse

from . import assemble


def main():
    parser = argparse.ArgumentParser(description="Generate a local stick-figure fact video from a prompt.")
    parser.add_argument("prompt", nargs="+", help="Topic/prompt for the video")
    parser.add_argument("--beats", type=int, default=6, help="Number of script beats (default 6)")
    parser.add_argument("--out", default="output.mp4", help="Output filename")
    args = parser.parse_args()

    prompt = " ".join(args.prompt)
    out_path = assemble.build_video(prompt, out_name=args.out, num_beats=args.beats)
    print(f"\nDone! Video saved to: {out_path}")


if __name__ == "__main__":
    main()
