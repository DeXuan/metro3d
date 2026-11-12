# 原始数据（Raw Data）

本目录保存从**高德地图地铁图接口**抓取的原始 JSON，用于重现 `data/metro_all.json` 的生成过程。

## 接口格式

```
https://map.amap.com/service/subway?_1&srhdata=<城市代码>_drw_<拼音>.json
```

示例：`3100_drw_shanghai.json`（上海）、`1100_drw_beijing.json`（北京）

## 字段说明

| 字段 | 含义 |
|---|---|
| `s` | 城市名 |
| `l` | 线路数组 |
| `l[].ln` | 线路名 |
| `l[].cl` | 线路颜色（十六进制） |
| `l[].lo` | 是否环线（`"1"` 为环线） |
| `l[].st` | 站点数组 |
| `l[].st[].n` | 站名 |
| `l[].st[].sl` | **经纬度**，格式 `"lng,lat"`（WGS84） |
| `l[].st[].poiid` | POI ID（同站跨线一致，用于推导换乘） |

## 使用方式

参考 `data/gen_cities.py` 与 `data/gen30.py`：

```bash
# 1. 将城市 JSON 放到本目录
# 2. 在 gen30.py 的 CITIES 列表加入该城
# 3. 运行
python -I data/gen30.py
```

## 版权

数据版权归高德地图所有，本项目仅用于技术研究与演示，不作商业用途。
如用于生产环境，请使用官方开放平台 API 或自行采集。
