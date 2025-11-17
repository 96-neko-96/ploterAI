"""
新規プロジェクトダイアログ
新しいプロジェクトを作成
"""
import customtkinter as ctk
from tkinter import filedialog, messagebox
from pathlib import Path


class NewProjectDialog(ctk.CTkToplevel):
    """新規プロジェクトダイアログ"""

    def __init__(self, parent):
        super().__init__(parent)

        self.result = None

        self.title("新規プロジェクト")
        self.geometry("500x250")
        self.resizable(False, False)

        # モーダルにする
        self.transient(parent)
        self.grab_set()

        self._create_widgets()

        # ウィンドウを中央に配置
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.winfo_screenheight() // 2) - (250 // 2)
        self.geometry(f"+{x}+{y}")

    def _create_widgets(self):
        """ウィジェットの作成"""
        # メインフレーム
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # タイトル
        title_label = ctk.CTkLabel(
            main_frame,
            text="新規プロジェクト",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.pack(pady=(0, 20))

        # プロジェクト名
        name_label = ctk.CTkLabel(
            main_frame,
            text="プロジェクト名:",
            font=ctk.CTkFont(size=14)
        )
        name_label.pack(anchor="w", pady=(0, 5))

        self.name_entry = ctk.CTkEntry(
            main_frame,
            width=400,
            placeholder_text="プロジェクト名を入力してください"
        )
        self.name_entry.pack(pady=(0, 15))

        # 保存先
        path_label = ctk.CTkLabel(
            main_frame,
            text="保存先:",
            font=ctk.CTkFont(size=14)
        )
        path_label.pack(anchor="w", pady=(0, 5))

        path_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        path_frame.pack(fill="x", pady=(0, 20))

        self.path_entry = ctk.CTkEntry(
            path_frame,
            width=330,
            placeholder_text="保存先を選択してください"
        )
        self.path_entry.pack(side="left", padx=(0, 10))

        browse_button = ctk.CTkButton(
            path_frame,
            text="参照...",
            command=self._browse_path,
            width=60
        )
        browse_button.pack(side="left")

        # ボタン
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(fill="x")

        cancel_button = ctk.CTkButton(
            button_frame,
            text="キャンセル",
            command=self._cancel,
            fg_color="gray",
            width=120
        )
        cancel_button.pack(side="left")

        create_button = ctk.CTkButton(
            button_frame,
            text="作成",
            command=self._create,
            width=120
        )
        create_button.pack(side="right")

    def _browse_path(self):
        """保存先を参照"""
        file_path = filedialog.asksaveasfilename(
            title="プロジェクトの保存先を選択",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )

        if file_path:
            self.path_entry.delete(0, "end")
            self.path_entry.insert(0, file_path)

    def _create(self):
        """プロジェクトを作成"""
        name = self.name_entry.get().strip()
        path = self.path_entry.get().strip()

        if not name:
            messagebox.showerror("エラー", "プロジェクト名を入力してください")
            return

        if not path:
            messagebox.showerror("エラー", "保存先を選択してください")
            return

        # パスの検証
        try:
            path_obj = Path(path)
            if not path_obj.suffix:
                path = str(path_obj) + ".json"
        except Exception as e:
            messagebox.showerror("エラー", f"無効なパスです: {str(e)}")
            return

        self.result = {"name": name, "path": path}
        self.destroy()

    def _cancel(self):
        """キャンセル"""
        self.result = None
        self.destroy()
