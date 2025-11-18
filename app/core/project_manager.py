"""
プロジェクト管理システム
プロジェクトの作成、保存、読み込みを管理
"""
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
from app.utils.json_handler import JSONHandler


class ProjectManager:
    """プロジェクトを管理するクラス"""

    def __init__(self):
        self.current_project: Optional[Dict[str, Any]] = None
        self.current_project_path: Optional[str] = None
        self.json_handler = JSONHandler()

    def create_new_project(self, name: str, save_path: str) -> Dict[str, Any]:
        """
        新規プロジェクトの作成

        Args:
            name: プロジェクト名
            save_path: 保存先パス

        Returns:
            作成されたプロジェクトデータ
        """
        project_data = self.json_handler.create_default_project(name)
        self.current_project = project_data
        self.current_project_path = save_path

        # プロジェクトを保存
        self.save_project()

        return project_data

    def save_project(self, save_path: Optional[str] = None):
        """
        プロジェクトの保存

        Args:
            save_path: 保存先パス（Noneの場合は現在のパス）
        """
        if not self.current_project:
            raise Exception("保存するプロジェクトがありません")

        path = save_path or self.current_project_path
        if not path:
            raise Exception("保存先パスが指定されていません")

        # 更新日時を更新
        self.current_project = self.json_handler.update_timestamp(self.current_project)

        # 保存
        self.json_handler.save_json(self.current_project, path)
        self.current_project_path = path

    def load_project(self, file_path: str) -> Dict[str, Any]:
        """
        プロジェクトの読み込み

        Args:
            file_path: 読み込むファイルパス

        Returns:
            読み込まれたプロジェクトデータ
        """
        project_data = self.json_handler.load_json(file_path)

        if not project_data:
            raise Exception("プロジェクトファイルが見つかりません")

        # データの検証
        if not self.json_handler.validate_project_data(project_data):
            raise Exception("プロジェクトファイルのフォーマットが不正です")

        self.current_project = project_data
        self.current_project_path = file_path

        return project_data

    def close_project(self):
        """プロジェクトを閉じる"""
        self.current_project = None
        self.current_project_path = None

    def add_character(self, character_data: Dict[str, str]) -> None:
        """
        キャラクターを追加

        Args:
            character_data: キャラクター情報
        """
        if not self.current_project:
            raise Exception("プロジェクトが開かれていません")

        # IDを付与
        character_id = self._generate_id()
        character_data['id'] = character_id

        self.current_project['characters'].append(character_data)
        self.save_project()

    def update_character(self, character_id: str, character_data: Dict[str, str]) -> None:
        """
        キャラクターを更新

        Args:
            character_id: キャラクターID
            character_data: 更新するキャラクター情報
        """
        if not self.current_project:
            raise Exception("プロジェクトが開かれていません")

        for i, char in enumerate(self.current_project['characters']):
            if char.get('id') == character_id:
                character_data['id'] = character_id
                self.current_project['characters'][i] = character_data
                self.save_project()
                return

        raise Exception("指定されたキャラクターが見つかりません")

    def delete_character(self, character_id: str) -> None:
        """
        キャラクターを削除

        Args:
            character_id: キャラクターID
        """
        if not self.current_project:
            raise Exception("プロジェクトが開かれていません")

        self.current_project['characters'] = [
            char for char in self.current_project['characters']
            if char.get('id') != character_id
        ]
        self.save_project()

    def get_characters(self) -> List[Dict[str, str]]:
        """
        全キャラクターを取得

        Returns:
            キャラクターリスト
        """
        if not self.current_project:
            return []

        return self.current_project['characters']

    def get_character_by_id(self, character_id: str) -> Optional[Dict[str, str]]:
        """
        IDでキャラクターを取得

        Args:
            character_id: キャラクターID

        Returns:
            キャラクター情報
        """
        if not self.current_project:
            return None

        for char in self.current_project['characters']:
            if char.get('id') == character_id:
                return char

        return None

    def set_world_settings(self, world_data: Dict[str, str]) -> None:
        """
        世界観設定を保存

        Args:
            world_data: 世界観情報
        """
        if not self.current_project:
            raise Exception("プロジェクトが開かれていません")

        self.current_project['world_settings'] = world_data
        self.save_project()

    def get_world_settings(self) -> Dict[str, str]:
        """
        世界観設定を取得

        Returns:
            世界観情報
        """
        if not self.current_project:
            return {}

        return self.current_project['world_settings']

    def add_scene(self, scene_data: Dict[str, Any]) -> None:
        """
        シーンを追加

        Args:
            scene_data: シーン情報
        """
        if not self.current_project:
            raise Exception("プロジェクトが開かれていません")

        # IDを付与
        scene_id = self._generate_id()
        scene_data['id'] = scene_id
        scene_data['created_at'] = datetime.now().isoformat()

        self.current_project['scenes'].append(scene_data)
        self.save_project()

    def update_scene(self, scene_id: str, scene_data: Dict[str, Any]) -> None:
        """
        シーンを更新

        Args:
            scene_id: シーンID
            scene_data: 更新するシーン情報
        """
        if not self.current_project:
            raise Exception("プロジェクトが開かれていません")

        for i, scene in enumerate(self.current_project['scenes']):
            if scene.get('id') == scene_id:
                scene_data['id'] = scene_id
                scene_data['created_at'] = scene.get('created_at')
                scene_data['updated_at'] = datetime.now().isoformat()
                self.current_project['scenes'][i] = scene_data
                self.save_project()
                return

        raise Exception("指定されたシーンが見つかりません")

    def delete_scene(self, scene_id: str) -> None:
        """
        シーンを削除

        Args:
            scene_id: シーンID
        """
        if not self.current_project:
            raise Exception("プロジェクトが開かれていません")

        self.current_project['scenes'] = [
            scene for scene in self.current_project['scenes']
            if scene.get('id') != scene_id
        ]
        self.save_project()

    def reorder_scenes(self, scene_ids: List[str]) -> None:
        """
        シーンの順序を変更

        Args:
            scene_ids: 新しい順序でのシーンIDリスト
        """
        if not self.current_project:
            raise Exception("プロジェクトが開かれていません")

        # 現在のシーンをIDでマッピング
        scenes_map = {scene['id']: scene for scene in self.current_project['scenes']}

        # 新しい順序でシーンリストを作成
        new_scenes = []
        for scene_id in scene_ids:
            if scene_id in scenes_map:
                new_scenes.append(scenes_map[scene_id])

        # シーンリストを更新
        self.current_project['scenes'] = new_scenes
        self.save_project()

    def get_scenes(self) -> List[Dict[str, Any]]:
        """
        全シーンを取得

        Returns:
            シーンリスト
        """
        if not self.current_project:
            return []

        return self.current_project['scenes']

    def get_scene_by_id(self, scene_id: str) -> Optional[Dict[str, Any]]:
        """
        IDでシーンを取得

        Args:
            scene_id: シーンID

        Returns:
            シーン情報
        """
        if not self.current_project:
            return None

        for scene in self.current_project['scenes']:
            if scene.get('id') == scene_id:
                return scene

        return None

    def set_writing_style(self, style_data: Dict[str, str]) -> None:
        """
        文体スタイルを設定

        Args:
            style_data: 文体スタイル情報
        """
        if not self.current_project:
            raise Exception("プロジェクトが開かれていません")

        self.current_project['writing_style'] = style_data
        self.save_project()

    def get_writing_style(self) -> Dict[str, str]:
        """
        文体スタイルを取得

        Returns:
            文体スタイル情報
        """
        if not self.current_project:
            return {
                'perspective': '三人称',
                'tense': '過去形',
                'tone': '標準',
                'description_level': '中程度',
                'dialogue_style': '標準'
            }

        return self.current_project['writing_style']

    def get_project_name(self) -> str:
        """
        プロジェクト名を取得

        Returns:
            プロジェクト名
        """
        if not self.current_project:
            return "未保存"

        return self.current_project.get('name', '未保存')

    def _generate_id(self) -> str:
        """
        ユニークIDを生成

        Returns:
            生成されたID
        """
        import uuid
        return str(uuid.uuid4())
