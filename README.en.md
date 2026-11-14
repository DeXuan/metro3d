# Chinese Metro Systems & Mega Bridges in 3D | 中国城市地铁与超级桥梁 · 三维立体视图

> **[中文说明](README.md)** · A **single-file, zero-dependency, offline-capable** 3D web visualization that projects the rail networks of **53 Chinese cities** into real geographic space, exposing the **vertical dimension** of metro systems — station depth, river crossings, elevated segments — plus 3D models of China's mega bridges.

> [!WARNING]
> **All data is for visualization demos and learning only. Not for engineering, construction, surveying, navigation, or military use.**
> - **Depths are algorithm-generated indicative values**, not measured data
> - **Coordinates are public-map grade** (±50–500 m), not survey grade
> - See [Data Accuracy & Usage Limits](#-data-accuracy--usage-limits)

[![CI](https://github.com/DeXuan/metro3d/actions/workflows/ci.yml/badge.svg)](https://github.com/DeXuan/metro3d/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Cities](https://img.shields.io/badge/cities-53-green)![Lines](https://img.shields.io/badge/lines-374-orange)![Stations](https://img.shields.io/badge/stations-8164-blue)]()
[![Single File](https://img.shields.io/badge/build-single%20HTML-blue)]()

## ✨ Highlights

- **Real coordinates, exaggerated depth** — WGS84 projection at 1 unit = 100 m; vertical exaggeration 30×–400× (adjustable) makes 15 m-deep tunnels legible at 60 km scale
- **53 cities / 374 lines / 8,164 stations** — official line colors, loop lines closed, transfer stations linked
- **Station search** — fuzzy search across all 8,164 stations and 11 bridges, cross-city camera fly-to
- **Live trains** — synthetic headway service gliding along real track curves (above ground, under rivers)
- **Network growth timeline** — drag the year slider (1969→2026) to replay how each city's network grew
- **River crossings marked** — gold pulsing rings at tunnel locations with max-depth labels
- **Rivers & landmarks** — major rivers drawn with scaled labels; 65 landmark buildings in 12 styles
- **11 mega bridges** — HZMB, Shenzhen-Zhongshan, Sutong, Beipanjiang… with water surface, piers, box girders, towers, aviation lights, and valley terrain
- **Depth coloring** — network-wide gradient by station depth
- **Sharing** — deep links (`?city=shanghai&line=sh-9`, `?city=bridges&bridge=0`, `&year=1993`), QR code generated locally, 8K poster mode (`?poster=1`)

## 🚀 Quick Start

```bash
git clone https://github.com/DeXuan/metro3d.git
cd metro3d
python -m http.server 8000
# open http://localhost:8000/  (double-clicking index.html also works — fully offline)
```

Single self-contained file: Three.js r160 + OrbitControls + all data inlined. **No CDN, no build step.**

## 📊 Data Scale

| Metric | Value |
|---|---|
| Cities | **53** (51 mainland + Taipei / Taoyuan / Kaohsiung / Macau / Hong Kong) |
| Lines | **374** (all with opening-year metadata) |
| Stations | **8,164** (2,237 transfer entries, 27.4%) |
| Rivers | 45 cities |
| Landmarks | 65 (29 cities) |
| River-crossing markers | 39 (11 cities) |
| File size | 2.3 MB (≈490 KB gzipped) |

## 🗂 Project Structure

```
metro3d/
├── index.html          # ★ The whole app (engine + data inlined)
├── lib/                # Inlined library sources for upgrades
├── data/
│   ├── metro_all.json  # ★ Full dataset (53 cities)
│   ├── build.py        # Inlines JSON into index.html (--check for CI)
│   └── check_data.py   # Data quality self-check (CI runs this)
├── docs/screenshots/
├── DEPLOY.md / deploy.sh / deploy.bat
└── README.md / README.en.md / CONTRIBUTING.md / CHANGELOG.md
```

## 📡 Data Sources

| Data | Source |
|---|---|
| Station coordinates | [OpenStreetMap](https://www.openstreetmap.org/) (Shanghai) · [AMap metro map](https://map.amap.com/) (other cities) |
| Line order & colors | Same sources (`cl` field = official color) |
| Opening years | Public records, some approximate (±1–2 years) |
| **Station depth** | **Indicative values** — per-station measured depths are rarely published; community PRs with `depthSource` references get a ✓ badge |
| Taiwan / Macau | Manually built (±300–500 m) |

## 🚫 Data Accuracy & Usage Limits

- ❌ Engineering design / construction — depth & tunnel parameters are indicative
- ❌ Surveying / geoinformation production — precision insufficient
- ❌ Navigation / location services — coordinate precision insufficient
- ❌ Military or any use requiring surveying licenses

This project contains no state-secret material: all data comes from public channels (AMap public API, OpenStreetMap, public encyclopedias and news). See the [Chinese README](README.md) for the full disclaimer.

## 🛠 Contributing

Issues and PRs welcome — see [CONTRIBUTING.md](CONTRIBUTING.md). Easiest wins: correct coordinates/station orders, real depth data with sources (`depthSource` field → ✓ badge), new cities in the documented JSON format.

## 📄 License

Code under [MIT License](LICENSE). Third-party components and data attribution in [THIRD-PARTY-NOTICES.md](THIRD-PARTY-NOTICES.md) (Three.js r160 MIT, qrcode-generator MIT, OSM ODbL, AMap).

## 🔗 Links

- Live demo (China): <https://xn--888-vw3e05fxyzc07e.cn:9006/web/metro3d/>
- Live demo (GitHub Pages): <https://dexuan.github.io/metro3d/>
- Sister project: Shanghai metro tunnel profile charts (Chinese)
