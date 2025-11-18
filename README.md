# Story Generator

Gemini APIを活用した物語生成デスクトップアプリケーション。CustomTkinterを使用した美しいGUIで、キャラクター管理、世界観設定、3段階の物語生成（プロット→中編→長編）を実現します。

## 特徴

- 🤖 **AIによる物語生成**: Gemini APIを活用した高品質な物語生成
- 👥 **キャラクター管理**: 手動作成とAI生成に対応
- 🌍 **世界観設定**: 詳細な世界観の構築と管理
- 📝 **3段階生成**: プロット→中編→長編と段階的に物語を膨らませる
- 💾 **プロジェクト管理**: JSON形式での保存と読み込み
- 📤 **複数形式エクスポート**: TXT、Markdown、PDF形式に対応
- 🎨 **カスタマイズ可能**: テーマ、文体スタイルの設定
- 🔒 **セキュア**: APIキーの暗号化保存

## インストール

### 必要要件

- Python 3.8以上
- pip

### ステップ1: リポジトリのクローン

```bash
git clone <repository-url>
cd ploterAI
```

### ステップ2: 依存関係のインストール

```bash
pip install -r requirements.txt
```

### ステップ3: Gemini APIキーの取得

[API_SETUP.md](API_SETUP.md)を参照してください。

## 使用方法

### アプリケーションの起動

```bash
python app/main.py
```

### 初回セットアップ

1. アプリケーションを起動
2. 「API設定」からGemini APIキーを設定
3. 「新規プロジェクト」でプロジェクトを作成
4. キャラクターや世界観を設定
5. シーンを作成して物語を生成

詳細な使用方法は[USAGE.md](USAGE.md)を参照してください。

## 主な機能

### プロジェクト管理

- 新規プロジェクト作成
- プロジェクトの保存・読み込み
- 名前を付けて保存
- 自動保存

### キャラクター管理

- 手動でキャラクター作成（8つの項目）
- AIによる自動生成
- キャラクターの編集・削除
- リスト表示

### 世界観設定

- 手動で世界観作成（8つの項目）
- AIによる自動生成
- 詳細な設定項目

### 物語生成

- **プロット生成**: 500-1000文字の簡潔なあらすじ
- **中編化**: 2000-3000文字に拡張
- **長編化**: 5000文字以上の本格的な物語

### エクスポート

- **TXT形式**: プレーンテキスト
- **Markdown形式**: 見出し付き
- **PDF形式**: 日本語対応

## ビルド

### exe化（Windows）

```bash
pyinstaller build.spec
```

実行ファイルは `dist/StoryGenerator.exe` に生成されます。

## ディレクトリ構造

```
ploterAI/
├── app/
│   ├── core/              # コアロジック
│   ├── gui/               # GUIコンポーネント
│   ├── utils/             # ユーティリティ
│   └── main.py            # エントリーポイント
├── data/
│   ├── projects/          # プロジェクト保存先
│   └── templates/         # テンプレート
├── resources/             # リソースファイル
├── requirements.txt       # 依存関係
├── build.spec             # PyInstallerビルド設定
└── README.md
```

## 設定ファイル

設定は `~/.story-generator/` に保存されます：

- `config.json`: アプリケーション設定
- `secret.key`: 暗号化キー（自動生成）

## トラブルシューティング

### APIキーエラー

- 「API設定」から正しいAPIキーを設定してください
- [API_SETUP.md](API_SETUP.md)を参照

### PDFエクスポートエラー

- 日本語フォントがインストールされているか確認してください
- Windows: MSゴシック（デフォルト）
- Linux: Takao Gothic または Noto Sans CJK

### アプリケーションが起動しない

```bash
# 依存関係を再インストール
pip install --upgrade -r requirements.txt

# エラーログを確認
python app/main.py
```

## ライセンス

このプロジェクトは教育目的で作成されています。

## サポート

問題が発生した場合は、GitHubのIssuesでお知らせください。

## 開発

### テスト

```bash
# TODO: テストスクリプトを追加
```

### 貢献

プルリクエストを歓迎します。大きな変更の場合は、まずIssueを開いて変更内容を議論してください。

---

**Story Generator** - Gemini APIで創作活動をサポート
