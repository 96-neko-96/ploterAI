"""
JSON処理ユーティリティ
プロジェクトデータの読み書きを管理
"""
import json
import shutil
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime


class JSONHandler:
    """JSON形式のデータ読み書きを管理するクラス"""

    @staticmethod
    def save_json(data: Dict[str, Any], file_path: str, create_backup: bool = True):
        """
        JSONファイルの保存

        Args:
            data: 保存するデータ
            file_path: 保存先ファイルパス
            create_backup: バックアップを作成するかどうか
        """
        path = Path(file_path)

        # バックアップの作成
        if create_backup and path.exists():
            backup_path = path.with_suffix('.json.bak')
            shutil.copy2(path, backup_path)

        # 親ディレクトリの作成
        path.parent.mkdir(parents=True, exist_ok=True)

        try:
            # 一時ファイルに書き込み
            temp_path = path.with_suffix('.json.tmp')
            with open(temp_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            # 一時ファイルを本ファイルに置き換え
            temp_path.replace(path)

        except Exception as e:
            # エラー時は一時ファイルを削除
            if temp_path.exists():
                temp_path.unlink()
            raise Exception(f"JSONファイルの保存に失敗しました: {e}")

    @staticmethod
    def load_json(file_path: str) -> Optional[Dict[str, Any]]:
        """
        JSONファイルの読み込み

        Args:
            file_path: 読み込むファイルパス

        Returns:
            読み込んだデータ、失敗時はNone
        """
        path = Path(file_path)

        if not path.exists():
            return None

        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            # バックアップからの復元を試みる
            backup_path = path.with_suffix('.json.bak')
            if backup_path.exists():
                try:
                    with open(backup_path, 'r', encoding='utf-8') as f:
                        return json.load(f)
                except json.JSONDecodeError:
                    pass
            raise Exception(f"JSONファイルの読み込みに失敗しました: {e}")
        except Exception as e:
            raise Exception(f"ファイルの読み込みに失敗しました: {e}")

    @staticmethod
    def validate_project_data(data: Dict[str, Any]) -> bool:
        """
        プロジェクトデータの検証

        Args:
            data: 検証するデータ

        Returns:
            検証結果
        """
        required_keys = ['name', 'characters', 'world_settings', 'scenes', 'writing_style']

        for key in required_keys:
            if key not in data:
                return False

        # 型のチェック
        if not isinstance(data['characters'], list):
            return False
        if not isinstance(data['world_settings'], dict):
            return False
        if not isinstance(data['scenes'], list):
            return False
        if not isinstance(data['writing_style'], dict):
            return False

        return True

    @staticmethod
    def create_default_project(name: str) -> Dict[str, Any]:
        """
        デフォルトプロジェクトデータの作成

        Args:
            name: プロジェクト名

        Returns:
            プロジェクトデータ
        """
        now = datetime.now().isoformat()

        return {
            'name': name,
            'characters': [],
            'world_settings': {},
            'scenes': [],
            'writing_style': {
                'perspective': '三人称',
                'tense': '過去形',
                'tone': '標準',
                'description_level': '中程度',
                'dialogue_style': '標準'
            },
            'created_at': now,
            'updated_at': now
        }

    @staticmethod
    def update_timestamp(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        更新日時の更新

        Args:
            data: プロジェクトデータ

        Returns:
            更新されたデータ
        """
        data['updated_at'] = datetime.now().isoformat()
        return data
