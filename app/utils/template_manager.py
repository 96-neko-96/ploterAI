"""
テンプレート管理モジュール
文体スタイルのテンプレート保存と読み込みを管理
"""
import json
from pathlib import Path
from typing import List, Dict, Any, Optional


class TemplateManager:
    """テンプレート管理クラス"""

    def __init__(self):
        self.template_dir = Path.home() / '.story-generator' / 'templates'
        self._ensure_template_dir()

    def _ensure_template_dir(self):
        """テンプレートディレクトリの作成"""
        self.template_dir.mkdir(parents=True, exist_ok=True)

    def save_template(self, name: str, style_data: Dict[str, Any]) -> bool:
        """
        テンプレートを保存

        Args:
            name: テンプレート名
            style_data: 文体スタイルデータ

        Returns:
            成功したかどうか
        """
        try:
            # ファイル名を安全にする
            safe_name = self._sanitize_filename(name)
            template_file = self.template_dir / f"{safe_name}.json"

            template_data = {
                'name': name,
                'style': style_data
            }

            with open(template_file, 'w', encoding='utf-8') as f:
                json.dump(template_data, f, indent=2, ensure_ascii=False)

            return True
        except Exception as e:
            print(f"テンプレート保存エラー: {e}")
            return False

    def load_template(self, name: str) -> Optional[Dict[str, Any]]:
        """
        テンプレートを読み込み

        Args:
            name: テンプレート名

        Returns:
            文体スタイルデータ、失敗時はNone
        """
        try:
            safe_name = self._sanitize_filename(name)
            template_file = self.template_dir / f"{safe_name}.json"

            if not template_file.exists():
                return None

            with open(template_file, 'r', encoding='utf-8') as f:
                template_data = json.load(f)

            return template_data.get('style')
        except Exception as e:
            print(f"テンプレート読み込みエラー: {e}")
            return None

    def delete_template(self, name: str) -> bool:
        """
        テンプレートを削除

        Args:
            name: テンプレート名

        Returns:
            成功したかどうか
        """
        try:
            safe_name = self._sanitize_filename(name)
            template_file = self.template_dir / f"{safe_name}.json"

            if template_file.exists():
                template_file.unlink()
                return True
            return False
        except Exception as e:
            print(f"テンプレート削除エラー: {e}")
            return False

    def list_templates(self) -> List[str]:
        """
        保存されているテンプレート一覧を取得

        Returns:
            テンプレート名のリスト
        """
        try:
            templates = []
            for file in self.template_dir.glob("*.json"):
                try:
                    with open(file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        name = data.get('name', file.stem)
                        templates.append(name)
                except Exception:
                    continue

            return sorted(templates)
        except Exception as e:
            print(f"テンプレート一覧取得エラー: {e}")
            return []

    def get_default_templates(self) -> Dict[str, Dict[str, Any]]:
        """
        デフォルトテンプレートを取得

        Returns:
            デフォルトテンプレートの辞書
        """
        return {
            'ライトノベル風': {
                'perspective': '一人称',
                'narration': '過去形',
                'tone': '標準',
                'description_level': '中程度',
                'dialogue_style': 'カジュアル'
            },
            '本格ファンタジー': {
                'perspective': '三人称',
                'narration': '過去形',
                'tone': 'シリアス',
                'description_level': '詳細',
                'dialogue_style': 'フォーマル'
            },
            'ミステリー・サスペンス': {
                'perspective': '三人称',
                'narration': '過去形',
                'tone': 'ダーク',
                'description_level': '詳細',
                'dialogue_style': '標準'
            },
            'コメディ': {
                'perspective': '一人称',
                'narration': '現在形',
                'tone': 'コメディ',
                'description_level': '簡潔',
                'dialogue_style': 'カジュアル'
            },
            'シンプル': {
                'perspective': '三人称',
                'narration': '過去形',
                'tone': '標準',
                'description_level': '簡潔',
                'dialogue_style': '標準'
            }
        }

    def _sanitize_filename(self, name: str) -> str:
        """
        ファイル名を安全にする

        Args:
            name: 元の名前

        Returns:
            安全なファイル名
        """
        # 使用できない文字を置換
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            name = name.replace(char, '_')

        # 長さを制限
        return name[:100]

    def ensure_default_templates(self):
        """デフォルトテンプレートが存在しない場合は作成"""
        defaults = self.get_default_templates()

        for name, style in defaults.items():
            safe_name = self._sanitize_filename(name)
            template_file = self.template_dir / f"{safe_name}.json"

            # 既に存在する場合はスキップ
            if not template_file.exists():
                self.save_template(name, style)
