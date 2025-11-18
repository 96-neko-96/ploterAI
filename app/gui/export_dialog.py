"""
エクスポートダイアログ
シーンやプロジェクトのエクスポート設定を管理
"""
import customtkinter as ctk
from tkinter import filedialog, messagebox
from typing import List, Dict, Any


class ExportDialog(ctk.CTkToplevel):
    """エクスポートダイアログ"""

    def __init__(
        self,
        parent,
        scenes: List[Dict[str, Any]],
        characters: List[Dict[str, str]],
        world_settings: Dict[str, str],
        project_name: str
    ):
        super().__init__(parent)

        self.scenes = scenes
        self.characters = characters
        self.world_settings = world_settings
        self.project_name = project_name
        self.result = None

        self.title("エクスポート")
        self.geometry("700x650")
        self.minsize(600, 550)  # 最小サイズを設定
        self.resizable(True, True)  # リサイズ可能に

        # モーダルにする
        self.transient(parent)
        self.grab_set()

        self._create_widgets()

        # ウィンドウを中央に配置
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (700 // 2)
        y = (self.winfo_screenheight() // 2) - (650 // 2)
        self.geometry(f"+{x}+{y}")

    def _create_widgets(self):
        """ウィジェットの作成"""
        # メインフレーム
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # タイトル
        title_label = ctk.CTkLabel(
            main_frame,
            text="エクスポート設定",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.pack(pady=(0, 20))

        # ファイル形式
        format_label = ctk.CTkLabel(
            main_frame,
            text="ファイル形式:",
            font=ctk.CTkFont(size=14)
        )
        format_label.pack(anchor="w", pady=(0, 5))

        self.format_var = ctk.StringVar(value="txt")
        format_menu = ctk.CTkOptionMenu(
            main_frame,
            width=500,
            values=["txt", "markdown", "pdf"],
            variable=self.format_var
        )
        format_menu.pack(pady=(0, 15))

        # シーン選択
        scenes_label = ctk.CTkLabel(
            main_frame,
            text="エクスポートするシーン:",
            font=ctk.CTkFont(size=14)
        )
        scenes_label.pack(anchor="w", pady=(0, 5))

        # シーンリスト
        scenes_frame = ctk.CTkScrollableFrame(main_frame, width=480, height=150)
        scenes_frame.pack(pady=(0, 15))

        self.scene_checkboxes = []
        for scene in self.scenes:
            var = ctk.BooleanVar(value=True)
            checkbox = ctk.CTkCheckBox(
                scenes_frame,
                text=scene.get('title', '無題'),
                variable=var
            )
            checkbox.pack(anchor="w", pady=2)
            self.scene_checkboxes.append((scene, var))

        # 含める内容
        include_label = ctk.CTkLabel(
            main_frame,
            text="含める内容:",
            font=ctk.CTkFont(size=14)
        )
        include_label.pack(anchor="w", pady=(0, 5))

        include_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        include_frame.pack(fill="x", pady=(0, 15))

        self.include_title_var = ctk.BooleanVar(value=True)
        title_checkbox = ctk.CTkCheckBox(
            include_frame,
            text="タイトル",
            variable=self.include_title_var
        )
        title_checkbox.pack(anchor="w", pady=2)

        self.include_characters_var = ctk.BooleanVar(value=False)
        characters_checkbox = ctk.CTkCheckBox(
            include_frame,
            text="キャラクター情報",
            variable=self.include_characters_var
        )
        characters_checkbox.pack(anchor="w", pady=2)

        self.include_world_var = ctk.BooleanVar(value=False)
        world_checkbox = ctk.CTkCheckBox(
            include_frame,
            text="世界観設定",
            variable=self.include_world_var
        )
        world_checkbox.pack(anchor="w", pady=2)

        # ボタン
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(fill="x", pady=(10, 0))

        cancel_button = ctk.CTkButton(
            button_frame,
            text="キャンセル",
            command=self._cancel,
            fg_color="gray",
            width=120
        )
        cancel_button.pack(side="left")

        export_button = ctk.CTkButton(
            button_frame,
            text="エクスポート",
            command=self._export,
            width=120
        )
        export_button.pack(side="right")

    def _export(self):
        """エクスポート"""
        # 選択されたシーン
        selected_scenes = []
        for scene, var in self.scene_checkboxes:
            if var.get():
                selected_scenes.append(scene)

        if not selected_scenes:
            messagebox.showerror("エラー", "エクスポートするシーンを選択してください")
            return

        # ファイル保存ダイアログ
        format_type = self.format_var.get()

        if format_type == "txt":
            file_types = [("Text files", "*.txt"), ("All files", "*.*")]
            default_ext = ".txt"
        elif format_type == "markdown":
            file_types = [("Markdown files", "*.md"), ("All files", "*.*")]
            default_ext = ".md"
        else:  # pdf
            file_types = [("PDF files", "*.pdf"), ("All files", "*.*")]
            default_ext = ".pdf"

        file_path = filedialog.asksaveasfilename(
            title="エクスポート先を選択",
            defaultextension=default_ext,
            filetypes=file_types,
            initialfile=self.project_name
        )

        if not file_path:
            return

        # エクスポート設定
        self.result = {
            'file_path': file_path,
            'format': format_type,
            'scenes': selected_scenes,
            'include_title': self.include_title_var.get(),
            'include_characters': self.include_characters_var.get(),
            'include_world': self.include_world_var.get(),
            'characters': self.characters if self.include_characters_var.get() else None,
            'world_settings': self.world_settings if self.include_world_var.get() else None,
            'project_name': self.project_name
        }

        self.destroy()

    def _cancel(self):
        """キャンセル"""
        self.result = None
        self.destroy()
