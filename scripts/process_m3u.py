import os
import re
from pathlib import Path

ROOT = "./source"
OUT_DIR = "output"

OTT_FILE = f"{OUT_DIR}/ott_mobaibox.m3u"
IPV4_FILE = f"{OUT_DIR}/ipv4_channels.m3u"
IPV6_FILE = f"{OUT_DIR}/ipv6_channels.m3u"

os.makedirs(OUT_DIR, exist_ok=True)

ipv4_pattern = re.compile(
    r'http[s]?://(?:\d{1,3}\.){3}\d{1,3}'
)

ipv6_pattern = re.compile(
    r'http[s]?://\[[0-9a-fA-F:]+\]'
)

def find_m3u_files():
    files = []
    for path in Path(ROOT).rglob("*"):
        if path.suffix.lower() in [".m3u", ".m3u8"]:
            files.append(path)
    return files


def parse_m3u(file_path):
    """
    返回 [(extinf, url)]
    """
    results = []
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()

    extinf = None
    for line in lines:
        line = line.strip()

        if line.startswith("#EXTINF"):
            extinf = line
        elif line.startswith("http"):
            if extinf:
                results.append((extinf, line))
                extinf = None

    return results


def dedup_write(channels, output_file):
    seen = set()

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")

        for extinf, url in channels:
            key = (extinf, url)
            if key not in seen:
                seen.add(key)
                f.write(extinf + "\n")
                f.write(url + "\n")


def main():

    ott_channels = []
    ipv4_channels = []
    ipv6_channels = []

    files = find_m3u_files()

    print(f"Found {len(files)} m3u files")

    for file in files:
        print("Parsing:", file)
        channels = parse_m3u(file)

        for extinf, url in channels:

            if "ott.mobaibox.com" in url:
                ott_channels.append((extinf, url))

            if ipv4_pattern.search(url):
                ipv4_channels.append((extinf, url))

            if ipv6_pattern.search(url):
                ipv6_channels.append((extinf, url))

    dedup_write(ott_channels, OTT_FILE)
    dedup_write(ipv4_channels, IPV4_FILE)
    dedup_write(ipv6_channels, IPV6_FILE)

    print("Done.")
    print("OTT:", len(ott_channels))
    print("IPv4:", len(ipv4_channels))
    print("IPv6:", len(ipv6_channels))


if __name__ == "__main__":
    main()
