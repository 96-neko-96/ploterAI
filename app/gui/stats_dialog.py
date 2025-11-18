"""
統計情報ダイアログ
プロジェクトの統計情報を表示
"""
import customtkinter as ctk
from typing import Dict, Any, List


class StatsDialog(ctk.CTkToplevel):
    """統計情報ダイアログクラス"""

    def __init__(self, parent, project_data: Dict[str, Any]):
        super().__init__(parent)

        self.title("統計情報")
        self.geometry("600x500")
        self.resizable(False, False)

        # モーダルにする
        self.transient(parent)
        self.grab_set()

        self.project_data = project_data
        self._create_widgets()
        self._calculate_stats()

    def _create_widgets(self):
        """ウィジェットの作成"""
        # メインフレーム
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # タイトル
        title_label = ctk.CTkLabel(
            main_frame,
            text="プロジェクト統計情報",
            font=("", 20, "bold")
        )
        title_label.pack(pady=(0, 20))

        # スクロール可能なフレーム
        scroll_frame = ctk.CTkScrollableFrame(main_frame, height=350)
        scroll_frame.pack(fill="both", expand=True, pady=(0, 20))

        # 統計情報表示エリア
        self.stats_text = ctk.CTkTextbox(scroll_frame, height=350)
        self.stats_text.pack(fill="both", expand=True)

        # 閉じるボタン
        close_btn = ctk.CTkButton(
            main_frame,
            text="閉じる",
            command=self.destroy,
            width=100
        )
        close_btn.pack()

    def _calculate_stats(self):
        """統計情報を計算して表示"""
        stats_text = []

        # プロジェクト名
        project_name = self.project_data.get('project_name', '不明')
        stats_text.append(f"【プロジェクト名】\n{project_name}\n")

        # キャラクター統計
        characters = self.project_data.get('characters', [])
        char_count = len(characters)
        stats_text.append(f"【キャラクター数】\n{char_count}名\n")

        if characters:
            stats_text.append("キャラクター一覧:")
            for i, char in enumerate(characters, 1):
                name = char.get('name', '不明')
                personality = char.get('personality', 'なし')
                stats_text.append(f"  {i}. {name} - {personality[:30]}...")
            stats_text.append("")

        # 世界観統計
        world = self.project_data.get('world_settings')
        if world:
            world_name = world.get('name', '不明')
            world_genre = world.get('era', '不明')
            stats_text.append(f"【世界観】\n名前: {world_name}\n時代: {world_genre}\n")
        else:
            stats_text.append("【世界観】\n未設定\n")

        # シーン統計
        scenes = self.project_data.get('scenes', [])
        scene_count = len(scenes)
        stats_text.append(f"【シーン数】\n{scene_count}シーン\n")

        if scenes:
            total_chars = 0
            total_words = 0

            for scene in scenes:
                content = scene.get('content', '')
                total_chars += len(content)
                total_words += len(content.split())

            avg_chars = total_chars // scene_count if scene_count > 0 else 0

            stats_text.append(f"総文字数: {total_chars:,}文字")
            stats_text.append(f"総単語数: {total_words:,}語")
            stats_text.append(f"平均文字数: {avg_chars:,}文字/シーン\n")

            stats_text.append("シーン一覧:")
            for i, scene in enumerate(scenes, 1):
                title = scene.get('title', '無題')
                content = scene.get('content', '')
                char_count_scene = len(content)
                stats_text.append(f"  {i}. {title} ({char_count_scene:,}文字)")
            stats_text.append("")

        # 文体スタイル
        style = self.project_data.get('writing_style')
        if style:
            stats_text.append("【文体スタイル】")
            stats_text.append(f"視点: {style.get('perspective', '不明')}")
            stats_text.append(f"語り口: {style.get('narration', '不明')}")
            stats_text.append(f"トーン: {style.get('tone', '不明')}")
            stats_text.append(f"描写レベル: {style.get('description_level', '不明')}")
            stats_text.append(f"会話スタイル: {style.get('dialogue_style', '不明')}\n")
        else:
            stats_text.append("【文体スタイル】\n未設定\n")

        # メタデータ
        metadata = self.project_data.get('metadata', {})
        created = metadata.get('created', '不明')
        modified = metadata.get('last_modified', '不明')

        stats_text.append("【メタデータ】")
        stats_text.append(f"作成日時: {created}")
        stats_text.append(f"最終更新: {modified}")

        # テキストボックスに表示
        self.stats_text.insert("1.0", "\n".join(stats_text))
        self.stats_text.configure(state="disabled")
