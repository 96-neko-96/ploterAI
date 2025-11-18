"""
文体設定ダイアログ
物語の文体スタイルを設定
"""
import customtkinter as ctk
from typing import Dict


class StyleDialog(ctk.CTkToplevel):
    """文体設定ダイアログ"""

    def __init__(self, parent, current_style: Dict[str, str]):
        super().__init__(parent)

        self.current_style = current_style
        self.result = None

        self.title("文体スタイル設定")
        self.geometry("600x550")
        self.minsize(500, 450)  # 最小サイズを設定
        self.resizable(True, True)  # リサイズ可能に

        # モーダルにする
        self.transient(parent)
        self.grab_set()

        self._create_widgets()
        self._load_current_style()

        # ウィンドウを中央に配置
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (600 // 2)
        y = (self.winfo_screenheight() // 2) - (550 // 2)
        self.geometry(f"+{x}+{y}")

    def _create_widgets(self):
        """ウィジェットの作成"""
        # メインフレーム
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # タイトル
        title_label = ctk.CTkLabel(
            main_frame,
            text="文体スタイル設定",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.pack(pady=(0, 20))

        # 視点
        perspective_label = ctk.CTkLabel(
            main_frame,
            text="視点:",
            font=ctk.CTkFont(size=14)
        )
        perspective_label.pack(anchor="w", pady=(0, 5))

        self.perspective_var = ctk.StringVar(value="三人称")
        perspective_menu = ctk.CTkOptionMenu(
            main_frame,
            width=400,
            values=["一人称（私）", "三人称（彼、彼女）", "二人称（あなた）"],
            variable=self.perspective_var
        )
        perspective_menu.pack(pady=(0, 15))

        # 時制
        tense_label = ctk.CTkLabel(
            main_frame,
            text="語り口:",
            font=ctk.CTkFont(size=14)
        )
        tense_label.pack(anchor="w", pady=(0, 5))

        self.tense_var = ctk.StringVar(value="過去形")
        tense_menu = ctk.CTkOptionMenu(
            main_frame,
            width=400,
            values=["過去形", "現在形"],
            variable=self.tense_var
        )
        tense_menu.pack(pady=(0, 15))

        # トーン
        tone_label = ctk.CTkLabel(
            main_frame,
            text="トーン:",
            font=ctk.CTkFont(size=14)
        )
        tone_label.pack(anchor="w", pady=(0, 5))

        self.tone_var = ctk.StringVar(value="標準")
        tone_menu = ctk.CTkOptionMenu(
            main_frame,
            width=400,
            values=["シリアス", "標準", "コメディ", "ダーク"],
            variable=self.tone_var
        )
        tone_menu.pack(pady=(0, 15))

        # 描写レベル
        desc_label = ctk.CTkLabel(
            main_frame,
            text="描写レベル:",
            font=ctk.CTkFont(size=14)
        )
        desc_label.pack(anchor="w", pady=(0, 5))

        self.desc_var = ctk.StringVar(value="中程度")
        desc_menu = ctk.CTkOptionMenu(
            main_frame,
            width=400,
            values=["簡潔", "中程度", "詳細"],
            variable=self.desc_var
        )
        desc_menu.pack(pady=(0, 15))

        # 会話スタイル
        dialogue_label = ctk.CTkLabel(
            main_frame,
            text="会話スタイル:",
            font=ctk.CTkFont(size=14)
        )
        dialogue_label.pack(anchor="w", pady=(0, 5))

        self.dialogue_var = ctk.StringVar(value="標準")
        dialogue_menu = ctk.CTkOptionMenu(
            main_frame,
            width=400,
            values=["フォーマル", "標準", "カジュアル"],
            variable=self.dialogue_var
        )
        dialogue_menu.pack(pady=(0, 20))

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

        save_button = ctk.CTkButton(
            button_frame,
            text="保存",
            command=self._save,
            width=120
        )
        save_button.pack(side="right")

    def _load_current_style(self):
        """現在のスタイルを読み込み"""
        self.perspective_var.set(self.current_style.get('perspective', '三人称'))
        self.tense_var.set(self.current_style.get('tense', '過去形'))
        self.tone_var.set(self.current_style.get('tone', '標準'))
        self.desc_var.set(self.current_style.get('description_level', '中程度'))
        self.dialogue_var.set(self.current_style.get('dialogue_style', '標準'))

    def _save(self):
        """設定を保存"""
        self.result = {
            'perspective': self.perspective_var.get(),
            'tense': self.tense_var.get(),
            'tone': self.tone_var.get(),
            'description_level': self.desc_var.get(),
            'dialogue_style': self.dialogue_var.get()
        }
        self.destroy()

    def _cancel(self):
        """キャンセル"""
        self.result = None
        self.destroy()
