# Ramcharitmanas + Mahabharat — MP3 Collection

Offline MP3 katha collection (downloaded from YouTube) organised folder-wise, ready to copy onto a pendrive.

> The audio files live in `mp3/` which is gitignored (too large for GitHub). This README documents what each file is and where it came from.

## Folder layout

```
mp3/
├── 01_Rambhadracharya_Kanpur_2019/            Shri Ramcharitmanas Katha — Kanpur 2019 (7 kathas + 4 extra clips)
├── 02_Rambhadracharya_Bageshwar_Dham/         Shri Ram Katha Day 1 — Vishesh Prasaran, Bageshwar Dham
├── 03_Raghvacharya_Ramcharitmanas_Path_Ayodhya/  Ramcharitmanas Paath — Shri Ramvarnashram, Ayodhya
├── 04_Rajan_Ji_Ramcharitmanas_Vyakhya/        Ramcharitmanas ki Sundar Vyakhya — Pujya Rajan Ji
└── 05_GovindDevGiri_Mahabharat_Katha_Pandharpur/  Shri Mahabharat Katha — Pandharpur (Days 1–7, Swami Govind Dev Giri ji)
```

## Sources

| Folder | Source | Link |
|---|---|---|
| 01 | Playlist: Shri Ramcharitmanas Katha — Kanpur 2019 (Jagadguru Rambhadracharaya ji, Satsang channel) | https://www.youtube.com/playlist?list=PLOZ4QPdIQPK014Q22A-MawqVI9pAuM70U |
| 02 | Shri Ram Katha Day-1 (Bageshwar Dham, jagadguru ramanandacharya ji) | https://www.youtube.com/watch?v=B6v_sBT3eTs |
| 03 | D-LIVE 04 — Shri Ramcharitmanas Paath (Swami Raghvacharya) | https://www.youtube.com/watch?v=xtZv9eDA6TE |
| 04 | Shri Ramcharitmanas ki Sundar Vyakhya (Pujya Rajan Ji Official) | https://www.youtube.com/watch?v=7RUK-P9pRd0 |
| 05 | Shri Mahabharat Katha — Pandharpur, Days 1–7 (Swami Govind Dev Giri ji, Satsang channel) | https://www.youtube.com/watch?v=6HpIAOHPxm4 (Day 1) — full series via watch_videos: `6HpIAOHPxm4,ex_52kbePEI,_zgNaywsvuk,UpUicoXBky0,o2WwKyul3_M,GpAXRTgDHCg,M4_KJTIUxyw` |

## Format

- MP3, 128 kbps, with embedded title/artist metadata and thumbnail artwork
- All 11 playlist videos included: full kathas (Days 1–7) plus 4 short extra clips
- Filenames are ASCII-safe and zero-padded so they sort correctly on any MP3 player

## How to copy to a pendrive

1. Plug in the pendrive.
2. Copy the `mp3` folder (or just the sub-folders you want) onto it.
3. Done — any car stereo / MP3 player / phone will play them.

## Re-downloading (if ever needed)

Requires [yt-dlp](https://github.com/yt-dlp/yt-dlp) and ffmpeg:

```bash
yt-dlp -f "ba/b" -x --audio-format mp3 --audio-quality 128K   --embed-metadata --embed-thumbnail   -o "mp3/01_Rambhadracharya_Kanpur_2019/Kanpur 2019 Katha - Day %(playlist_index)02d.%(ext)s"   --playlist-items 1-7 "https://www.youtube.com/playlist?list=PLOZ4QPdIQPK014Q22A-MawqVI9pAuM70U"
```

*Downloaded for personal/family listening.*
