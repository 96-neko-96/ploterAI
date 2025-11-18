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
        self.geometry("1400x800")

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

    def _create_menu(self):
        """メニューバーの作成"""
        # CustomTkinterはネイティブメニューバーをサポートしていないため、
        # ボタンベースのメニューを作成
        pass

    def _create_widgets(self):
        """ウィジェットの作成"""
        # トップフレーム（メニュー相当）
        top_frame = ctk.CTkFrame(self, height=50)
        top_frame.pack(fill="x", padx=10, pady=5)

        # メニューボタン
        menu_buttons = [
            ("新規プロジェクト", self._new_project),
            ("プロジェクトを開く", self._open_project),
            ("保存", self._save_project),
            ("名前を付けて保存", self._save_as_project),
            ("エクスポート", self._export),
            ("API設定", self._show_api_config),
            ("テーマ設定", self._show_theme_config),
        ]

        for text, command in menu_buttons:
            btn = ctk.CTkButton(
                top_frame,
                text=text,
                command=command,
                width=120,
                height=35
            )
            btn.pack(side="left", padx=5)

        # プロジェクト名表示
        self.project_label = ctk.CTkLabel(
            top_frame,
            text="プロジェクト: 未保存",
            font=ctk.CTkFont(size=14)
        )
        self.project_label.pack(side="right", padx=10)

        # メインコンテナ
        main_container = ctk.CTkFrame(self)
        main_container.pack(fill="both", expand=True, padx=10, pady=5)

        # 左パネル（キャラクター・世界観）
        left_panel = ctk.CTkFrame(main_container, width=300)
        left_panel.pack(side="left", fill="both", padx=(0, 5))
        left_panel.pack_propagate(False)

        self._create_left_panel(left_panel)

        # 右パネル（シーン作成・編集）
        right_panel = ctk.CTkFrame(main_container)
        right_panel.pack(side="right", fill="both", expand=True)

        self._create_right_panel(right_panel)

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
        # シーン作成エリア
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

        self.scene_overview_text = ctk.CTkTextbox(scene_frame, height=80)
        self.scene_overview_text.pack(fill="x", pady=(0, 10))

        # 使用キャラクター
        char_label = ctk.CTkLabel(scene_frame, text="使用キャラクター:", font=ctk.CTkFont(size=14))
        char_label.pack(anchor="w", pady=(0, 5))

        self.scene_characters_menu = ctk.CTkOptionMenu(scene_frame, values=["なし"])
        self.scene_characters_menu.pack(fill="x", pady=(0, 10))

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

        # 結果表示
        result_label = ctk.CTkLabel(parent, text="生成結果:", font=ctk.CTkFont(size=14))
        result_label.pack(anchor="w", padx=10, pady=(10, 5))

        self.result_text = ctk.CTkTextbox(parent, wrap="word")
        self.result_text.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    def _initialize_api(self):
        """APIの初期化"""
        api_key = self.config.get_api_key()
        if not api_key:
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
        except Exception as e:
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

        # キャラクター選択メニュー更新
        self._refresh_character_menu()

    def _refresh_character_list(self):
        """キャラクターリストを更新"""
        # 既存のウィジェットを削除
        for widget in self.character_listbox.winfo_children():
            widget.destroy()

        # キャラクターを表示
        characters = self.project_manager.get_characters()
        for char in characters:
            btn = ctk.CTkButton(
                self.character_listbox,
                text=char.get('name', '不明'),
                command=lambda c=char: self._select_character(c),
                anchor="w"
            )
            btn.pack(fill="x", pady=2)

    def _refresh_world_display(self):
        """世界観表示を更新"""
        world = self.project_manager.get_world_settings()
        self.world_text.delete("1.0", "end")

        if world:
            text = f"世界観名: {world.get('name', '不明')}\n"
            text += f"時代: {world.get('era', '不明')}\n"
            text += f"概要: {world.get('overview', '不明')}\n"
            self.world_text.insert("1.0", text)

    def _refresh_character_menu(self):
        """キャラクター選択メニューを更新"""
        characters = self.project_manager.get_characters()
        char_names = [c.get('name', '不明') for c in characters]
        if not char_names:
            char_names = ["なし"]

        self.scene_characters_menu.configure(values=char_names)
        if char_names:
            self.scene_characters_menu.set(char_names[0])

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
                self._refresh_character_menu()
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
                self._refresh_character_menu()
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
                self._refresh_character_menu()
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
                self._refresh_character_menu()
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
        """選択されたキャラクターを取得"""
        # 現在は1つのキャラクターのみ選択可能
        selected_name = self.scene_characters_menu.get()
        if selected_name == "なし":
            return []

        characters = self.project_manager.get_characters()
        for char in characters:
            if char.get('name') == selected_name:
                return [char]

        return []
