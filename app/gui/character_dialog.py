"""
キャラクターダイアログ
キャラクターの作成・編集・AI生成を管理
"""
import customtkinter as ctk
from tkinter import messagebox
from typing import Dict, Optional, Callable
import threading


class CharacterDialog(ctk.CTkToplevel):
    """キャラクターダイアログ"""

    def __init__(
        self,
        parent,
        character_data: Optional[Dict[str, str]] = None,
        ai_generate_callback: Optional[Callable] = None
    ):
        super().__init__(parent)

        self.character_data = character_data
        self.ai_generate_callback = ai_generate_callback
        self.result = None

        mode = "編集" if character_data else "作成"
        self.title(f"キャラクター{mode}")
        self.geometry("850x750")
        self.minsize(700, 600)  # 最小サイズを設定
        self.resizable(True, True)  # リサイズ可能に

        # モーダルにする
        self.transient(parent)
        self.grab_set()

        self._create_widgets()

        if character_data:
            self._load_character_data()

        # ウィンドウを中央に配置
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (850 // 2)
        y = (self.winfo_screenheight() // 2) - (750 // 2)
        self.geometry(f"+{x}+{y}")

    def _create_widgets(self):
        """ウィジェットの作成"""
        # メインフレーム
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # ヘッダーフレーム
        header_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 15))

        # タイトル
        mode = "編集" if self.character_data else "作成"
        title_label = ctk.CTkLabel(
            header_frame,
            text=f"👤 キャラクター{mode}",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=("#1f538d", "#3a7ebf")
        )
        title_label.pack(side="left")

        # AI生成ボタン
        if not self.character_data and self.ai_generate_callback:
            ai_button = ctk.CTkButton(
                header_frame,
                text="✨ AIで生成",
                command=self._show_ai_generation,
                width=130,
                height=36,
                corner_radius=6,
                fg_color="#1565c0",
                hover_color="#0d47a1",
                font=ctk.CTkFont(size=13, weight="bold")
            )
            ai_button.pack(side="right")

        # スクロール可能フレーム
        scroll_frame = ctk.CTkScrollableFrame(main_frame, width=700, height=480)
        scroll_frame.pack(fill="both", expand=True, pady=(0, 15))

        # フィールドウィジェット保存用
        self.field_widgets = {}

        # フォームフィールド
        fields = [
            ("名前", "name", "キャラクターの名前を入力...", True, 1),
            ("性格", "personality", "性格の特徴を入力...", False, 3),
            ("外見", "appearance", "外見の特徴を入力...", False, 3),
            ("背景・経歴", "background", "生い立ちや経歴を入力...", False, 3),
            ("特技・能力", "skills", "特殊な能力やスキルを入力...", False, 3),
            ("口調・話し方", "speech", "話し方の特徴を入力...", False, 2),
            ("人間関係", "relationships", "他のキャラクターとの関係を入力...", False, 3),
            ("目標・動機", "goals", "行動の目的や動機を入力...", False, 3),
        ]

        for label_text, field_name, placeholder, is_entry, height in fields:
            # フィールドコンテナ
            field_container = ctk.CTkFrame(scroll_frame, fg_color="transparent")
            field_container.pack(fill="x", pady=(0, 15), padx=10)

            # ラベル
            label_frame = ctk.CTkFrame(field_container, fg_color="transparent")
            label_frame.pack(fill="x", pady=(0, 5))

            label = ctk.CTkLabel(
                label_frame,
                text=label_text,
                font=ctk.CTkFont(size=13, weight="bold"),
                anchor="w"
            )
            label.pack(side="left")

            if is_entry:
                # 必須マーク
                required_label = ctk.CTkLabel(
                    label_frame,
                    text=" *",
                    font=ctk.CTkFont(size=14, weight="bold"),
                    text_color="red"
                )
                required_label.pack(side="left", padx=(3, 0))

            # 入力フィールド
            if is_entry:
                widget = ctk.CTkEntry(
                    field_container,
                    placeholder_text=placeholder,
                    height=38,
                    corner_radius=6,
                    font=ctk.CTkFont(size=13)
                )
            else:
                widget = ctk.CTkTextbox(
                    field_container,
                    height=height * 30,
                    corner_radius=6,
                    font=ctk.CTkFont(size=12),
                    wrap="word"
                )

            widget.pack(fill="x")
            self.field_widgets[field_name] = widget

        # ボタン
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(fill="x")

        cancel_button = ctk.CTkButton(
            button_frame,
            text="キャンセル",
            command=self._cancel,
            fg_color="gray",
            hover_color="darkgray",
            width=140,
            height=38,
            corner_radius=6,
            font=ctk.CTkFont(size=13)
        )
        cancel_button.pack(side="left")

        save_button = ctk.CTkButton(
            button_frame,
            text="💾 保存",
            command=self._save,
            width=140,
            height=38,
            corner_radius=6,
            fg_color="#2e7d32",
            hover_color="#1b5e20",
            font=ctk.CTkFont(size=13, weight="bold")
        )
        save_button.pack(side="right")

    def _load_character_data(self):
        """キャラクターデータを読み込み"""
        for field_name, widget in self.field_widgets.items():
            value = self.character_data.get(field_name, '')
            if isinstance(widget, ctk.CTkEntry):
                widget.insert(0, value)
            else:  # CTkTextbox
                widget.insert("1.0", value)

    def _show_ai_generation(self):
        """AI生成ダイアログを表示"""
        ai_dialog = AICharacterDialog(self, self.ai_generate_callback)
        self.wait_window(ai_dialog)

        if ai_dialog.result:
            # 生成されたデータをフォームに入力
            for field_name, widget in self.field_widgets.items():
                value = ai_dialog.result.get(field_name, '')
                if isinstance(widget, ctk.CTkEntry):
                    widget.delete(0, "end")
                    widget.insert(0, value)
                else:  # CTkTextbox
                    widget.delete("1.0", "end")
                    widget.insert("1.0", value)

    def _save(self):
        """保存"""
        # 名前の必須チェック
        name_widget = self.field_widgets['name']
        name = name_widget.get().strip()

        if not name:
            messagebox.showerror("エラー", "名前は必須です")
            return

        # 全フィールドのデータを収集
        self.result = {}
        for field_name, widget in self.field_widgets.items():
            if isinstance(widget, ctk.CTkEntry):
                self.result[field_name] = widget.get().strip()
            else:  # CTkTextbox
                self.result[field_name] = widget.get("1.0", "end-1c").strip()

        self.destroy()

    def _cancel(self):
        """キャンセル"""
        self.result = None
        self.destroy()


class AICharacterDialog(ctk.CTkToplevel):
    """AI生成用ダイアログ"""

    def __init__(self, parent, ai_generate_callback):
        super().__init__(parent)

        self.ai_generate_callback = ai_generate_callback
        self.result = None

        self.title("AIでキャラクター生成")
        self.geometry("600x300")
        self.resizable(False, False)

        # モーダルにする
        self.transient(parent)
        self.grab_set()

        self._create_widgets()

        # ウィンドウを中央に配置
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (600 // 2)
        y = (self.winfo_screenheight() // 2) - (300 // 2)
        self.geometry(f"+{x}+{y}")

    def _create_widgets(self):
        """ウィジェットの作成"""
        # メインフレーム
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # タイトル
        title_label = ctk.CTkLabel(
            main_frame,
            text="✨ AIでキャラクター生成",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=("#1f538d", "#3a7ebf")
        )
        title_label.pack(pady=(0, 10))

        # 説明文
        desc_label = ctk.CTkLabel(
            main_frame,
            text="AIがキャラクターの詳細な設定を自動生成します",
            font=ctk.CTkFont(size=12),
            text_color=("gray40", "gray60")
        )
        desc_label.pack(pady=(0, 20))

        # コンセプト
        concept_label = ctk.CTkLabel(
            main_frame,
            text="キャラクターのコンセプト *",
            font=ctk.CTkFont(size=13, weight="bold"),
            anchor="w"
        )
        concept_label.pack(anchor="w", pady=(0, 5))

        self.concept_entry = ctk.CTkEntry(
            main_frame,
            width=520,
            height=38,
            placeholder_text="例: 勇敢な騎士、天才魔法使い、気弱な学生",
            font=ctk.CTkFont(size=13),
            corner_radius=6
        )
        self.concept_entry.pack(fill="x", pady=(0, 15))

        # 追加情報
        additional_label = ctk.CTkLabel(
            main_frame,
            text="追加情報（任意）",
            font=ctk.CTkFont(size=13, weight="bold"),
            anchor="w"
        )
        additional_label.pack(anchor="w", pady=(0, 5))

        self.additional_text = ctk.CTkTextbox(
            main_frame,
            height=90,
            font=ctk.CTkFont(size=12),
            corner_radius=6,
            wrap="word"
        )
        self.additional_text.pack(fill="x", pady=(0, 20))

        # ボタン
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(fill="x")

        cancel_button = ctk.CTkButton(
            button_frame,
            text="キャンセル",
            command=self._cancel,
            fg_color="gray",
            hover_color="darkgray",
            width=140,
            height=38,
            corner_radius=6,
            font=ctk.CTkFont(size=13)
        )
        cancel_button.pack(side="left")

        generate_button = ctk.CTkButton(
            button_frame,
            text="✨ 生成開始",
            command=self._generate,
            width=140,
            height=38,
            corner_radius=6,
            fg_color="#1565c0",
            hover_color="#0d47a1",
            font=ctk.CTkFont(size=13, weight="bold")
        )
        generate_button.pack(side="right")

    def _generate(self):
        """生成"""
        concept = self.concept_entry.get().strip()

        if not concept:
            messagebox.showerror("エラー", "コンセプトを入力してください")
            return

        additional_info = self.additional_text.get("1.0", "end-1c").strip()

        # プログレスダイアログを表示
        progress_dialog = ProgressDialog(self, "キャラクターを生成中...")

        def generate_thread():
            try:
                result = self.ai_generate_callback(concept, additional_info)
                self.result = result
                progress_dialog.close()
                self.destroy()
            except Exception as e:
                progress_dialog.close()
                messagebox.showerror("エラー", f"生成に失敗しました: {str(e)}")

        thread = threading.Thread(target=generate_thread, daemon=True)
        thread.start()

        progress_dialog.show()

    def _cancel(self):
        """キャンセル"""
        self.result = None
        self.destroy()


class ProgressDialog(ctk.CTkToplevel):
    """プログレスダイアログ"""

    def __init__(self, parent, message):
        super().__init__(parent)

        self.title("処理中")
        self.geometry("350x120")
        self.resizable(False, False)

        # モーダルにする
        self.transient(parent)

        # メインフレーム
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # アイコン付きメッセージ
        message_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        message_frame.pack(pady=(0, 15))

        icon_label = ctk.CTkLabel(
            message_frame,
            text="⏳",
            font=ctk.CTkFont(size=24)
        )
        icon_label.pack(side="left", padx=(0, 10))

        label = ctk.CTkLabel(
            message_frame,
            text=message,
            font=ctk.CTkFont(size=14)
        )
        label.pack(side="left")

        # プログレスバー
        self.progressbar = ctk.CTkProgressBar(main_frame, width=280, height=8)
        self.progressbar.pack()
        self.progressbar.set(0)
        self.progressbar.start()

        # ウィンドウを中央に配置
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (350 // 2)
        y = (self.winfo_screenheight() // 2) - (120 // 2)
        self.geometry(f"+{x}+{y}")

        # 表示しない（show()で表示）
        self.withdraw()

    def show(self):
        """ダイアログを表示"""
        self.deiconify()
        self.grab_set()

    def close(self):
        """ダイアログを閉じる"""
        self.grab_release()
        self.destroy()
