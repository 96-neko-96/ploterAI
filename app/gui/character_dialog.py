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
        self.geometry("800x700")

        # モーダルにする
        self.transient(parent)
        self.grab_set()

        self._create_widgets()

        if character_data:
            self._load_character_data()

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
        mode = "編集" if self.character_data else "作成"
        title_label = ctk.CTkLabel(
            main_frame,
            text=f"キャラクター{mode}",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.pack(pady=(0, 10))

        # AI生成ボタン
        if not self.character_data and self.ai_generate_callback:
            ai_button = ctk.CTkButton(
                main_frame,
                text="AIで生成",
                command=self._show_ai_generation,
                width=120
            )
            ai_button.pack(pady=(0, 10))

        # スクロール可能フレーム
        scroll_frame = ctk.CTkScrollableFrame(main_frame, width=700, height=480)
        scroll_frame.pack(fill="both", expand=True, pady=(0, 10))

        # 名前
        name_label = ctk.CTkLabel(
            scroll_frame,
            text="名前 (必須):",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        name_label.pack(anchor="w", pady=(0, 5))

        self.name_entry = ctk.CTkEntry(
            scroll_frame,
            width=700,
            placeholder_text="キャラクターの名前"
        )
        self.name_entry.pack(pady=(0, 15))

        # 性格
        personality_label = ctk.CTkLabel(
            scroll_frame,
            text="性格:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        personality_label.pack(anchor="w", pady=(0, 5))

        self.personality_text = ctk.CTkTextbox(
            scroll_frame,
            width=700,
            height=80
        )
        self.personality_text.pack(pady=(0, 15))

        # 外見
        appearance_label = ctk.CTkLabel(
            scroll_frame,
            text="外見:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        appearance_label.pack(anchor="w", pady=(0, 5))

        self.appearance_text = ctk.CTkTextbox(
            scroll_frame,
            width=700,
            height=80
        )
        self.appearance_text.pack(pady=(0, 15))

        # 背景・経歴
        background_label = ctk.CTkLabel(
            scroll_frame,
            text="背景・経歴:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        background_label.pack(anchor="w", pady=(0, 5))

        self.background_text = ctk.CTkTextbox(
            scroll_frame,
            width=700,
            height=80
        )
        self.background_text.pack(pady=(0, 15))

        # 特技・能力
        skills_label = ctk.CTkLabel(
            scroll_frame,
            text="特技・能力:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        skills_label.pack(anchor="w", pady=(0, 5))

        self.skills_text = ctk.CTkTextbox(
            scroll_frame,
            width=700,
            height=80
        )
        self.skills_text.pack(pady=(0, 15))

        # 口調・話し方
        speech_label = ctk.CTkLabel(
            scroll_frame,
            text="口調・話し方:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        speech_label.pack(anchor="w", pady=(0, 5))

        self.speech_text = ctk.CTkTextbox(
            scroll_frame,
            width=700,
            height=60
        )
        self.speech_text.pack(pady=(0, 15))

        # 人間関係
        relationships_label = ctk.CTkLabel(
            scroll_frame,
            text="人間関係:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        relationships_label.pack(anchor="w", pady=(0, 5))

        self.relationships_text = ctk.CTkTextbox(
            scroll_frame,
            width=700,
            height=80
        )
        self.relationships_text.pack(pady=(0, 15))

        # 目標・動機
        goals_label = ctk.CTkLabel(
            scroll_frame,
            text="目標・動機:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        goals_label.pack(anchor="w", pady=(0, 5))

        self.goals_text = ctk.CTkTextbox(
            scroll_frame,
            width=700,
            height=80
        )
        self.goals_text.pack(pady=(0, 15))

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

    def _load_character_data(self):
        """キャラクターデータを読み込み"""
        self.name_entry.insert(0, self.character_data.get('name', ''))
        self.personality_text.insert("1.0", self.character_data.get('personality', ''))
        self.appearance_text.insert("1.0", self.character_data.get('appearance', ''))
        self.background_text.insert("1.0", self.character_data.get('background', ''))
        self.skills_text.insert("1.0", self.character_data.get('skills', ''))
        self.speech_text.insert("1.0", self.character_data.get('speech', ''))
        self.relationships_text.insert("1.0", self.character_data.get('relationships', ''))
        self.goals_text.insert("1.0", self.character_data.get('goals', ''))

    def _show_ai_generation(self):
        """AI生成ダイアログを表示"""
        ai_dialog = AICharacterDialog(self, self.ai_generate_callback)
        self.wait_window(ai_dialog)

        if ai_dialog.result:
            # 生成されたデータをフォームに入力
            self.name_entry.delete(0, "end")
            self.name_entry.insert(0, ai_dialog.result.get('name', ''))

            self.personality_text.delete("1.0", "end")
            self.personality_text.insert("1.0", ai_dialog.result.get('personality', ''))

            self.appearance_text.delete("1.0", "end")
            self.appearance_text.insert("1.0", ai_dialog.result.get('appearance', ''))

            self.background_text.delete("1.0", "end")
            self.background_text.insert("1.0", ai_dialog.result.get('background', ''))

            self.skills_text.delete("1.0", "end")
            self.skills_text.insert("1.0", ai_dialog.result.get('skills', ''))

            self.speech_text.delete("1.0", "end")
            self.speech_text.insert("1.0", ai_dialog.result.get('speech', ''))

            self.relationships_text.delete("1.0", "end")
            self.relationships_text.insert("1.0", ai_dialog.result.get('relationships', ''))

            self.goals_text.delete("1.0", "end")
            self.goals_text.insert("1.0", ai_dialog.result.get('goals', ''))

    def _save(self):
        """保存"""
        name = self.name_entry.get().strip()

        if not name:
            messagebox.showerror("エラー", "名前は必須です")
            return

        self.result = {
            'name': name,
            'personality': self.personality_text.get("1.0", "end-1c").strip(),
            'appearance': self.appearance_text.get("1.0", "end-1c").strip(),
            'background': self.background_text.get("1.0", "end-1c").strip(),
            'skills': self.skills_text.get("1.0", "end-1c").strip(),
            'speech': self.speech_text.get("1.0", "end-1c").strip(),
            'relationships': self.relationships_text.get("1.0", "end-1c").strip(),
            'goals': self.goals_text.get("1.0", "end-1c").strip()
        }

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
            text="AIでキャラクター生成",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.pack(pady=(0, 20))

        # コンセプト
        concept_label = ctk.CTkLabel(
            main_frame,
            text="キャラクターのコンセプト:",
            font=ctk.CTkFont(size=14)
        )
        concept_label.pack(anchor="w", pady=(0, 5))

        self.concept_entry = ctk.CTkEntry(
            main_frame,
            width=520,
            placeholder_text="例: 勇敢な騎士、天才魔法使い、気弱な学生"
        )
        self.concept_entry.pack(pady=(0, 15))

        # 追加情報
        additional_label = ctk.CTkLabel(
            main_frame,
            text="追加情報（任意）:",
            font=ctk.CTkFont(size=14)
        )
        additional_label.pack(anchor="w", pady=(0, 5))

        self.additional_text = ctk.CTkTextbox(
            main_frame,
            width=520,
            height=80
        )
        self.additional_text.pack(pady=(0, 20))

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

        generate_button = ctk.CTkButton(
            button_frame,
            text="生成",
            command=self._generate,
            width=120
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
        self.geometry("300x100")
        self.resizable(False, False)

        # モーダルにする
        self.transient(parent)

        # メッセージ
        label = ctk.CTkLabel(
            self,
            text=message,
            font=ctk.CTkFont(size=14)
        )
        label.pack(pady=20)

        # プログレスバー
        self.progressbar = ctk.CTkProgressBar(self, width=250)
        self.progressbar.pack(pady=10)
        self.progressbar.set(0)
        self.progressbar.start()

        # ウィンドウを中央に配置
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (300 // 2)
        y = (self.winfo_screenheight() // 2) - (100 // 2)
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
