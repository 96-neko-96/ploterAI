# Gemini API セットアップガイド

このドキュメントでは、Story Generatorで使用するGemini APIキーの取得方法を説明します。

## 目次

1. [Gemini APIとは](#gemini-apiとは)
2. [APIキーの取得方法](#apiキーの取得方法)
3. [APIキーの設定](#apiキーの設定)
4. [料金について](#料金について)
5. [利用制限](#利用制限)
6. [トラブルシューティング](#トラブルシューティング)

## Gemini APIとは

Gemini APIは、GoogleのAIモデル「Gemini」を利用するためのAPIです。高品質なテキスト生成が可能で、Story GeneratorではこのAPIを使って物語を生成します。

### 利用可能なモデル

- **gemini-2.5-pro**: 最高品質の出力（最新）
- **gemini-2.5-flash**: バランスの取れた高速モデル（最新）
- **gemini-2.5-flash-lite**: 超高速な軽量モデル（最新）
- **gemini-2.0-flash** (推奨): 高速で安定したモデル
- **gemini-2.0-flash-lite**: 高速な軽量モデル
- **gemini-2.0-flash-exp**: 実験的な高速モデル
- **gemini-1.5-pro**: 高品質な出力
- **gemini-1.5-flash**: 高速な応答

## APIキーの取得方法

### ステップ1: Google AI Studioにアクセス

1. ブラウザで [https://ai.google.dev/](https://ai.google.dev/) にアクセス
2. 「Get started」または「Try Gemini API」をクリック

### ステップ2: Googleアカウントでサインイン

1. Googleアカウントでログイン
2. 初めての場合は利用規約に同意

### ステップ3: APIキーを作成

1. Google AI Studio（[https://makersuite.google.com/](https://makersuite.google.com/)）にアクセス
2. 左メニューから「Get API key」を選択
3. 「Create API key」をクリック
4. プロジェクトを選択（または新規作成）
5. APIキーが表示されます
6. 「Copy」をクリックしてコピー

**重要**: APIキーは再表示できないため、必ず安全な場所に保存してください。

### 詳細な手順（スクリーンショット付き）

#### 1. Google AI Studioへのアクセス

![Google AI Studio](https://ai.google.dev/)

「Get API key」ボタンをクリックします。

#### 2. APIキーの作成

新しいAPIキーを作成するか、既存のプロジェクトからキーを取得します。

#### 3. APIキーのコピー

生成されたAPIキーは以下のような形式です:

```
AIzaSy...（長い文字列）
```

このキーをコピーして安全に保管してください。

## APIキーの設定

### Story Generatorでの設定

1. Story Generatorを起動
2. トップメニューから「API設定」をクリック
3. 「APIキー」欄にコピーしたキーを貼り付け
4. 「接続テスト」をクリックして動作確認
5. 成功したら「保存」をクリック

### セキュリティ

- APIキーは暗号化されて保存されます
- 保存場所: `~/.story-generator/config.json`
- 暗号化キー: `~/.story-generator/secret.key`

**注意**: これらのファイルは他人と共有しないでください。

## 料金について

### 無料枠

Gemini APIには無料枠があります（2024年1月時点）:

- **Gemini 1.5 Flash**: 月間150万トークンまで無料
- **Gemini 1.5 Pro**: 月間15万トークンまで無料

### トークンとは

トークンは、AIが処理するテキストの単位です。

- 1トークン ≈ 日本語で約0.7文字
- 1000文字 ≈ 約1400トークン

### Story Generatorでの使用量目安

- **プロット生成**: 約2000-3000トークン
- **中編化**: 約4000-6000トークン
- **長編化**: 約8000-12000トークン
- **キャラクター生成**: 約1500-2500トークン
- **世界観生成**: 約2000-3000トークン

月間で約100-150の物語を生成できます（無料枠内）。

### 料金の確認

1. [Google Cloud Console](https://console.cloud.google.com/)にアクセス
2. プロジェクトを選択
3. 「Billing」から使用量を確認

## 利用制限

### レート制限

無料枠では以下のレート制限があります:

- **RPM** (Requests Per Minute): 15リクエスト/分
- **TPM** (Tokens Per Minute): 100万トークン/分

Story Generatorは自動的にレート制限を考慮しますが、短時間に大量の生成を行うとエラーが発生する可能性があります。

### 推奨される使用方法

- 生成は1つずつ実行
- エラーが出たら少し待ってから再実行
- 大量生成が必要な場合は間隔を空ける

## トラブルシューティング

### APIキーが無効と表示される

**原因**:
- APIキーが間違っている
- APIキーが無効化されている
- APIが有効化されていない

**解決方法**:
1. APIキーを再確認してください
2. Google Cloud Consoleで「Gemini API」が有効になっているか確認
3. 必要に応じて新しいAPIキーを作成

### 接続テストに失敗する

**原因**:
- インターネット接続の問題
- APIサービスの一時的な障害
- ファイアウォール/プロキシの問題

**解決方法**:
1. インターネット接続を確認
2. [Google Cloud Status](https://status.cloud.google.com/)でサービス状態を確認
3. ファイアウォール設定を確認

### 「Quota exceeded」エラー

**原因**:
- 無料枠を超えた
- レート制限に達した

**解決方法**:
1. [Google Cloud Console](https://console.cloud.google.com/)で使用量を確認
2. 月初まで待つ（無料枠がリセットされます）
3. 有料プランへのアップグレードを検討

### 「API not enabled」エラー

**原因**:
- プロジェクトでGemini APIが有効化されていない

**解決方法**:
1. [Google Cloud Console](https://console.cloud.google.com/)にアクセス
2. プロジェクトを選択
3. 「APIs & Services」→「Enable APIs and Services」
4. 「Gemini API」を検索して有効化

## APIキーの管理

### セキュリティベストプラクティス

1. **共有しない**: APIキーは絶対に他人と共有しない
2. **公開しない**: GitHubなどにアップロードしない
3. **定期的に更新**: セキュリティのため定期的に再生成
4. **権限を制限**: 必要最小限の権限のみ付与

### APIキーの再生成

セキュリティ上の理由でAPIキーを再生成する必要がある場合:

1. Google AI Studioにアクセス
2. 既存のAPIキーを削除
3. 新しいAPIキーを作成
4. Story Generatorで新しいキーを設定

### 複数のAPIキー

複数のプロジェクトで使用する場合、それぞれに異なるAPIキーを使用することを推奨します。

## 参考リンク

- [Google AI for Developers](https://ai.google.dev/)
- [Gemini API Documentation](https://ai.google.dev/docs)
- [Google Cloud Console](https://console.cloud.google.com/)
- [Pricing Information](https://ai.google.dev/pricing)

## サポート

APIキーに関する問題が解決しない場合:

1. [Google AI Studio Help](https://support.google.com/)
2. Story Generatorの[GitHub Issues](https://github.com/your-repo/issues)

---

**重要な注意事項**

- APIキーは秘密情報として扱ってください
- 不正使用を防ぐため、定期的にキーを確認してください
- 予期しない使用量がある場合は、すぐにキーを再生成してください
