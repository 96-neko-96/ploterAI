"""
検索ダイアログ
キャラクターとシーンの検索機能
"""
import customtkinter as ctk
from tkinter import messagebox
from typing import Dict, Any, List, Callable


class SearchDialog(ctk.CTkToplevel):
    """検索ダイアログクラス"""

    def __init__(self, parent, project_manager, on_character_select: Callable, on_scene_select: Callable):
        super().__init__(parent)

        self.title("検索")
        self.geometry("800x700")
        self.minsize(600, 500)  # 最小サイズを設定
        self.resizable(True, True)  # リサイズ可能に

        # モーダルにする
        self.transient(parent)
        self.grab_set()

        self.project_manager = project_manager
        self.on_character_select = on_character_select
        self.on_scene_select = on_scene_select

        self._create_widgets()

        # ウィンドウを中央に配置
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (800 // 2)
        y = (self.winfo_screenheight() // 2) - (700 // 2)
        self.geometry(f"+{x}+{y}")

    def _create_widgets(self):
        """ウィジェットの作成"""
        # メインフレーム
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # タイトル
        title_label = ctk.CTkLabel(
            main_frame,
            text="検索",
            font=("", 20, "bold")
        )
        title_label.pack(pady=(0, 20))

        # 検索フレーム
        search_frame = ctk.CTkFrame(main_frame)
        search_frame.pack(fill="x", pady=(0, 20))

        # 検索ボックス
        ctk.CTkLabel(search_frame, text="検索キーワード:").pack(side="left", padx=5)

        self.search_entry = ctk.CTkEntry(search_frame, width=400)
        self.search_entry.pack(side="left", padx=5)
        self.search_entry.bind('<Return>', lambda e: self._perform_search())

        # 検索ボタン
        search_btn = ctk.CTkButton(
            search_frame,
            text="検索",
            command=self._perform_search,
            width=100
        )
        search_btn.pack(side="left", padx=5)

        # 検索対象選択
        filter_frame = ctk.CTkFrame(main_frame)
        filter_frame.pack(fill="x", pady=(0, 20))

        ctk.CTkLabel(filter_frame, text="検索対象:").pack(side="left", padx=5)

        self.search_type = ctk.StringVar(value="all")

        type_buttons = [
            ("すべて", "all"),
            ("キャラクター", "characters"),
            ("シーン", "scenes")
        ]

        for text, value in type_buttons:
            radio = ctk.CTkRadioButton(
                filter_frame,
                text=text,
                variable=self.search_type,
                value=value,
                command=self._perform_search
            )
            radio.pack(side="left", padx=10)

        # 結果表示エリア
        results_label = ctk.CTkLabel(main_frame, text="検索結果:", anchor="w")
        results_label.pack(fill="x", pady=(0, 5))

        # タブビュー
        self.result_tabs = ctk.CTkTabview(main_frame, height=350)
        self.result_tabs.pack(fill="both", expand=True, pady=(0, 20))

        # キャラクタータブ
        char_tab = self.result_tabs.add("キャラクター")
        self.char_results_frame = ctk.CTkScrollableFrame(char_tab, height=300)
        self.char_results_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # シーンタブ
        scene_tab = self.result_tabs.add("シーン")
        self.scene_results_frame = ctk.CTkScrollableFrame(scene_tab, height=300)
        self.scene_results_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # 結果カウント表示
        self.result_count_label = ctk.CTkLabel(
            main_frame,
            text="検索結果: 0件",
            anchor="w"
        )
        self.result_count_label.pack(fill="x", pady=(0, 10))

        # 閉じるボタン
        close_btn = ctk.CTkButton(
            main_frame,
            text="閉じる",
            command=self.destroy,
            width=100
        )
        close_btn.pack()

        # 初期検索（全件表示）
        self._perform_search()

    def _perform_search(self):
        """検索を実行"""
        keyword = self.search_entry.get().strip().lower()
        search_type = self.search_type.get()

        # 結果をクリア
        for widget in self.char_results_frame.winfo_children():
            widget.destroy()
        for widget in self.scene_results_frame.winfo_children():
            widget.destroy()

        char_count = 0
        scene_count = 0

        # キャラクター検索
        if search_type in ["all", "characters"]:
            characters = self.project_manager.get_characters()
            char_results = self._search_characters(characters, keyword)
            char_count = len(char_results)

            if char_results:
                for char in char_results:
                    self._create_character_result(char)
            else:
                no_result = ctk.CTkLabel(
                    self.char_results_frame,
                    text="該当するキャラクターが見つかりません",
                    text_color="gray"
                )
                no_result.pack(pady=20)

        # シーン検索
        if search_type in ["all", "scenes"]:
            scenes = self.project_manager.get_scenes()
            scene_results = self._search_scenes(scenes, keyword)
            scene_count = len(scene_results)

            if scene_results:
                for scene in scene_results:
                    self._create_scene_result(scene)
            else:
                no_result = ctk.CTkLabel(
                    self.scene_results_frame,
                    text="該当するシーンが見つかりません",
                    text_color="gray"
                )
                no_result.pack(pady=20)

        # 結果カウント更新
        total_count = char_count + scene_count
        self.result_count_label.configure(
            text=f"検索結果: {total_count}件 (キャラクター: {char_count}件, シーン: {scene_count}件)"
        )

    def _search_characters(self, characters: List[Dict[str, Any]], keyword: str) -> List[Dict[str, Any]]:
        """キャラクターを検索"""
        if not keyword:
            return characters

        results = []
        for char in characters:
            # 名前、性格、背景などで検索
            searchable_text = " ".join([
                char.get('name', ''),
                char.get('personality', ''),
                char.get('appearance', ''),
                char.get('background', ''),
                char.get('skills', ''),
                char.get('speech', ''),
                char.get('relationships', ''),
                char.get('goals', '')
            ]).lower()

            if keyword in searchable_text:
                results.append(char)

        return results

    def _search_scenes(self, scenes: List[Dict[str, Any]], keyword: str) -> List[Dict[str, Any]]:
        """シーンを検索"""
        if not keyword:
            return scenes

        results = []
        for scene in scenes:
            # タイトル、概要、内容で検索
            searchable_text = " ".join([
                scene.get('title', ''),
                scene.get('summary', ''),
                scene.get('content', '')
            ]).lower()

            if keyword in searchable_text:
                results.append(scene)

        return results

    def _create_character_result(self, character: Dict[str, Any]):
        """キャラクター検索結果を作成"""
        result_frame = ctk.CTkFrame(self.char_results_frame)
        result_frame.pack(fill="x", pady=5, padx=5)

        # 名前
        name_label = ctk.CTkLabel(
            result_frame,
            text=character.get('name', '不明'),
            font=("", 14, "bold"),
            anchor="w"
        )
        name_label.pack(fill="x", padx=10, pady=(5, 0))

        # 性格
        personality = character.get('personality', 'なし')
        personality_preview = personality[:100] + "..." if len(personality) > 100 else personality

        personality_label = ctk.CTkLabel(
            result_frame,
            text=f"性格: {personality_preview}",
            anchor="w",
            text_color="gray"
        )
        personality_label.pack(fill="x", padx=10, pady=(0, 5))

        # 選択ボタン
        select_btn = ctk.CTkButton(
            result_frame,
            text="選択",
            command=lambda c=character: self._select_character(c),
            width=80,
            height=25
        )
        select_btn.pack(anchor="e", padx=10, pady=5)

    def _create_scene_result(self, scene: Dict[str, Any]):
        """シーン検索結果を作成"""
        result_frame = ctk.CTkFrame(self.scene_results_frame)
        result_frame.pack(fill="x", pady=5, padx=5)

        # タイトル
        title_label = ctk.CTkLabel(
            result_frame,
            text=scene.get('title', '無題'),
            font=("", 14, "bold"),
            anchor="w"
        )
        title_label.pack(fill="x", padx=10, pady=(5, 0))

        # 概要
        summary = scene.get('summary', 'なし')
        summary_preview = summary[:100] + "..." if len(summary) > 100 else summary

        summary_label = ctk.CTkLabel(
            result_frame,
            text=f"概要: {summary_preview}",
            anchor="w",
            text_color="gray"
        )
        summary_label.pack(fill="x", padx=10, pady=(0, 0))

        # 文字数
        content_length = len(scene.get('content', ''))
        length_label = ctk.CTkLabel(
            result_frame,
            text=f"文字数: {content_length:,}文字",
            anchor="w",
            text_color="gray"
        )
        length_label.pack(fill="x", padx=10, pady=(0, 5))

        # 選択ボタン
        select_btn = ctk.CTkButton(
            result_frame,
            text="選択",
            command=lambda s=scene: self._select_scene(s),
            width=80,
            height=25
        )
        select_btn.pack(anchor="e", padx=10, pady=5)

    def _select_character(self, character: Dict[str, Any]):
        """キャラクターを選択"""
        if self.on_character_select:
            self.on_character_select(character)
        self.destroy()

    def _select_scene(self, scene: Dict[str, Any]):
        """シーンを選択"""
        if self.on_scene_select:
            self.on_scene_select(scene)
        self.destroy()
