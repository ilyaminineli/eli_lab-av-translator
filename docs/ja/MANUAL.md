---
title: 操作マニュアル
section: 02 / OPERATIONS
lang: ja
---
# 操作マニュアル

このマニュアルでは、PCの準備、映像素材の読み込み、構成の作成、外部コントロールの接続、ライブパフォーマンスの順に説明します。

## 01 — インストールと起動

パッケージ版は Windows 11 x64 と OpenGL 3.3 Core Profile 対応のグラフィックスドライバーを対象としています。[GitHub Releases](https://github.com/ilyaminineli/eli_lab-av-translator/releases) から Windows 版を入手してください。

開発環境から起動する場合は [Windows setup guide](../SETUP_WINDOWS.md) を参照してください。パッケージ版の実行に Python は必要ありません。Sonic Pi、映像素材、ユーザー追加の素材フォルダーは別途用意します。

## 02 — 映像素材を準備する

1. ローカルフォルダーに映像素材をまとめます。最初は H.264 MP4 の720pまたは1080p素材を推奨します。
2. **PREPARE** ワークスペースを開き、Media Library にフォルダーを追加します。
3. 索引作成とサムネイル生成が完了するまで待ちます。
4. 4つの独立した動画デッキにクリップを読み込みます。
5. 元の動画ファイルはプロジェクトの外部にあります。削除・移動しないでください。

## 03 — ビジュアルを構成する

**COMPOSE** を開き、必要な要素を追加します。

- ジオメトリ、波形、パーティクルのジェネレーター。
- Text Art、アニメーション文字、縦書き。
- 画像・動画オーバーレイ。
- レイヤーの変形、不透明度、合成モード、順序。
- マスターフィルターとレイヤー別エフェクトスタック。

詳しくは [Generative visuals](../M2_GENERATIVE_VISUALS.md) と [Typography](../M6_E_TYPOGRAPHY.md) を参照してください。

## 04 — 音や時間に反応させる

6つの Performance Macro は、複数のビジュアルパラメーターをまとめて制御する共通の操作系です。Modulator Bank では LFO、エンベロープ、ステップ、リズム、フォロワーを使えます。

音声解析には物理入力またはシステムループバックを使用します。MIDI機器から操作することもできます。

## 05 — Sonic Pi を接続する

AVTranslator は `/eli_lab/v1` OSC プロトコルを受信します。Sonic Pi は音楽再生を担当し、AVTranslator はトランスポート、キュー、マクロの情報を受け取って映像を制御します。

同じPCで使用する場合は `127.0.0.1` から始めます。別PCを使う場合は、AVTranslator が動作するPCのLANアドレスを指定してください。

詳細は [Sonic Pi / SONATA integration guide](../SONIC_PI_SONATA_INTEGRATION.md) を参照してください。

## 06 — ライブセットを構成する

VJシーンでビジュアル状態を保存・呼び出しできます。ライブタイムラインは小節とビートを基準にマーカーやアクションを予約します。Performance Mode は外部コントロールと AUTO PERF をアームしますが、Sonic Pi 自体は起動しません。

## 07 — プロジェクターに出力する

1. 出力を開く前にプロジェクターを接続します。
2. Windows のディスプレイ設定を「表示画面を拡張する」にします。
3. **View → PROJECTOR OUTPUT** から出力先ディスプレイを選択します。
4. 実際のPCとプロジェクターで解像度・リフレッシュレート・長時間動作を確認してください。

## 08 — プロジェクトを保存して移動する

- `.eliav` は構成とプロジェクト状態を保存します。
- `.eliset` はパフォーマンスセットを保存します。
- 元の動画・画像ファイルは別に管理されます。

別PCへ移す場合は素材フォルダーもコピーし、Media Library に再登録してください。

## トラブルシューティング

- [Windows setup and troubleshooting](../SETUP_WINDOWS.md)
- [Project format](../PROJECT_FORMAT.md)
- [Sonic Pi / OSC](../SONIC_PI_SONATA_INTEGRATION.md)

自動テストの成功は、対象PCのOpenGL、複数デッキ再生、長時間動作、プロジェクター出力の検証を意味しません。重要な公演の前に実機で確認してください。
