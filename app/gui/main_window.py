"""
メインウィンドウ
アプリケーションのメインGUI
"""
import customtkinter as ctk
from tkinter import messagebox, filedialog
import threading
from typing import Optional, List, Dict, Any

from app.utils.config import Config
from app.core.project_manager import ProjectManager
from app.core.gemini_client import GeminiClient
from app.core.exporter import Exporter
from app.gui.api_config_dialog import APIConfigDialog
from app.gui.style_dialog import StyleDialog
from app.gui.theme_dialog import ThemeDialog
from app.gui.new_project_dialog import NewProjectDialog
from app.gui.character_dialog import CharacterDialog, ProgressDialog
from app.gui.world_dialog import WorldDialog
from app.gui.export_dialog import ExportDialog
from app.gui.stats_dialog import StatsDialog
from app.gui.template_dialog import TemplateDialog
from app.gui.search_dialog import SearchDialog


class MainWindow(ctk.CTk):
    """メインウィンドウクラス"""

    def __init__(self):
        super().__init__()

        # 設定とマネージャーの初期化
        self.config = Config()
        self.project_manager = ProjectManager()
        self.exporter = Exporter()
        self.gemini_client: Optional[GeminiClient] = None

        # 現在の状態
        self.current_scene_content = ""

        # ウィンドウ設定
        self.title("Story Generator")
        self.geometry("1400x900")
        self.minsize(1200, 850)

        # テーマの適用
        theme = self.config.get_ui_theme()
        self._apply_theme(theme['theme_mode'], theme['color_theme'])

        # GUIの作成
        self._create_menu()
        self._create_widgets()

        # APIキーのチェック
        self._initialize_api()

        # 最後のプロジェクトを開く
        self._load_last_project()

    def _apply_theme(self, mode: str, color: str):
        """テーマを適用"""
        ctk.set_appearance_mode(mode)
        ctk.set_default_color_theme(color)

    def _create_button_group(self, parent, title, buttons):
        """ボタングループを作成"""
        group_frame = ctk.CTkFrame(parent, fg_color="transparent")
        group_frame.pack(side="left", padx=5)

        # グループタイトル
        title_label = ctk.CTkLabel(
            group_frame,
            text=title,
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=("gray50", "gray50")
        )
        title_label.pack(pady=(0, 3))

        # ボタンコンテナ
        button_container = ctk.CTkFrame(group_frame, fg_color="transparent")
        button_container.pack()

        for text, command, color in buttons:
            btn = ctk.CTkButton(
                button_container,
                text=text,
                command=command,
                width=140,
                height=32,
                corner_radius=6,
                fg_color=color,
                hover_color=self._darken_color(color),
                font=ctk.CTkFont(size=12)
            )
            btn.pack(side="left", padx=2)

    def _darken_color(self, color):
        """色を暗くする（簡易版）"""
        color_map = {
            "#2e7d32": "#1b5e20",
            "#1565c0": "#0d47a1",
            "#6a1b9a": "#4a148c",
            "#c62828": "#b71c1c",
            "#f57c00": "#e65100",
            "#00838f": "#006064",
            "#5e35b1": "#4527a0",
            "#37474f": "#263238",
            "#455a64": "#37474f",
        }
        return color_map.get(color, color)

    def _create_menu(self):
        """メニューバーの作成"""
        # CustomTkinterはネイティブメニューバーをサポートしていないため、
        # ボタンベースのメニューを作成
        pass

    def _create_widgets(self):
        """ウィジェットの作成"""
        # ========== ヘッダーバー ==========
        header_frame = ctk.CTkFrame(self, height=60, corner_radius=0)
        header_frame.pack(fill="x", padx=0, pady=0)
        header_frame.pack_propagate(False)

        # アプリタイトル
        title_label = ctk.CTkLabel(
            header_frame,
            text="📖 Story Generator",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=("#1f538d", "#3a7ebf")
        )
        title_label.pack(side="left", padx=20, pady=10)

        # プロジェクト名表示
        self.project_label = ctk.CTkLabel(
            header_frame,
            text="プロジェクト: 未保存",
            font=ctk.CTkFont(size=14),
            text_color=("gray30", "gray70")
        )
        self.project_label.pack(side="right", padx=20)

        # ========== ツールバー ==========
        toolbar_frame = ctk.CTkFrame(self, height=100, corner_radius=0)
        toolbar_frame.pack(fill="x", padx=0, pady=0)
        toolbar_frame.pack_propagate(False)

        # ツールバースクロールエリア
        toolbar_scroll = ctk.CTkScrollableFrame(
            toolbar_frame,
            orientation="horizontal",
            height=85,
            fg_color="transparent"
        )
        toolbar_scroll.pack(fill="both", expand=True, padx=10, pady=5)

        # ボタングループ1: プロジェクト
        project_buttons = [
            ("📝 新規", self._new_project, "#2e7d32"),
            ("📂 開く", self._open_project, "#1565c0"),
            ("💾 保存", self._save_project, "#6a1b9a"),
            ("💾 名前保存", self._save_as_project, "#6a1b9a"),
        ]
        self._create_button_group(toolbar_scroll, "プロジェクト", project_buttons)

        # ボタングループ2: ツール
        tool_buttons = [
            ("📤 エクスポート", self._export, "#00838f"),
            ("🔍 検索", self._show_search, "#f57c00"),
            ("📊 統計", self._show_stats, "#f57c00"),
            ("📋 テンプレート", self._show_templates, "#f57c00"),
        ]
        self._create_button_group(toolbar_scroll, "ツール", tool_buttons)

        # ボタングループ3: 設定
        setting_buttons = [
            ("⚙️ API設定", self._show_api_config, "#455a64"),
            ("🎨 テーマ", self._show_theme_config, "#5e35b1"),
        ]
        self._create_button_group(toolbar_scroll, "設定", setting_buttons)

        # ========== メインコンテナ ==========
        main_container = ctk.CTkFrame(self)
        main_container.pack(fill="both", expand=True, padx=10, pady=5)

        # 左パネル（キャラクター・世界観）
        left_panel = ctk.CTkFrame(main_container, width=300)
        left_panel.pack(side="left", fill="both", padx=(0, 5))
        left_panel.pack_propagate(False)

        self._create_left_panel(left_panel)

        # 右パネル（シーン作成・編集）- スクロール対応
        right_panel_container = ctk.CTkFrame(main_container, fg_color="transparent")
        right_panel_container.pack(side="right", fill="both", expand=True)

        right_panel = ctk.CTkScrollableFrame(
            right_panel_container,
            fg_color="transparent"
        )
        right_panel.pack(fill="both", expand=True)

        self._create_right_panel(right_panel)

        # ========== ステータスバー ==========
        status_frame = ctk.CTkFrame(self, height=30, corner_radius=0)
        status_frame.pack(fill="x", side="bottom", padx=0, pady=0)
        status_frame.pack_propagate(False)

        # API接続状態
        self.api_status_label = ctk.CTkLabel(
            status_frame,
            text="● API: 未接続",
            font=ctk.CTkFont(size=11),
            text_color=("gray40", "gray60")
        )
        self.api_status_label.pack(side="left", padx=10)

        # ステータスメッセージ
        self.status_message_label = ctk.CTkLabel(
            status_frame,
            text="準備完了",
            font=ctk.CTkFont(size=11),
            text_color=("gray40", "gray60")
        )
        self.status_message_label.pack(side="right", padx=10)

    def _create_left_panel(self, parent):
        """左パネルの作成"""
        # タブビュー
        self.tabview = ctk.CTkTabview(parent)
        self.tabview.pack(fill="both", expand=True, padx=5, pady=5)

        # キャラクタータブ
        self.char_tab = self.tabview.add("キャラクター")
        self._create_character_tab(self.char_tab)

        # 世界観タブ
        self.world_tab = self.tabview.add("世界観")
        self._create_world_tab(self.world_tab)

    def _create_character_tab(self, parent):
        """キャラクタータブの作成"""
        # ボタンフレーム
        button_frame = ctk.CTkFrame(parent, fg_color="transparent")
        button_frame.pack(fill="x", pady=(0, 5))

        add_btn = ctk.CTkButton(
            button_frame,
            text="新規作成",
            command=self._add_character,
            width=80
        )
        add_btn.pack(side="left", padx=(0, 5))

        ai_btn = ctk.CTkButton(
            button_frame,
            text="AI生成",
            command=self._generate_character,
            width=80
        )
        ai_btn.pack(side="left")

        # キャラクターリスト
        self.character_listbox = ctk.CTkScrollableFrame(parent)
        self.character_listbox.pack(fill="both", expand=True, pady=(0, 5))

        # 操作ボタン
        action_frame = ctk.CTkFrame(parent, fg_color="transparent")
        action_frame.pack(fill="x")

        edit_btn = ctk.CTkButton(
            action_frame,
            text="編集",
            command=self._edit_character,
            width=80
        )
        edit_btn.pack(side="left", padx=(0, 5))

        delete_btn = ctk.CTkButton(
            action_frame,
            text="削除",
            command=self._delete_character,
            fg_color="red",
            width=80
        )
        delete_btn.pack(side="left")

        # 選択されたキャラクター
        self.selected_character_id = None

    def _create_world_tab(self, parent):
        """世界観タブの作成"""
        # ボタンフレーム
        button_frame = ctk.CTkFrame(parent, fg_color="transparent")
        button_frame.pack(fill="x", pady=(0, 5))

        manual_btn = ctk.CTkButton(
            button_frame,
            text="手動作成",
            command=self._create_world_manual,
            width=100
        )
        manual_btn.pack(side="left", padx=(0, 5))

        ai_btn = ctk.CTkButton(
            button_frame,
            text="AI生成",
            command=self._generate_world,
            width=100
        )
        ai_btn.pack(side="left")

        # 世界観情報表示
        self.world_text = ctk.CTkTextbox(parent, wrap="word")
        self.world_text.pack(fill="both", expand=True)

    def _create_right_panel(self, parent):
        """右パネルの作成"""
        # 上下分割
        # 上部: シーン作成・編集エリア
        # 下部: シーン一覧と生成結果

        # 上部フレーム（シーン作成エリア）
        scene_frame = ctk.CTkFrame(parent)
        scene_frame.pack(fill="x", padx=10, pady=10)

        # ボタン
        button_frame = ctk.CTkFrame(scene_frame, fg_color="transparent")
        button_frame.pack(fill="x", pady=(0, 10))

        ctk.CTkButton(
            button_frame,
            text="新規シーン",
            command=self._new_scene,
            width=100
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            button_frame,
            text="シーン保存",
            command=self._save_scene,
            width=100
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            button_frame,
            text="文体設定",
            command=self._show_style_dialog,
            width=100
        ).pack(side="left", padx=5)

        # シーンタイトル
        title_label = ctk.CTkLabel(scene_frame, text="シーンタイトル:", font=ctk.CTkFont(size=14))
        title_label.pack(anchor="w", pady=(0, 5))

        self.scene_title_entry = ctk.CTkEntry(scene_frame, width=600)
        self.scene_title_entry.pack(fill="x", pady=(0, 10))

        # シーン概要
        overview_label = ctk.CTkLabel(scene_frame, text="シーン概要:", font=ctk.CTkFont(size=14))
        overview_label.pack(anchor="w", pady=(0, 5))

        self.scene_overview_text = ctk.CTkTextbox(scene_frame, height=60)
        self.scene_overview_text.pack(fill="x", pady=(0, 10))

        # 使用キャラクター（複数選択対応）
        char_label = ctk.CTkLabel(scene_frame, text="使用キャラクター（複数選択可）:", font=ctk.CTkFont(size=14))
        char_label.pack(anchor="w", pady=(0, 5))

        # キャラクター選択フレーム
        self.char_selection_frame = ctk.CTkScrollableFrame(scene_frame, height=80)
        self.char_selection_frame.pack(fill="x", pady=(0, 10))

        self.character_checkboxes = []

        # 生成ボタン
        generate_frame = ctk.CTkFrame(scene_frame, fg_color="transparent")
        generate_frame.pack(fill="x", pady=10)

        ctk.CTkButton(
            generate_frame,
            text="プロット生成",
            command=self._generate_plot,
            width=130
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            generate_frame,
            text="中編化",
            command=self._expand_to_medium,
            width=130
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            generate_frame,
            text="長編化",
            command=self._expand_to_long,
            width=130
        ).pack(side="left", padx=5)

        # 下部フレーム（タブビュー：シーン一覧と生成結果）
        bottom_tabview = ctk.CTkTabview(parent)
        bottom_tabview.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # 生成結果タブ
        result_tab = bottom_tabview.add("生成結果")
        self.result_text = ctk.CTkTextbox(result_tab, wrap="word")
        self.result_text.pack(fill="both", expand=True, padx=5, pady=5)

        # シーン一覧タブ
        scenes_tab = bottom_tabview.add("シーン一覧")

        # シーン一覧操作ボタン
        scene_button_frame = ctk.CTkFrame(scenes_tab, fg_color="transparent")
        scene_button_frame.pack(fill="x", pady=(0, 5))

        ctk.CTkButton(
            scene_button_frame,
            text="読み込み",
            command=self._load_selected_scene,
            width=100
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            scene_button_frame,
            text="削除",
            command=self._delete_selected_scene,
            fg_color="red",
            width=100
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            scene_button_frame,
            text="更新",
            command=self._refresh_scene_list,
            width=100
        ).pack(side="left", padx=5)

        # シーン一覧
        self.scene_listbox = ctk.CTkScrollableFrame(scenes_tab)
        self.scene_listbox.pack(fill="both", expand=True, padx=5, pady=5)

        self.selected_scene_id = None

    def _initialize_api(self):
        """APIの初期化"""
        api_key = self.config.get_api_key()
        if not api_key:
            self.api_status_label.configure(text="● API: 未接続", text_color="red")
            messagebox.showwarning(
                "API設定",
                "Gemini APIキーが設定されていません。\n「API設定」メニューから設定してください。"
            )
            return

        try:
            api_config = self.config.get_api_config()
            self.gemini_client = GeminiClient(
                api_key=api_key,
                model=api_config.get('model', 'gemini-2.0-flash')
            )
            self.gemini_client.update_generation_config(
                temperature=api_config.get('temperature', 0.7),
                max_tokens=api_config.get('max_tokens', 4000),
                top_p=api_config.get('top_p', 0.9)
            )
            self.api_status_label.configure(text="● API: 接続済み", text_color="green")
        except Exception as e:
            self.api_status_label.configure(text="● API: エラー", text_color="red")
            messagebox.showerror("エラー", f"API初期化に失敗しました: {str(e)}")

    def _load_last_project(self):
        """最後のプロジェクトを読み込み"""
        last_project = self.config.get_last_project()
        if last_project:
            try:
                self.project_manager.load_project(last_project)
                self._update_ui_from_project()
            except Exception:
                pass  # 失敗しても続行

    def _new_project(self):
        """新規プロジェクト"""
        dialog = NewProjectDialog(self)
        self.wait_window(dialog)

        if dialog.result:
            try:
                self.project_manager.create_new_project(
                    dialog.result['name'],
                    dialog.result['path']
                )
                self.config.set_last_project(dialog.result['path'])
                self._update_ui_from_project()
                messagebox.showinfo("成功", "プロジェクトを作成しました")
            except Exception as e:
                messagebox.showerror("エラー", f"プロジェクト作成に失敗しました: {str(e)}")

    def _open_project(self):
        """プロジェクトを開く"""
        file_path = filedialog.askopenfilename(
            title="プロジェクトを開く",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )

        if file_path:
            try:
                self.project_manager.load_project(file_path)
                self.config.set_last_project(file_path)
                self._update_ui_from_project()
                messagebox.showinfo("成功", "プロジェクトを開きました")
            except Exception as e:
                messagebox.showerror("エラー", f"プロジェクトを開けませんでした: {str(e)}")

    def _save_project(self):
        """プロジェクトを保存"""
        try:
            self.project_manager.save_project()
            messagebox.showinfo("成功", "プロジェクトを保存しました")
        except Exception as e:
            messagebox.showerror("エラー", f"保存に失敗しました: {str(e)}")

    def _save_as_project(self):
        """名前を付けて保存"""
        file_path = filedialog.asksaveasfilename(
            title="名前を付けて保存",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )

        if file_path:
            try:
                self.project_manager.save_project(file_path)
                self.config.set_last_project(file_path)
                self._update_ui_from_project()
                messagebox.showinfo("成功", "プロジェクトを保存しました")
            except Exception as e:
                messagebox.showerror("エラー", f"保存に失敗しました: {str(e)}")

    def _export(self):
        """エクスポート"""
        if not self.project_manager.current_project:
            messagebox.showwarning("警告", "プロジェクトを開いてください")
            return

        scenes = self.project_manager.get_scenes()
        if not scenes:
            messagebox.showwarning("警告", "エクスポートするシーンがありません")
            return

        dialog = ExportDialog(
            self,
            scenes,
            self.project_manager.get_characters(),
            self.project_manager.get_world_settings(),
            self.project_manager.get_project_name()
        )
        self.wait_window(dialog)

        if dialog.result:
            try:
                export_data = dialog.result

                if export_data['format'] == 'txt':
                    self.exporter.export_to_txt(**export_data)
                elif export_data['format'] == 'markdown':
                    self.exporter.export_to_markdown(**export_data)
                else:  # pdf
                    self.exporter.export_to_pdf(**export_data)

                messagebox.showinfo("成功", "エクスポートが完了しました")
            except Exception as e:
                messagebox.showerror("エラー", f"エクスポートに失敗しました: {str(e)}")

    def _show_search(self):
        """検索ダイアログを表示"""
        if not self.project_manager.current_project:
            messagebox.showwarning("警告", "プロジェクトを開いてください")
            return

        dialog = SearchDialog(
            self,
            self.project_manager,
            self._select_character,
            self._load_scene_from_search
        )
        self.wait_window(dialog)

    def _show_stats(self):
        """統計情報を表示"""
        if not self.project_manager.current_project:
            messagebox.showwarning("警告", "プロジェクトを開いてください")
            return

        dialog = StatsDialog(self, self.project_manager.current_project)
        self.wait_window(dialog)

    def _show_templates(self):
        """テンプレート管理ダイアログを表示"""
        if not self.project_manager.current_project:
            messagebox.showwarning("警告", "プロジェクトを開いてください")
            return

        current_style = self.project_manager.get_writing_style()
        dialog = TemplateDialog(self, current_style, self._apply_template_style)
        self.wait_window(dialog)

    def _apply_template_style(self, style: Dict[str, Any]):
        """テンプレートからスタイルを適用"""
        try:
            self.project_manager.set_writing_style(style)
        except Exception as e:
            messagebox.showerror("エラー", f"スタイルの適用に失敗しました: {str(e)}")

    def _show_api_config(self):
        """API設定ダイアログを表示"""
        dialog = APIConfigDialog(
            self,
            self.config,
            test_connection_callback=self._test_api_connection
        )
        self.wait_window(dialog)

        if dialog.result:
            self._initialize_api()

    def _show_theme_config(self):
        """テーマ設定ダイアログを表示"""
        dialog = ThemeDialog(self, self.config, self._apply_theme)
        self.wait_window(dialog)

    def _show_style_dialog(self):
        """文体設定ダイアログを表示"""
        if not self.project_manager.current_project:
            messagebox.showwarning("警告", "プロジェクトを開いてください")
            return

        current_style = self.project_manager.get_writing_style()
        dialog = StyleDialog(self, current_style)
        self.wait_window(dialog)

        if dialog.result:
            try:
                self.project_manager.set_writing_style(dialog.result)
                messagebox.showinfo("成功", "文体スタイルを設定しました")
            except Exception as e:
                messagebox.showerror("エラー", f"設定に失敗しました: {str(e)}")

    def _test_api_connection(self, api_key: str, model: str) -> bool:
        """API接続テスト"""
        try:
            client = GeminiClient(api_key=api_key, model=model)
            return client.test_connection()
        except Exception:
            return False

    def _update_ui_from_project(self):
        """プロジェクトからUIを更新"""
        # プロジェクト名表示
        project_name = self.project_manager.get_project_name()
        self.project_label.configure(text=f"プロジェクト: {project_name}")

        # キャラクターリスト更新
        self._refresh_character_list()

        # 世界観表示
        self._refresh_world_display()

        # キャラクター選択チェックボックス更新
        self._refresh_character_checkboxes()

        # シーン一覧更新
        self._refresh_scene_list()

    def _refresh_character_list(self):
        """キャラクターリストを更新（カード型）"""
        # 既存のウィジェットを削除
        for widget in self.character_listbox.winfo_children():
            widget.destroy()

        # キャラクターを表示
        characters = self.project_manager.get_characters()
        if not characters:
            label = ctk.CTkLabel(
                self.character_listbox,
                text="キャラクターがありません",
                text_color="gray"
            )
            label.pack(pady=20)
            return

        for char in characters:
            # カードフレーム
            card = ctk.CTkFrame(
                self.character_listbox,
                fg_color=("gray90", "gray25"),
                corner_radius=8
            )
            card.pack(fill="x", pady=4, padx=5)

            # 選択ボタン
            name = char.get('name', '不明')
            btn = ctk.CTkButton(
                card,
                text=f"👤 {name}",
                command=lambda c=char: self._select_character(c),
                anchor="w",
                fg_color="transparent",
                hover_color=("gray85", "gray30"),
                text_color=("gray10", "gray90"),
                font=ctk.CTkFont(size=13, weight="bold")
            )
            btn.pack(fill="x", padx=8, pady=8)

    def _refresh_world_display(self):
        """世界観表示を更新"""
        world = self.project_manager.get_world_settings()
        self.world_text.delete("1.0", "end")

        if world:
            text = f"世界観名: {world.get('name', '不明')}\n"
            text += f"時代: {world.get('era', '不明')}\n"
            text += f"概要: {world.get('overview', '不明')}\n"
            self.world_text.insert("1.0", text)

    def _refresh_character_checkboxes(self):
        """キャラクター選択チェックボックスを更新"""
        # 既存のチェックボックスを削除
        for widget in self.char_selection_frame.winfo_children():
            widget.destroy()

        self.character_checkboxes = []

        # キャラクターのチェックボックスを作成
        characters = self.project_manager.get_characters()
        if not characters:
            label = ctk.CTkLabel(
                self.char_selection_frame,
                text="キャラクターがありません",
                text_color="gray"
            )
            label.pack(pady=10)
        else:
            for char in characters:
                var = ctk.BooleanVar(value=False)
                checkbox = ctk.CTkCheckBox(
                    self.char_selection_frame,
                    text=char.get('name', '不明'),
                    variable=var
                )
                checkbox.pack(anchor="w", pady=2, padx=5)
                self.character_checkboxes.append((char, var))

    def _refresh_scene_list(self):
        """シーン一覧を更新（カード型）"""
        # 既存のウィジェットを削除
        for widget in self.scene_listbox.winfo_children():
            widget.destroy()

        # シーンを表示
        scenes = self.project_manager.get_scenes()
        if not scenes:
            label = ctk.CTkLabel(
                self.scene_listbox,
                text="シーンがありません",
                text_color="gray"
            )
            label.pack(pady=20)
        else:
            for scene in scenes:
                # カードフレーム
                card = ctk.CTkFrame(
                    self.scene_listbox,
                    fg_color=("gray90", "gray25"),
                    corner_radius=8
                )
                card.pack(fill="x", pady=4, padx=5)

                # シーンタイトル
                title = scene.get('title', '無題')
                btn = ctk.CTkButton(
                    card,
                    text=f"📄 {title}",
                    command=lambda s=scene: self._select_scene(s),
                    anchor="w",
                    fg_color="transparent",
                    hover_color=("gray85", "gray30"),
                    text_color=("gray10", "gray90"),
                    font=ctk.CTkFont(size=13, weight="bold")
                )
                btn.pack(fill="x", padx=8, pady=(8, 2))

                # 文字数表示
                content_length = len(scene.get('content', ''))
                info_label = ctk.CTkLabel(
                    card,
                    text=f"文字数: {content_length:,}",
                    font=ctk.CTkFont(size=10),
                    text_color=("gray50", "gray50"),
                    anchor="w"
                )
                info_label.pack(fill="x", padx=8, pady=(0, 8))

    def _select_scene(self, scene):
        """シーンを選択"""
        self.selected_scene_id = scene.get('id')

    def _load_selected_scene(self):
        """選択されたシーンを読み込み"""
        if not self.selected_scene_id:
            messagebox.showwarning("警告", "読み込むシーンを選択してください")
            return

        scene = self.project_manager.get_scene_by_id(self.selected_scene_id)
        if not scene:
            messagebox.showerror("エラー", "シーンが見つかりません")
            return

        # シーン情報をフォームに読み込み
        self.scene_title_entry.delete(0, "end")
        self.scene_title_entry.insert(0, scene.get('title', ''))

        self.scene_overview_text.delete("1.0", "end")
        self.scene_overview_text.insert("1.0", scene.get('overview', ''))

        self.result_text.delete("1.0", "end")
        self.result_text.insert("1.0", scene.get('content', ''))

        self.current_scene_content = scene.get('content', '')

        messagebox.showinfo("成功", "シーンを読み込みました")

    def _delete_selected_scene(self):
        """選択されたシーンを削除"""
        if not self.selected_scene_id:
            messagebox.showwarning("警告", "削除するシーンを選択してください")
            return

        if messagebox.askyesno("確認", "本当にこのシーンを削除しますか？"):
            try:
                self.project_manager.delete_scene(self.selected_scene_id)
                self.selected_scene_id = None
                self._refresh_scene_list()
                messagebox.showinfo("成功", "シーンを削除しました")
            except Exception as e:
                messagebox.showerror("エラー", f"削除に失敗しました: {str(e)}")

    def _load_scene_from_search(self, scene: Dict[str, Any]):
        """検索結果からシーンを読み込み"""
        # シーン情報をフォームに読み込み
        self.scene_title_entry.delete(0, "end")
        self.scene_title_entry.insert(0, scene.get('title', ''))

        self.scene_overview_text.delete("1.0", "end")
        self.scene_overview_text.insert("1.0", scene.get('summary', ''))

        self.result_text.delete("1.0", "end")
        self.result_text.insert("1.0", scene.get('content', ''))

        self.current_scene_content = scene.get('content', '')

        messagebox.showinfo("成功", f"シーン「{scene.get('title', '無題')}」を読み込みました")

    def _select_character(self, character):
        """キャラクターを選択"""
        self.selected_character_id = character.get('id')

    def _add_character(self):
        """キャラクターを追加"""
        if not self.project_manager.current_project:
            messagebox.showwarning("警告", "プロジェクトを開いてください")
            return

        dialog = CharacterDialog(self)
        self.wait_window(dialog)

        if dialog.result:
            try:
                self.project_manager.add_character(dialog.result)
                self._refresh_character_list()
                self._refresh_character_checkboxes()
                messagebox.showinfo("成功", "キャラクターを追加しました")
            except Exception as e:
                messagebox.showerror("エラー", f"追加に失敗しました: {str(e)}")

    def _generate_character(self):
        """AIでキャラクターを生成"""
        if not self.project_manager.current_project:
            messagebox.showwarning("警告", "プロジェクトを開いてください")
            return

        if not self.gemini_client:
            messagebox.showwarning("警告", "APIが初期化されていません")
            return

        dialog = CharacterDialog(
            self,
            ai_generate_callback=self.gemini_client.generate_character
        )
        self.wait_window(dialog)

        if dialog.result:
            try:
                self.project_manager.add_character(dialog.result)
                self._refresh_character_list()
                self._refresh_character_checkboxes()
                messagebox.showinfo("成功", "キャラクターを追加しました")
            except Exception as e:
                messagebox.showerror("エラー", f"追加に失敗しました: {str(e)}")

    def _edit_character(self):
        """キャラクターを編集"""
        if not self.selected_character_id:
            messagebox.showwarning("警告", "編集するキャラクターを選択してください")
            return

        character = self.project_manager.get_character_by_id(self.selected_character_id)
        if not character:
            messagebox.showerror("エラー", "キャラクターが見つかりません")
            return

        dialog = CharacterDialog(self, character_data=character)
        self.wait_window(dialog)

        if dialog.result:
            try:
                self.project_manager.update_character(self.selected_character_id, dialog.result)
                self._refresh_character_list()
                self._refresh_character_checkboxes()
                messagebox.showinfo("成功", "キャラクターを更新しました")
            except Exception as e:
                messagebox.showerror("エラー", f"更新に失敗しました: {str(e)}")

    def _delete_character(self):
        """キャラクターを削除"""
        if not self.selected_character_id:
            messagebox.showwarning("警告", "削除するキャラクターを選択してください")
            return

        if messagebox.askyesno("確認", "本当に削除しますか?"):
            try:
                self.project_manager.delete_character(self.selected_character_id)
                self.selected_character_id = None
                self._refresh_character_list()
                self._refresh_character_checkboxes()
                messagebox.showinfo("成功", "キャラクターを削除しました")
            except Exception as e:
                messagebox.showerror("エラー", f"削除に失敗しました: {str(e)}")

    def _create_world_manual(self):
        """手動で世界観を作成"""
        if not self.project_manager.current_project:
            messagebox.showwarning("警告", "プロジェクトを開いてください")
            return

        world = self.project_manager.get_world_settings()
        dialog = WorldDialog(self, world_data=world if world else None)
        self.wait_window(dialog)

        if dialog.result:
            try:
                self.project_manager.set_world_settings(dialog.result)
                self._refresh_world_display()
                messagebox.showinfo("成功", "世界観を設定しました")
            except Exception as e:
                messagebox.showerror("エラー", f"設定に失敗しました: {str(e)}")

    def _generate_world(self):
        """AIで世界観を生成"""
        if not self.project_manager.current_project:
            messagebox.showwarning("警告", "プロジェクトを開いてください")
            return

        if not self.gemini_client:
            messagebox.showwarning("警告", "APIが初期化されていません")
            return

        dialog = WorldDialog(
            self,
            ai_generate_callback=self.gemini_client.generate_world
        )
        self.wait_window(dialog)

        if dialog.result:
            try:
                self.project_manager.set_world_settings(dialog.result)
                self._refresh_world_display()
                messagebox.showinfo("成功", "世界観を設定しました")
            except Exception as e:
                messagebox.showerror("エラー", f"設定に失敗しました: {str(e)}")

    def _new_scene(self):
        """新規シーン"""
        self.scene_title_entry.delete(0, "end")
        self.scene_overview_text.delete("1.0", "end")
        self.result_text.delete("1.0", "end")
        self.current_scene_content = ""

    def _save_scene(self):
        """シーンを保存"""
        if not self.project_manager.current_project:
            messagebox.showwarning("警告", "プロジェクトを開いてください")
            return

        title = self.scene_title_entry.get().strip()
        content = self.result_text.get("1.0", "end-1c").strip()

        if not title or not content:
            messagebox.showwarning("警告", "タイトルと内容を入力してください")
            return

        scene_data = {
            'title': title,
            'overview': self.scene_overview_text.get("1.0", "end-1c").strip(),
            'content': content
        }

        try:
            self.project_manager.add_scene(scene_data)
            messagebox.showinfo("成功", "シーンを保存しました")
        except Exception as e:
            messagebox.showerror("エラー", f"保存に失敗しました: {str(e)}")

    def _generate_plot(self):
        """プロット生成"""
        if not self.gemini_client:
            messagebox.showwarning("警告", "APIが初期化されていません")
            return

        title = self.scene_title_entry.get().strip()
        overview = self.scene_overview_text.get("1.0", "end-1c").strip()

        if not title or not overview:
            messagebox.showwarning("警告", "タイトルと概要を入力してください")
            return

        # キャラクター取得
        characters = self._get_selected_characters()
        world_settings = self.project_manager.get_world_settings()
        writing_style = self.project_manager.get_writing_style()

        progress_dialog = ProgressDialog(self, "プロットを生成中...")

        def generate_thread():
            try:
                result = self.gemini_client.generate_plot(
                    title=title,
                    overview=overview,
                    characters=characters,
                    world_setting=world_settings,
                    writing_style=writing_style
                )
                self.current_scene_content = result
                self.result_text.delete("1.0", "end")
                self.result_text.insert("1.0", result)
                progress_dialog.close()
            except Exception as e:
                progress_dialog.close()
                messagebox.showerror("エラー", f"生成に失敗しました: {str(e)}")

        thread = threading.Thread(target=generate_thread, daemon=True)
        thread.start()
        progress_dialog.show()

    def _expand_to_medium(self):
        """中編化"""
        if not self.gemini_client:
            messagebox.showwarning("警告", "APIが初期化されていません")
            return

        content = self.result_text.get("1.0", "end-1c").strip()
        if not content:
            messagebox.showwarning("警告", "生成結果がありません")
            return

        title = self.scene_title_entry.get().strip()
        characters = self._get_selected_characters()
        world_settings = self.project_manager.get_world_settings()
        writing_style = self.project_manager.get_writing_style()

        progress_dialog = ProgressDialog(self, "中編化中...")

        def expand_thread():
            try:
                result = self.gemini_client.expand_to_medium(
                    plot=content,
                    title=title,
                    characters=characters,
                    world_setting=world_settings,
                    writing_style=writing_style
                )
                self.current_scene_content = result
                self.result_text.delete("1.0", "end")
                self.result_text.insert("1.0", result)
                progress_dialog.close()
            except Exception as e:
                progress_dialog.close()
                messagebox.showerror("エラー", f"中編化に失敗しました: {str(e)}")

        thread = threading.Thread(target=expand_thread, daemon=True)
        thread.start()
        progress_dialog.show()

    def _expand_to_long(self):
        """長編化"""
        if not self.gemini_client:
            messagebox.showwarning("警告", "APIが初期化されていません")
            return

        content = self.result_text.get("1.0", "end-1c").strip()
        if not content:
            messagebox.showwarning("警告", "生成結果がありません")
            return

        title = self.scene_title_entry.get().strip()
        characters = self._get_selected_characters()
        world_settings = self.project_manager.get_world_settings()
        writing_style = self.project_manager.get_writing_style()

        progress_dialog = ProgressDialog(self, "長編化中...")

        def expand_thread():
            try:
                result = self.gemini_client.expand_to_long(
                    medium_story=content,
                    title=title,
                    characters=characters,
                    world_setting=world_settings,
                    writing_style=writing_style
                )
                self.current_scene_content = result
                self.result_text.delete("1.0", "end")
                self.result_text.insert("1.0", result)
                progress_dialog.close()
            except Exception as e:
                progress_dialog.close()
                messagebox.showerror("エラー", f"長編化に失敗しました: {str(e)}")

        thread = threading.Thread(target=expand_thread, daemon=True)
        thread.start()
        progress_dialog.show()

    def _get_selected_characters(self) -> List[Dict[str, Any]]:
        """選択されたキャラクターを取得（複数選択対応）"""
        selected_characters = []

        for char, var in self.character_checkboxes:
            if var.get():  # チェックボックスがオンの場合
                selected_characters.append(char)

        return selected_characters
