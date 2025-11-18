"""
API設定ダイアログ
Gemini APIの設定を管理
"""
import customtkinter as ctk
from tkinter import messagebox
from typing import Callable, Optional


class APIConfigDialog(ctk.CTkToplevel):
    """API設定ダイアログ"""

    def __init__(
        self,
        parent,
        config,
        test_connection_callback: Optional[Callable] = None
    ):
        super().__init__(parent)

        self.config = config
        self.test_connection_callback = test_connection_callback
        self.result = None

        self.title("API設定")
        self.geometry("600x500")
        self.resizable(False, False)

        # モーダルにする
        self.transient(parent)
        self.grab_set()

        self._create_widgets()
        self._load_current_config()

        # ウィンドウを中央に配置
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (600 // 2)
        y = (self.winfo_screenheight() // 2) - (500 // 2)
        self.geometry(f"+{x}+{y}")

    def _create_widgets(self):
        """ウィジェットの作成"""
        # メインフレーム
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # タイトル
        title_label = ctk.CTkLabel(
            main_frame,
            text="Gemini API設定",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.pack(pady=(0, 20))

        # APIキー入力
        api_key_label = ctk.CTkLabel(
            main_frame,
            text="APIキー:",
            font=ctk.CTkFont(size=14)
        )
        api_key_label.pack(anchor="w", pady=(0, 5))

        self.api_key_entry = ctk.CTkEntry(
            main_frame,
            width=500,
            placeholder_text="Gemini APIキーを入力してください",
            show="*"
        )
        self.api_key_entry.pack(pady=(0, 5))

        # APIキー表示/非表示トグル
        self.show_key_var = ctk.BooleanVar(value=False)
        show_key_checkbox = ctk.CTkCheckBox(
            main_frame,
            text="APIキーを表示",
            variable=self.show_key_var,
            command=self._toggle_api_key_visibility
        )
        show_key_checkbox.pack(anchor="w", pady=(0, 15))

        # モデル選択
        model_label = ctk.CTkLabel(
            main_frame,
            text="モデル:",
            font=ctk.CTkFont(size=14)
        )
        model_label.pack(anchor="w", pady=(0, 5))

        self.model_var = ctk.StringVar(value="gemini-2.0-flash")
        self.model_menu = ctk.CTkOptionMenu(
            main_frame,
            width=500,
            values=[
                "gemini-2.5-pro",
                "gemini-2.5-flash",
                "gemini-2.5-flash-lite",
                "gemini-2.0-flash",
                "gemini-2.0-flash-lite",
                "gemini-2.0-flash-exp",
                "gemini-1.5-pro",
                "gemini-1.5-flash"
            ],
            variable=self.model_var
        )
        self.model_menu.pack(pady=(0, 15))

        # Temperature
        temp_label = ctk.CTkLabel(
            main_frame,
            text="Temperature (0.0 - 1.0):",
            font=ctk.CTkFont(size=14)
        )
        temp_label.pack(anchor="w", pady=(0, 5))

        temp_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        temp_frame.pack(fill="x", pady=(0, 15))

        self.temp_slider = ctk.CTkSlider(
            temp_frame,
            from_=0.0,
            to=1.0,
            number_of_steps=10,
            command=self._update_temp_label
        )
        self.temp_slider.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.temp_slider.set(0.7)

        self.temp_label = ctk.CTkLabel(temp_frame, text="0.7", width=40)
        self.temp_label.pack(side="right")

        # Max Tokens
        tokens_label = ctk.CTkLabel(
            main_frame,
            text="Max Tokens (1000 - 8000):",
            font=ctk.CTkFont(size=14)
        )
        tokens_label.pack(anchor="w", pady=(0, 5))

        tokens_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        tokens_frame.pack(fill="x", pady=(0, 15))

        self.tokens_slider = ctk.CTkSlider(
            tokens_frame,
            from_=1000,
            to=8000,
            number_of_steps=70,
            command=self._update_tokens_label
        )
        self.tokens_slider.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.tokens_slider.set(4000)

        self.tokens_label = ctk.CTkLabel(tokens_frame, text="4000", width=50)
        self.tokens_label.pack(side="right")

        # Top P
        top_p_label = ctk.CTkLabel(
            main_frame,
            text="Top P (0.0 - 1.0):",
            font=ctk.CTkFont(size=14)
        )
        top_p_label.pack(anchor="w", pady=(0, 5))

        top_p_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        top_p_frame.pack(fill="x", pady=(0, 20))

        self.top_p_slider = ctk.CTkSlider(
            top_p_frame,
            from_=0.0,
            to=1.0,
            number_of_steps=10,
            command=self._update_top_p_label
        )
        self.top_p_slider.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.top_p_slider.set(0.9)

        self.top_p_label = ctk.CTkLabel(top_p_frame, text="0.9", width=40)
        self.top_p_label.pack(side="right")

        # ボタン
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(fill="x", pady=(10, 0))

        test_button = ctk.CTkButton(
            button_frame,
            text="接続テスト",
            command=self._test_connection,
            width=120
        )
        test_button.pack(side="left", padx=(0, 10))

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

    def _load_current_config(self):
        """現在の設定を読み込み"""
        api_config = self.config.get_api_config()

        # APIキー
        api_key = self.config.get_api_key()
        if api_key:
            self.api_key_entry.insert(0, api_key)

        # モデル
        self.model_var.set(api_config.get('model', 'gemini-2.0-flash-exp'))

        # Temperature
        self.temp_slider.set(api_config.get('temperature', 0.7))
        self._update_temp_label(api_config.get('temperature', 0.7))

        # Max Tokens
        self.tokens_slider.set(api_config.get('max_tokens', 4000))
        self._update_tokens_label(api_config.get('max_tokens', 4000))

        # Top P
        self.top_p_slider.set(api_config.get('top_p', 0.9))
        self._update_top_p_label(api_config.get('top_p', 0.9))

    def _toggle_api_key_visibility(self):
        """APIキーの表示/非表示を切り替え"""
        if self.show_key_var.get():
            self.api_key_entry.configure(show="")
        else:
            self.api_key_entry.configure(show="*")

    def _update_temp_label(self, value):
        """Temperatureラベルの更新"""
        self.temp_label.configure(text=f"{float(value):.1f}")

    def _update_tokens_label(self, value):
        """Max Tokensラベルの更新"""
        self.tokens_label.configure(text=str(int(value)))

    def _update_top_p_label(self, value):
        """Top Pラベルの更新"""
        self.top_p_label.configure(text=f"{float(value):.1f}")

    def _test_connection(self):
        """接続テスト"""
        api_key = self.api_key_entry.get().strip()

        if not api_key:
            messagebox.showerror("エラー", "APIキーを入力してください")
            return

        if self.test_connection_callback:
            try:
                if self.test_connection_callback(api_key, self.model_var.get()):
                    messagebox.showinfo("成功", "API接続に成功しました")
                else:
                    messagebox.showerror("エラー", "API接続に失敗しました")
            except Exception as e:
                messagebox.showerror("エラー", f"API接続に失敗しました: {str(e)}")

    def _save(self):
        """設定を保存"""
        api_key = self.api_key_entry.get().strip()

        if not api_key:
            messagebox.showerror("エラー", "APIキーを入力してください")
            return

        try:
            # APIキーの保存
            self.config.set_api_key(api_key)

            # API設定の保存
            self.config.set_api_config(
                model=self.model_var.get(),
                temperature=self.temp_slider.get(),
                max_tokens=int(self.tokens_slider.get()),
                top_p=self.top_p_slider.get()
            )

            self.result = True
            self.destroy()

        except Exception as e:
            messagebox.showerror("エラー", f"設定の保存に失敗しました: {str(e)}")

    def _cancel(self):
        """キャンセル"""
        self.result = False
        self.destroy()
