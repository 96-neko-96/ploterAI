"""
テーマ設定ダイアログ
UIのカラーテーマを設定
"""
import customtkinter as ctk


class ThemeDialog(ctk.CTkToplevel):
    """テーマ設定ダイアログ"""

    def __init__(self, parent, config, apply_theme_callback):
        super().__init__(parent)

        self.config = config
        self.apply_theme_callback = apply_theme_callback
        self.result = None

        self.title("テーマ設定")
        self.geometry("500x400")
        self.minsize(400, 300)  # 最小サイズを設定
        self.resizable(True, True)  # リサイズ可能に

        # モーダルにする
        self.transient(parent)
        self.grab_set()

        self._create_widgets()
        self._load_current_theme()

        # ウィンドウを中央に配置
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.winfo_screenheight() // 2) - (400 // 2)
        self.geometry(f"+{x}+{y}")

    def _create_widgets(self):
        """ウィジェットの作成"""
        # メインフレーム
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # タイトル
        title_label = ctk.CTkLabel(
            main_frame,
            text="テーマ設定",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.pack(pady=(0, 20))

        # カラーモード
        mode_label = ctk.CTkLabel(
            main_frame,
            text="カラーモード:",
            font=ctk.CTkFont(size=14)
        )
        mode_label.pack(anchor="w", pady=(0, 5))

        self.mode_var = ctk.StringVar(value="dark")
        mode_menu = ctk.CTkOptionMenu(
            main_frame,
            width=320,
            values=["light", "dark"],
            variable=self.mode_var,
            command=self._preview_theme
        )
        mode_menu.pack(pady=(0, 15))

        # カラーテーマ
        theme_label = ctk.CTkLabel(
            main_frame,
            text="カラーテーマ:",
            font=ctk.CTkFont(size=14)
        )
        theme_label.pack(anchor="w", pady=(0, 5))

        self.theme_var = ctk.StringVar(value="blue")
        theme_menu = ctk.CTkOptionMenu(
            main_frame,
            width=320,
            values=["blue", "green", "dark-blue"],
            variable=self.theme_var,
            command=self._preview_theme
        )
        theme_menu.pack(pady=(0, 20))

        # プレビュー説明
        preview_label = ctk.CTkLabel(
            main_frame,
            text="※テーマは選択時にプレビュー表示されます",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        preview_label.pack(pady=(0, 20))

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

    def _load_current_theme(self):
        """現在のテーマを読み込み"""
        ui_theme = self.config.get_ui_theme()
        self.mode_var.set(ui_theme.get('theme_mode', 'dark'))
        self.theme_var.set(ui_theme.get('color_theme', 'blue'))

    def _preview_theme(self, value=None):
        """テーマをプレビュー"""
        if self.apply_theme_callback:
            self.apply_theme_callback(self.mode_var.get(), self.theme_var.get())

    def _save(self):
        """設定を保存"""
        try:
            self.config.set_ui_theme(self.mode_var.get(), self.theme_var.get())
            self.result = True
            self.destroy()
        except Exception as e:
            ctk.CTkMessagebox(
                title="エラー",
                message=f"設定の保存に失敗しました: {str(e)}",
                icon="cancel"
            )

    def _cancel(self):
        """キャンセル"""
        # 元のテーマに戻す
        ui_theme = self.config.get_ui_theme()
        if self.apply_theme_callback:
            self.apply_theme_callback(
                ui_theme.get('theme_mode', 'dark'),
                ui_theme.get('color_theme', 'blue')
            )

        self.result = False
        self.destroy()
