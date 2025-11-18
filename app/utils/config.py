"""
設定管理モジュール
APIキーの暗号化保存と設定の読み書きを管理
"""
import json
import os
from pathlib import Path
from typing import Optional, Dict, Any
from cryptography.fernet import Fernet


class Config:
    """アプリケーション設定管理クラス"""

    def __init__(self):
        self.config_dir = Path.home() / '.story-generator'
        self.config_file = self.config_dir / 'config.json'
        self.key_file = self.config_dir / 'secret.key'
        self._ensure_config_dir()
        self._load_or_create_key()
        self.settings = self._load_config()

    def _ensure_config_dir(self):
        """設定ディレクトリの作成"""
        self.config_dir.mkdir(parents=True, exist_ok=True)

    def _load_or_create_key(self):
        """暗号化キーの読み込みまたは生成"""
        if self.key_file.exists():
            with open(self.key_file, 'rb') as f:
                self.key = f.read()
        else:
            self.key = Fernet.generate_key()
            with open(self.key_file, 'wb') as f:
                f.write(self.key)
            # キーファイルのパーミッションを制限（Unix系のみ）
            if os.name != 'nt':
                os.chmod(self.key_file, 0o600)

        self.cipher = Fernet(self.key)

    def _load_config(self) -> Dict[str, Any]:
        """設定ファイルの読み込み"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return self._default_config()
        return self._default_config()

    def _default_config(self) -> Dict[str, Any]:
        """デフォルト設定"""
        return {
            'api': {
                'encrypted_key': None,
                'model': 'gemini-2.0-flash-exp',
                'temperature': 0.7,
                'max_tokens': 4000,
                'top_p': 0.9
            },
            'ui': {
                'theme_mode': 'dark',
                'color_theme': 'blue'
            },
            'last_project': None
        }

    def save_config(self):
        """設定ファイルの保存"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
        except IOError as e:
            raise Exception(f"設定の保存に失敗しました: {e}")

    def encrypt_api_key(self, api_key: str) -> str:
        """APIキーの暗号化"""
        encrypted = self.cipher.encrypt(api_key.encode())
        return encrypted.decode()

    def decrypt_api_key(self, encrypted_key: str) -> str:
        """APIキーの復号化"""
        try:
            decrypted = self.cipher.decrypt(encrypted_key.encode())
            return decrypted.decode()
        except Exception:
            return ""

    def set_api_key(self, api_key: str):
        """APIキーの設定"""
        # 'api'キーが存在しない場合、デフォルト値で初期化
        if 'api' not in self.settings:
            self.settings['api'] = self._default_config()['api']

        encrypted = self.encrypt_api_key(api_key)
        self.settings['api']['encrypted_key'] = encrypted
        self.save_config()

    def get_api_key(self) -> Optional[str]:
        """APIキーの取得"""
        # 'api'キーが存在しない場合、Noneを返す
        if 'api' not in self.settings:
            return None

        encrypted_key = self.settings['api'].get('encrypted_key')
        if encrypted_key:
            return self.decrypt_api_key(encrypted_key)
        return None

    def set_api_config(self, model: str, temperature: float, max_tokens: int, top_p: float):
        """API設定の更新"""
        # 'api'キーが存在しない場合、デフォルト値で初期化
        if 'api' not in self.settings:
            self.settings['api'] = self._default_config()['api']

        self.settings['api']['model'] = model
        self.settings['api']['temperature'] = temperature
        self.settings['api']['max_tokens'] = max_tokens
        self.settings['api']['top_p'] = top_p
        self.save_config()

    def get_api_config(self) -> Dict[str, Any]:
        """API設定の取得"""
        # 'api'キーが存在しない場合、デフォルト値を返す
        if 'api' not in self.settings:
            self.settings['api'] = self._default_config()['api']
            self.save_config()

        # 必要なキーが存在することを確認
        required_keys = ['model', 'temperature', 'max_tokens', 'top_p']
        api = self.settings['api']
        if not all(key in api for key in required_keys):
            self.settings['api'] = self._default_config()['api']
            self.save_config()

        return self.settings['api']

    def set_ui_theme(self, mode: str, color: str):
        """UIテーマの設定"""
        # 'ui'キーが存在しない場合、デフォルト値で初期化
        if 'ui' not in self.settings:
            self.settings['ui'] = self._default_config()['ui']

        self.settings['ui']['theme_mode'] = mode
        self.settings['ui']['color_theme'] = color
        self.save_config()

    def get_ui_theme(self) -> Dict[str, str]:
        """UIテーマの取得"""
        # 'ui'キーが存在しない場合、デフォルト値を返す
        if 'ui' not in self.settings:
            self.settings['ui'] = self._default_config()['ui']
            self.save_config()

        # 必要なキーが存在することを確認
        ui = self.settings['ui']
        if 'theme_mode' not in ui or 'color_theme' not in ui:
            self.settings['ui'] = self._default_config()['ui']
            self.save_config()

        return self.settings['ui']

    def set_last_project(self, project_path: Optional[str]):
        """最後に開いたプロジェクトの設定"""
        self.settings['last_project'] = project_path
        self.save_config()

    def get_last_project(self) -> Optional[str]:
        """最後に開いたプロジェクトの取得"""
        return self.settings.get('last_project')
