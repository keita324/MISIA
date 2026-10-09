# F IT UP（1曲目）編集スクリプト

Louis Cole「Live 2019」の1曲目の動画を参考に、全体カメラと手持ちカメラの2本からカット割り・ズーム・ゲーム風のドット文字を入れた動画を作ります。

## 素材

| 素材 | 使い方 |
| --- | --- |
| 全体カメラ（`louiscole_1曲目_全体カメラ`） | 音源はすべてここから使う。映像は三脚固定なので、ズームはここからの切り抜き |
| 手持ちカメラ（`louiscole1曲目_手持ちカメラ`） | 映像のみ使う（音声は使わない） |

* 手持ちカメラは全体カメラより **11.92 秒遅れて** 録画開始（音声の相互相関で計測。曲全体でずれは ±0.03 秒以内）。
* 本家の字幕タイミングは、本家の音声とこちらの演奏音声を区間ごとに照合して、こちらの演奏時間に合わせ直した。

## 字幕（本家から流用したもの / 置き換えたもの）

| 時間 | 文字 | 備考 |
| --- | --- | --- |
| 0:01 | `2026` | 本家「LOUIS COLE / LOS ANGELES / 2019」のうち固有名詞以外（年号は撮影日の 2026 年に変更） |
| 0:10 | `F IT UP / BY: LOUIS COLE` | 曲名と作曲者のクレジット（演奏曲そのものなので残した） |
| 0:13–0:48 | ● `KEYBOARD PART` / ▶ / ● `KEYBOARD PART 2` / ▶ / ● `BASS` / ▶ | ループ録音の REC / PLAY 表示 |
| 1:15 | `THROAT SLAP VOCAL RUN` | |
| 1:26 | `FF>>` | メンバー入場部分 |
| 1:45 | `20 MINUTES LATER` | |
| 1:59 | `EVERYONE` | |
| 2:13–2:22 | `KAZUHO` → `IZUSHUN` → `KAZUHO AND IZUSHUN` | 本家の人名（JACOB MANN / PAUL CORNISH）の位置に置き換え |
| 2:47 | `IZUSHUN` | 本家 SAM WILKES（ベース）の位置 |
| 2:49 | `BASS FILL APPROVED` | |
| 3:24 | `HORN BREAKDOWN` | 2分割画面 |
| 4:15 | `BASSLINE BUDDIEZ` | 5分割画面のラベル |
| 4:39 | `THEY LOVE IT` | |

ホーンの人名（本家 ZACH RAMACIER）は名前の指定がないので文字なし（分割画面・ズームのみ）。

## 編集の変更方法

* カット・ズーム・分割画面: `edl.py` の `SHOTS`
  * `S(開始, 終了, "W"/"H", 開始時の枠, 終了時の枠)` … 枠を変えるとゆっくりズームイン/アウト
  * 枠の位置は `WR`（全体カメラ）/ `HR`（手持ち）に `(x, y, 幅, 高さ)` で定義
* 文字: `edl.py` の `TEXTS`（時間・文言・位置・サイズ）
* フォント: Press Start 2P（SIL Open Font License, `fonts/OFL.txt`）

## 書き出し

```bash
# 確認用（半分の解像度）
./build.sh 全体カメラ.MOV 手持ちカメラ.MOV out_preview 0.5 23
# 本番（1920x1080 / 30fps）
./build.sh 全体カメラ.MOV 手持ちカメラ.MOV out 1 18
```

必要なもの: `ffmpeg`, Python 3, `numpy`, `Pillow`
