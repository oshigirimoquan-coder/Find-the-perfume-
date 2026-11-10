# Find the Perfume

給香水新手的選香網站：7 題測驗找出香調、用感覺找香水、一萬支香水庫（中英文與同音字搜尋）、調香師介紹、台灣通路與參考價。

純靜態網站，沒有後端，放在 GitHub Pages 就能用。

## 檔案

| 檔案 | 用途 |
|---|---|
| `index.html` | 網站本體（版面、測驗、精選 200 支、搜尋邏輯） |
| `perfumes.json` | 完整香水庫（約 9,800 支，由 `tools/build.py` 產生） |
| `py.json` | 中文字轉拼音表，用來做同音錯字搜尋 |
| `additions.csv` | **自己新增或修正香水用的表格** |
| `tools/` | 重新產生 `perfumes.json` 的腳本與中文對照表 |

## 上架到 GitHub Pages

1. 在 GitHub 建一個新的 repository（例如 `perfume-guide`），設為 Public。
2. 把這個資料夾裡的所有檔案上傳（網頁上按 **Add file → Upload files**，整批拖進去，Commit）。
3. 到 **Settings → Pages**，Source 選 **Deploy from a branch**，Branch 選 `main`、資料夾 `/ (root)`，Save。
4. 等一兩分鐘，網址會是 `https://<你的帳號>.github.io/perfume-guide/`。

> 直接雙擊打開 `index.html` 只會看到精選 200 支，因為瀏覽器不允許本機檔案讀取 JSON。要在自己電腦預覽，請在資料夾裡執行 `python3 -m http.server`，再開 `http://localhost:8000`。

## 新增香水（最常用）

在 GitHub 網頁上打開 `additions.csv` → 按鉛筆圖示編輯 → 每支香水加一行 → Commit。Pages 會自動更新，重新整理網站就看得到。

同名同品牌的香水會**覆蓋**原本的資料，所以也可以用這個檔修正錯誤（例如補價格、標停產）。

範例（第一行是欄位名稱，已經在檔案裡）：

```csv
name,brand,brand_zh,nickname,perfumer,families,notes,moods,seasons,sillage,gender,year,region,tier,availability,price_ml,price_ntd,discontinued,popularity
V00 裘野,OCO,,裘野,未公開,wod2 grn1,木質、綠意,rain study,aw,2,中性,2024,港台,i,n,50,3600,0,800
Santal 33,Le Labo,勒拉博,檀香33,Frank Voelkl,wod3 lea2 aro1,檀香、雪松、皮革、紫羅蘭,study fire,aw,3,中性,2011,歐美,n,c,50,7250,0,30000
```

欄位說明：

| 欄位 | 必填 | 寫法 |
|---|---|---|
| `name` | ✔ | 香水名 |
| `brand` | ✔ | 品牌名（要覆蓋原資料時，需和網站上顯示的一樣） |
| `brand_zh` |  | 品牌中文名 |
| `nickname` |  | 中文名、暱稱、縮寫，空格分隔，搜尋用 |
| `perfumer` |  | 調香師 |
| `families` |  | 香調代碼＋強度 1–3，空格分隔，例如 `wod3 lea2`。代碼：`cit`柑橘 `grn`綠意 `aqu`水生 `flo`花香 `wht`白花 `fru`果香 `gou`美食 `wod`木質 `amb`琥珀東方 `smk`煙燻焚香 `lea`皮革 `msk`麝香肤感 `aro`芳香草本 `pow`粉感 |
| `notes` |  | 香材描述（中文） |
| `moods` |  | 感覺，空格分隔：`soap` `skin` `morning` `sea` `rain` `tea` `garden` `dessert` `fire` `study` `temple` `night` |
| `seasons` |  | `s`春 `u`夏 `a`秋 `w`冬，例如 `aw` |
| `sillage` |  | 存在感 1–3 |
| `gender` |  | `女` / `男` / `中性` |
| `year` |  | 推出年份 |
| `region` |  | `歐美` `日本` `韓國` `中國` `港台` `中東` `其他` |
| `tier` |  | `d`專櫃大牌 `n`沙龍小眾 `i`獨立調香 |
| `availability` |  | `c`台灣有專櫃 `o`選品店／電商 `n`需線上或代購 |
| `price_ml` / `price_ntd` |  | 容量與台幣價格 |
| `discontinued` |  | 停產填 `1` |
| `popularity` |  | 排序用的熱門度數字，不確定就留空 |

用 Excel 編輯也可以，存檔時選 **CSV UTF-8**，否則中文會亂碼。

## 大量更新資料（進階）

`tools/build.py` 從 Fragrantica 公開資料集重新產生 `perfumes.json`，`tools/maps.py` 是中文品牌名、香水中文名、香材翻譯、台灣通路與價格的對照表。修改對照表後：

```bash
pip install pandas pypinyin opencc-python-reimplemented
git clone --depth 1 https://github.com/aStyxxx/dataset_Fragrantica_perfumes
git clone --depth 1 https://github.com/leev75/fragrance-analytics-dashboard-
mv dataset_Fragrantica_perfumes aStyxxx__dataset_Fragrantica_perfumes
mv fragrance-analytics-dashboard- leev75__fragrance-analytics-dashboard-
python3 tools/build.py index.html   # 產生 perfumes.json 與 py.json
```

## 資料來源與注意事項

- 香調、前中後調、調香師、年份、持香評分取自 Fragrantica 社群的公開資料集；商業使用前請先確認授權。
- 價格為參考價，以實際售價為準；停產只標示已確認的幾支。
