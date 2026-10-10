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
| 1:17 | `YEAH` ×2 | 追加（1:17.2 と 1:17.9、画面中央の同じ位置） |
| 1:26 | `FF>>` | メンバー入場部分 |
| 1:45 | `20 MINUTES LATER` | 表示中は音声を消す（`edl.py` の `MUTE`） |
| 1:59 | `EVERYONE` | |
| 2:13–2:22 | `KAZUHO` → `IZUSHUN` → `KAZUHO AND IZUSHUN` | 本家の人名（JACOB MANN / PAUL CORNISH）の位置に置き換え |
| 2:47 | `IZUSHUN` | 本家 SAM WILKES（ベース）の位置 |
| 2:49 | `BASS FILL APPROVED` | |
| 3:24 | `HORN BREAKDOWN` | 2分割画面 |
| 3:49 | `KAESUKE` | トランペットソロ（本家 ZACH RAMACIER の位置） |
| 4:14 | （一瞬暗転 → ドラム → 分割画面） | 本家と同じ流れ |
| 4:15 | `BASSLINE BUDDIEZ` | 5分割画面のラベル |
| 4:40 | `THEY LOVE IT` | |

文字はタイピング風ではなく、そのまま出てそのまま消える（`type=True` を付けた文字だけタイピング表示）。

## 編集の変更方法

* カット・ズーム・分割画面: `edl.py` の `SHOTS`
  * `S(開始, 終了, "W"/"H", 開始時の枠, 終了時の枠)` … 枠を変えるとゆっくりズームイン/アウト
  * 枠の位置は `WR`（全体カメラ）/ `HR`（手持ち）に `(x, y, 幅, 高さ)` で定義
* ズームの動きの量: `edl.py` の `ZOOM_AMOUNT`（1.0 = 最大、現在 0.8）
* 文字: `edl.py` の `TEXTS`（時間・文言・位置・サイズ）
* 音声を消す区間: `edl.py` の `MUTE`
* フォント: Press Start 2P（SIL Open Font License, `fonts/OFL.txt`）

## 書き出し

```bash
# 確認用（半分の解像度）
./build.sh 全体カメラ.MOV 手持ちカメラ.MOV out_preview 0.5 23
# 本番（1920x1080 / 30fps）
./build.sh 全体カメラ.MOV 手持ちカメラ.MOV out 1 18
```

必要なもの: `ffmpeg`, Python 3, `numpy`, `Pillow`

---

# 2曲目 FAILING IN A COOL WAY

編集データは `edl_song2.py`（1曲目の `edl.py` とは別ファイル。書き出し名も `failing_in_a_cool_way_edit.mp4`）。

```bash
EDL=edl_song2.py ./build.sh 全体カメラ.MOV 手持ちカメラ.MOV out_song2 1 18
```

* 音源は全体カメラ（`louiscole2曲目_全体カメラ` 相当）。手持ちカメラは全体カメラより **100.6 秒早く** 録画開始（音声の相互相関で計測）。手持ちの映像は全体カメラの 4:19 で終わるので、それ以降は全体カメラのみ。
* 歌詞は本家の表示タイミングを読み取り、こちらの演奏に合わせて 1番 +7.92 秒 / 2番 +7.70 秒ずらして表示。
* 本家 3:00 以降の日本語（サックス①-1、ここのフィルは〜 など）は入れていない。

| 時間 | 文字 | 備考 |
| --- | --- | --- |
| 0:01 | `FAILING IN A COOL WAY / BY: LOUIS COLE` | 曲名クレジット |
| 0:25–0:50 | 1番の歌詞 | 本家と同じ水色 |
| 0:56 | `(we ran out of camera angles)` | |
| 1:13 | `IZUSHUN` | 本家 PETTER 9000 の位置（ベース） |
| 1:42–2:06 | 2番の歌詞 | |
| 3:07 | `SHIORI` | サックスソロ1人目（1列目いちばん右）。本家 HENRY SOLOMON のレイアウト（3画面 + `GROOVE ZONE`） |
| 3:36 | `TOWACO` / `SO HD` | 2人目（右から3番目） |
| 3:54 | `KOTOMI` | 3人目（TOWACO の右隣）。4:06 まで |
| 4:26 | `YEAH` | |

---

# YouTube Shorts（縦型 1080x1920）: SAX SOLO RELAY

`short_sax_relay.py` … 2曲目のサックスソロ（3:07〜4:06）を、3人でつなぐ「ゲームのプレイヤー交代」に見立てた約1分の縦型動画。

```bash
python3 short_sax_relay.py 全体カメラ.MOV 手持ちカメラ.MOV short_sax_relay_vertical.mp4
```

* 上: `LOUIS COLE` / 曲名 / `SAX SOLO RELAY`
* 中: ホーン全体（全体カメラ・手持ちカメラを 4 小節ごとに切り替え）
* 下: いまソロ中の人のアップ（ゆっくりズームイン）
* 交代のたびに白フラッシュ + `PLAYER 1/2/3`、下に `PLAYER 1` などと進行ゲージ（名前は出さない）
* 4:06 で全員が戻ったら下の画面がバンド全体に切り替わる（文字なし）

## ほかの Shorts（`shorts.py`）

```bash
python3 shorts.py loop    1曲目全体.MOV 1曲目手持ち.MOV short_loop_vertical.mp4
python3 shorts.py stack   1曲目全体.MOV 1曲目手持ち.MOV short_stack_vertical.mp4
python3 shorts.py karaoke 2曲目全体.MOV 2曲目手持ち.MOV short_karaoke_vertical.mp4
```

| 名前 | 場面 | レイアウト |
| --- | --- | --- |
| `loop` | 1曲目 0:10–0:49 ループ録音 | 縦全画面で1人を追う。録音中は手元に寄り、大きな `REC`（点滅）/ `PLAY`、`LOOP x1〜x3` と重なった数のゲージ |
| `stack` | 1曲目 3:23–3:54 HORN BREAKDOWN → トランペットソロ | 16:9 の画面を3段に積み、2小節ごとに上から順に切り替え。ソロに入ると3段ともトランペット |
| `karaoke` | 2曲目 0:25–0:51 1番 | 縦全画面でメンバーを順に寄りで映し、歌詞を画面下に大きく表示 |
