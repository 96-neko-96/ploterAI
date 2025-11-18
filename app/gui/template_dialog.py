"""
テンプレートダイアログ
文体スタイルテンプレートの管理
"""
import customtkinter as ctk
from tkinter import messagebox
from typing import Dict, Any, Optional
from app.utils.template_manager import TemplateManager


class TemplateDialog(ctk.CTkToplevel):
    """テンプレートダイアログクラス"""

    def __init__(self, parent, current_style: Dict[str, Any], callback):
        super().__init__(parent)

        self.title("テンプレート管理")
        self.geometry("700x600")
        self.minsize(600, 500)  # 最小サイズを設定
        self.resizable(True, True)  # リサイズ可能に

        # モーダルにする
        self.transient(parent)
        self.grab_set()

        self.current_style = current_style
        self.callback = callback
        self.template_manager = TemplateManager()
        self.result = None

        self._create_widgets()
        self._refresh_template_list()

        # ウィンドウを中央に配置
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (700 // 2)
        y = (self.winfo_screenheight() // 2) - (600 // 2)
        self.geometry(f"+{x}+{y}")

    def _create_widgets(self):
        """ウィジェットの作成"""
        # メインフレーム
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # タイトル
        title_label = ctk.CTkLabel(
            main_frame,
            text="文体スタイル テンプレート",
            font=("", 20, "bold")
        )
        title_label.pack(pady=(0, 20))

        # テンプレート一覧
        list_label = ctk.CTkLabel(main_frame, text="保存済みテンプレート:", anchor="w")
        list_label.pack(fill="x", pady=(0, 5))

        # スクロール可能なフレーム
        self.template_list_frame = ctk.CTkScrollableFrame(main_frame, height=250)
        self.template_list_frame.pack(fill="both", expand=True, pady=(0, 20))

        # 選択されたテンプレート名表示
        self.selected_label = ctk.CTkLabel(
            main_frame,
            text="選択: なし",
            anchor="w"
        )
        self.selected_label.pack(fill="x", pady=(0, 10))

        # ボタンフレーム
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.pack(fill="x", pady=(0, 10))

        # 読み込みボタン
        load_btn = ctk.CTkButton(
            button_frame,
            text="読み込み",
            command=self._load_template,
            width=120
        )
        load_btn.pack(side="left", padx=5)

        # 保存ボタン
        save_btn = ctk.CTkButton(
            button_frame,
            text="現在のスタイルを保存",
            command=self._save_current_style,
            width=150
        )
        save_btn.pack(side="left", padx=5)

        # 削除ボタン
        delete_btn = ctk.CTkButton(
            button_frame,
            text="削除",
            command=self._delete_template,
            width=100,
            fg_color="red",
            hover_color="darkred"
        )
        delete_btn.pack(side="left", padx=5)

        # デフォルトテンプレート作成ボタン
        default_btn = ctk.CTkButton(
            button_frame,
            text="デフォルト復元",
            command=self._restore_defaults,
            width=130
        )
        default_btn.pack(side="left", padx=5)

        # 閉じるボタン
        close_btn = ctk.CTkButton(
            main_frame,
            text="閉じる",
            command=self.destroy,
            width=100
        )
        close_btn.pack()

        # 選択されたテンプレート
        self.selected_template = None

    def _refresh_template_list(self):
        """テンプレート一覧を更新"""
        # 既存のウィジェットを削除
        for widget in self.template_list_frame.winfo_children():
            widget.destroy()

        # テンプレート一覧を取得
        templates = self.template_manager.list_templates()

        if not templates:
            no_template_label = ctk.CTkLabel(
                self.template_list_frame,
                text="保存済みテンプレートがありません",
                text_color="gray"
            )
            no_template_label.pack(pady=20)
            return

        # テンプレートをボタンで表示
        for template_name in templates:
            btn = ctk.CTkButton(
                self.template_list_frame,
                text=template_name,
                command=lambda name=template_name: self._select_template(name),
                anchor="w"
            )
            btn.pack(fill="x", pady=2)

    def _select_template(self, template_name: str):
        """テンプレートを選択"""
        self.selected_template = template_name
        self.selected_label.configure(text=f"選択: {template_name}")

    def _load_template(self):
        """選択したテンプレートを読み込み"""
        if not self.selected_template:
            messagebox.showwarning("警告", "テンプレートを選択してください")
            return

        style = self.template_manager.load_template(self.selected_template)

        if style:
            # コールバックでスタイルを適用
            if self.callback:
                self.callback(style)

            messagebox.showinfo("成功", f"テンプレート「{self.selected_template}」を読み込みました")
            self.result = style
            self.destroy()
        else:
            messagebox.showerror("エラー", "テンプレートの読み込みに失敗しました")

    def _save_current_style(self):
        """現在のスタイルをテンプレートとして保存"""
        # 名前入力ダイアログを表示
        dialog = ctk.CTkInputDialog(
            text="テンプレート名を入力してください:",
            title="テンプレート保存"
        )
        template_name = dialog.get_input()

        if template_name:
            if self.template_manager.save_template(template_name, self.current_style):
                messagebox.showinfo("成功", f"テンプレート「{template_name}」を保存しました")
                self._refresh_template_list()
            else:
                messagebox.showerror("エラー", "テンプレートの保存に失敗しました")

    def _delete_template(self):
        """選択したテンプレートを削除"""
        if not self.selected_template:
            messagebox.showwarning("警告", "削除するテンプレートを選択してください")
            return

        # 確認ダイアログ
        result = messagebox.askyesno(
            "確認",
            f"テンプレート「{self.selected_template}」を削除しますか?"
        )

        if result:
            if self.template_manager.delete_template(self.selected_template):
                messagebox.showinfo("成功", "テンプレートを削除しました")
                self.selected_template = None
                self.selected_label.configure(text="選択: なし")
                self._refresh_template_list()
            else:
                messagebox.showerror("エラー", "テンプレートの削除に失敗しました")

    def _restore_defaults(self):
        """デフォルトテンプレートを復元"""
        result = messagebox.askyesno(
            "確認",
            "デフォルトテンプレートを復元しますか?\n（既存の同名テンプレートは上書きされません）"
        )

        if result:
            self.template_manager.ensure_default_templates()
            messagebox.showinfo("成功", "デフォルトテンプレートを復元しました")
            self._refresh_template_list()
