"""
世界観ダイアログ
世界観設定の作成・編集・AI生成を管理
"""
import customtkinter as ctk
from tkinter import messagebox
from typing import Dict, Optional, Callable
import threading


class WorldDialog(ctk.CTkToplevel):
    """世界観ダイアログ"""

    def __init__(
        self,
        parent,
        world_data: Optional[Dict[str, str]] = None,
        ai_generate_callback: Optional[Callable] = None
    ):
        super().__init__(parent)

        self.world_data = world_data
        self.ai_generate_callback = ai_generate_callback
        self.result = None

        mode = "編集" if world_data else "作成"
        self.title(f"世界観{mode}")
        self.geometry("850x750")
        self.minsize(700, 600)  # 最小サイズを設定
        self.resizable(True, True)  # リサイズ可能に

        # モーダルにする
        self.transient(parent)
        self.grab_set()

        self._create_widgets()

        if world_data:
            self._load_world_data()

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

        # タイトル
        mode = "編集" if self.world_data else "作成"
        title_label = ctk.CTkLabel(
            main_frame,
            text=f"世界観{mode}",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.pack(pady=(0, 10))

        # AI生成ボタン
        if not self.world_data and self.ai_generate_callback:
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

        # 世界観名
        name_label = ctk.CTkLabel(
            scroll_frame,
            text="世界観名:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        name_label.pack(anchor="w", pady=(0, 5))

        self.name_entry = ctk.CTkEntry(
            scroll_frame,
            width=700,
            placeholder_text="世界観の名称"
        )
        self.name_entry.pack(pady=(0, 15))

        # 時代設定
        era_label = ctk.CTkLabel(
            scroll_frame,
            text="時代設定:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        era_label.pack(anchor="w", pady=(0, 5))

        self.era_entry = ctk.CTkEntry(
            scroll_frame,
            width=700,
            placeholder_text="例: 中世ファンタジー、現代、近未来"
        )
        self.era_entry.pack(pady=(0, 15))

        # 概要・説明
        overview_label = ctk.CTkLabel(
            scroll_frame,
            text="概要・説明:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        overview_label.pack(anchor="w", pady=(0, 5))

        self.overview_text = ctk.CTkTextbox(
            scroll_frame,
            width=700,
            height=100
        )
        self.overview_text.pack(pady=(0, 15))

        # 地理・環境
        geography_label = ctk.CTkLabel(
            scroll_frame,
            text="地理・環境:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        geography_label.pack(anchor="w", pady=(0, 5))

        self.geography_text = ctk.CTkTextbox(
            scroll_frame,
            width=700,
            height=80
        )
        self.geography_text.pack(pady=(0, 15))

        # 社会体制
        society_label = ctk.CTkLabel(
            scroll_frame,
            text="社会体制:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        society_label.pack(anchor="w", pady=(0, 5))

        self.society_text = ctk.CTkTextbox(
            scroll_frame,
            width=700,
            height=80
        )
        self.society_text.pack(pady=(0, 15))

        # 特殊ルール
        special_rules_label = ctk.CTkLabel(
            scroll_frame,
            text="特殊ルール:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        special_rules_label.pack(anchor="w", pady=(0, 5))

        self.special_rules_text = ctk.CTkTextbox(
            scroll_frame,
            width=700,
            height=80
        )
        self.special_rules_text.pack(pady=(0, 15))

        # 文化・習慣
        culture_label = ctk.CTkLabel(
            scroll_frame,
            text="文化・習慣:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        culture_label.pack(anchor="w", pady=(0, 5))

        self.culture_text = ctk.CTkTextbox(
            scroll_frame,
            width=700,
            height=80
        )
        self.culture_text.pack(pady=(0, 15))

        # 歴史・背景
        history_label = ctk.CTkLabel(
            scroll_frame,
            text="歴史・背景:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        history_label.pack(anchor="w", pady=(0, 5))

        self.history_text = ctk.CTkTextbox(
            scroll_frame,
            width=700,
            height=100
        )
        self.history_text.pack(pady=(0, 15))

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

    def _load_world_data(self):
        """世界観データを読み込み"""
        self.name_entry.insert(0, self.world_data.get('name', ''))
        self.era_entry.insert(0, self.world_data.get('era', ''))
        self.overview_text.insert("1.0", self.world_data.get('overview', ''))
        self.geography_text.insert("1.0", self.world_data.get('geography', ''))
        self.society_text.insert("1.0", self.world_data.get('society', ''))
        self.special_rules_text.insert("1.0", self.world_data.get('special_rules', ''))
        self.culture_text.insert("1.0", self.world_data.get('culture', ''))
        self.history_text.insert("1.0", self.world_data.get('history', ''))

    def _show_ai_generation(self):
        """AI生成ダイアログを表示"""
        ai_dialog = AIWorldDialog(self, self.ai_generate_callback)
        self.wait_window(ai_dialog)

        if ai_dialog.result:
            # 生成されたデータをフォームに入力
            self.name_entry.delete(0, "end")
            self.name_entry.insert(0, ai_dialog.result.get('name', ''))

            self.era_entry.delete(0, "end")
            self.era_entry.insert(0, ai_dialog.result.get('era', ''))

            self.overview_text.delete("1.0", "end")
            self.overview_text.insert("1.0", ai_dialog.result.get('overview', ''))

            self.geography_text.delete("1.0", "end")
            self.geography_text.insert("1.0", ai_dialog.result.get('geography', ''))

            self.society_text.delete("1.0", "end")
            self.society_text.insert("1.0", ai_dialog.result.get('society', ''))

            self.special_rules_text.delete("1.0", "end")
            self.special_rules_text.insert("1.0", ai_dialog.result.get('special_rules', ''))

            self.culture_text.delete("1.0", "end")
            self.culture_text.insert("1.0", ai_dialog.result.get('culture', ''))

            self.history_text.delete("1.0", "end")
            self.history_text.insert("1.0", ai_dialog.result.get('history', ''))

    def _save(self):
        """保存"""
        self.result = {
            'name': self.name_entry.get().strip(),
            'era': self.era_entry.get().strip(),
            'overview': self.overview_text.get("1.0", "end-1c").strip(),
            'geography': self.geography_text.get("1.0", "end-1c").strip(),
            'society': self.society_text.get("1.0", "end-1c").strip(),
            'special_rules': self.special_rules_text.get("1.0", "end-1c").strip(),
            'culture': self.culture_text.get("1.0", "end-1c").strip(),
            'history': self.history_text.get("1.0", "end-1c").strip()
        }

        self.destroy()

    def _cancel(self):
        """キャンセル"""
        self.result = None
        self.destroy()


class AIWorldDialog(ctk.CTkToplevel):
    """AI生成用ダイアログ"""

    def __init__(self, parent, ai_generate_callback):
        super().__init__(parent)

        self.ai_generate_callback = ai_generate_callback
        self.result = None

        self.title("AIで世界観生成")
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
            text="AIで世界観生成",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.pack(pady=(0, 20))

        # ジャンル
        genre_label = ctk.CTkLabel(
            main_frame,
            text="ジャンル:",
            font=ctk.CTkFont(size=14)
        )
        genre_label.pack(anchor="w", pady=(0, 5))

        self.genre_entry = ctk.CTkEntry(
            main_frame,
            width=520,
            placeholder_text="例: ファンタジー、SF、現代、歴史"
        )
        self.genre_entry.pack(pady=(0, 15))

        # キーワード
        keywords_label = ctk.CTkLabel(
            main_frame,
            text="キーワード:",
            font=ctk.CTkFont(size=14)
        )
        keywords_label.pack(anchor="w", pady=(0, 5))

        self.keywords_text = ctk.CTkTextbox(
            main_frame,
            width=520,
            height=80
        )
        self.keywords_text.pack(pady=(0, 20))

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
        genre = self.genre_entry.get().strip()

        if not genre:
            messagebox.showerror("エラー", "ジャンルを入力してください")
            return

        keywords = self.keywords_text.get("1.0", "end-1c").strip()

        # プログレスダイアログを表示
        from app.gui.character_dialog import ProgressDialog
        progress_dialog = ProgressDialog(self, "世界観を生成中...")

        def generate_thread():
            try:
                result = self.ai_generate_callback(genre, keywords)
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
