"""
Story Generator
Gemini APIを使用した物語生成デスクトップアプリケーション

起動方法:
    python app/main.py
"""
import sys
import os

# プロジェクトルートをパスに追加
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.gui.main_window import MainWindow


def main():
    """アプリケーションのエントリーポイント"""
    try:
        app = MainWindow()
        app.mainloop()
    except Exception as e:
        print(f"アプリケーション起動エラー: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
