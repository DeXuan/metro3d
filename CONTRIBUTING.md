# 贡献指南

感谢你对本项目的兴趣！以下是参与贡献的几种方式。

---

## 报告问题

提交 Issue 时请包含：

1. **城市 / 线路 / 站名**（具体到哪一条数据有问题）
2. **现象**（截图 / 描述）
3. **期望结果**
4. 浏览器与设备（如涉及渲染问题）

### 常见的数据问题类型

| 类型 | 示例 | 需要的材料 |
|---|---|---|
| 站点坐标偏差 | 某站标到河里了 | 正确的经纬度（可附官方站点地图） |
| 站序错误 | 线路站点顺序不对 | 官方线路图链接 |
| 缺站/多站 | 某站漏了 | 官方站点列表 |
| 换乘关系缺失 | A 站应可换乘 B 线 | 官方换乘信息 |
| 埋深不准 | 有实测数据 | 施工资料 / 论文 / 新闻报道链接 |
| 制式错误 | 某站是高架但标成地下 | 官方说明 |
| 线路名/颜色错误 | — | 官方线路图 |

---

## 提交代码

### 1. Fork 并克隆

```bash
git clone https://github.com/<your-name>/metro3d.git
cd metro3d
```

### 2. 分支

```bash
git checkout -b fix/beijing-line-order
```

命名建议：`fix/`、`feat/`、`data/`、`docs/`

### 3. 修改

- **只改数据**（最常见）：编辑 `data/metro_all.json`
- **改渲染逻辑**：编辑 `index.html` 中的 `<script type="module">` 应用段
- **改生成脚本**：编辑 `data/*.py`

### 4. 重新内联数据

若修改了 `data/metro_all.json`，必须同步到 `index.html`：

```bash
python - <<'PY'
import io, json
h = io.open('index.html', encoding='utf-8').read()
d = json.load(open('data/metro_all.json', encoding='utf-8'))
blob = json.dumps(d, ensure_ascii=False, separators=(',', ':'))
i0 = h.index('const METRO_DATA = ')
i1 = h.index(';\n', h.index('"cities"', i0))
io.open('index.html','w',encoding='utf-8').write(h[:i0] + 'const METRO_DATA = ' + blob + h[i1:])
print('OK')
PY
```

### 5. 自测

```bash
# 语法检查（提取内联脚本）
python - <<'PY'
import re, io
h = io.open('index.html', encoding='utf-8').read()
s = re.findall(r'<script type="module">(.*?)</script>', h, re.S)[1]
io.open('_check.mjs','w',encoding='utf-8').write(s)
PY
node --check _check.mjs && echo "syntax OK"
rm -f _check.mjs

# 打开验证
python -m http.server 8000
```

浏览器检查项：
- 切换到你的目标城市，无 JS 报错（F12 Console）
- 站点列表、信息卡、换乘标注正常
- 深度着色 / 垂直夸张 / 巡航等交互仍可用

### 6. 提交

```bash
git add -A
git commit -m "fix(data): 修正北京 2 号线站序"
git push origin fix/beijing-line-order
```

提交信息规范（Conventional Commits）：

| 前缀 | 用途 |
|---|---|
| `feat:` | 新功能 |
| `fix:` | 修复 |
| `data:` | 数据修正 |
| `docs:` | 文档 |
| `style:` | 样式/格式（不改逻辑） |
| `perf:` | 性能优化 |
| `refactor:` | 重构 |

### 7. 开 Pull Request

说明：改了什么、为什么、如何验证。附截图更好。

---

## 新增城市的完整流程

### 方法 A：有高德原始数据（推荐）

1. 下载该城市的高德地铁图 JSON：
   ```
   https://map.amap.com/service/subway?_1&srhdata=<城市代码>_drw_<拼音>.json
   ```
   城市代码示例：`1100`=北京、`3100`=上海、`4401`=广州

2. 参考 `data/gen30.py` 的 `CITIES` 与 `ELEV_RULES`，加入你的城市
3. 运行脚本生成片段，合并进 `data/metro_all.json`
4. 参考 `data/refine_depth.py` 做埋深精修
5. 跑 `data/fill_transfers.py` 推导换乘
6. 重新内联到 `index.html`

### 方法 B：手工构建（数据源缺失时）

参考 `data/gen_tw_mo.py`（台北/澳门示例），按线路逐站录入 `{name, lng, lat, type, depth|height}`。

> 注意：手工数据务必在对应城市加 `note` 字段说明"坐标为近似值"。

---

## 数据质量要求

| 项目 | 要求 |
|---|---|
| 坐标 | 小数 6 位；落在城市实际范围内；不得与同城其它站距离 <120m（除非真实共站） |
| 站序 | 与官方线路图一致；首末站为终点 |
| 同名站 | 同城同名站应互为换乘；跨线同名但距离 >1.2km 视为不同站，需重命名区分 |
| 深度 | 地下站 6–40m；高架高度 5–25m；不得为负 |
| 环线 | 首末站相同或相距 <300m 时设 `"loop": true` |
| 换乘 | 短名格式（`"2"` 而非 `"2号线"`），不含自身线路 |
| 埋深引用 | 有实测数据的站加 `"depthSource"`（资料 URL 或简述）——信息卡显示 ✓ 徽章 |
| 线路名 | 同城不可重名；避免括号（用 `·` 或直接省略） |

自检脚本（提交前跑一遍，CI 也会跑）：

```bash
python data/build.py --check   # 内联数据一致性 + JS 语法
python data/check_data.py      # 数据质量（站名/坐标/深度/年份）
```

---

## 代码风格

- `index.html` 内的 JS：ES2022、无构建步骤、不引入 npm 依赖
- 渲染逻辑保持**数据驱动**（新增城市不改渲染代码）
- 注释用中文（与现有代码一致）
- 不要提交 `poster/8k/`、`*.mp4`、临时脚本等大文件

---

## 行为准则

- 尊重所有贡献者
- 数据修正请附**可验证的依据**（官方链接优先）
- 不接受把有轨电车/云巴等路面制式标为"地铁"的改动（项目定位为地铁/磁浮/市域）
- 涉及台湾、香港、澳门的数据，请使用"中国台湾/香港/澳门"表述