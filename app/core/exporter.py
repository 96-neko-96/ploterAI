"""
エクスポート機能
TXT、Markdown、PDF形式でのエクスポートを管理
"""
import os
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_LEFT, TA_CENTER
import markdown


class Exporter:
    """エクスポート機能を管理するクラス"""

    def __init__(self):
        self._setup_pdf_fonts()

    def _setup_pdf_fonts(self):
        """PDF用日本語フォントの設定"""
        try:
            # Windowsの場合
            if os.name == 'nt':
                font_paths = [
                    'C:/Windows/Fonts/msgothic.ttc',  # MSゴシック
                    'C:/Windows/Fonts/msmincho.ttc',  # MS明朝
                ]
                for font_path in font_paths:
                    if os.path.exists(font_path):
                        pdfmetrics.registerFont(TTFont('Japanese', font_path))
                        return
            # Linuxの場合
            else:
                font_paths = [
                    '/usr/share/fonts/truetype/takao-gothic/TakaoPGothic.ttf',
                    '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',
                ]
                for font_path in font_paths:
                    if os.path.exists(font_path):
                        pdfmetrics.registerFont(TTFont('Japanese', font_path))
                        return

            # デフォルトフォント（日本語が正しく表示されない可能性あり）
            self.japanese_font = 'Helvetica'
        except Exception:
            self.japanese_font = 'Helvetica'
        else:
            self.japanese_font = 'Japanese'

    def export_to_txt(
        self,
        file_path: str,
        scenes: List[Dict[str, Any]],
        include_title: bool = True,
        include_characters: bool = False,
        include_world: bool = False,
        characters: List[Dict[str, str]] = None,
        world_settings: Dict[str, str] = None,
        project_name: str = ""
    ):
        """
        TXT形式でエクスポート

        Args:
            file_path: 保存先パス
            scenes: エクスポートするシーン
            include_title: タイトルを含めるか
            include_characters: キャラクター情報を含めるか
            include_world: 世界観設定を含めるか
            characters: キャラクター情報
            world_settings: 世界観設定
            project_name: プロジェクト名
        """
        content = []

        # タイトル
        if include_title and project_name:
            content.append(f"{'=' * 60}")
            content.append(project_name)
            content.append(f"{'=' * 60}")
            content.append("")

        # キャラクター情報
        if include_characters and characters:
            content.append("【キャラクター情報】")
            content.append("")
            for char in characters:
                content.append(f"■ {char.get('name', '不明')}")
                content.append(f"性格: {char.get('personality', '不明')}")
                content.append(f"外見: {char.get('appearance', '不明')}")
                content.append("")
            content.append(f"{'=' * 60}")
            content.append("")

        # 世界観設定
        if include_world and world_settings:
            content.append("【世界観設定】")
            content.append("")
            content.append(f"世界観名: {world_settings.get('name', '不明')}")
            content.append(f"時代: {world_settings.get('era', '不明')}")
            content.append(f"概要: {world_settings.get('overview', '不明')}")
            content.append("")
            content.append(f"{'=' * 60}")
            content.append("")

        # シーン
        for i, scene in enumerate(scenes, 1):
            content.append(f"【第{i}話: {scene.get('title', '無題')}】")
            content.append("")
            content.append(scene.get('content', ''))
            content.append("")
            content.append(f"{'=' * 60}")
            content.append("")

        # 作成日時
        content.append(f"作成日時: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}")

        # ファイルに書き込み
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(content))

    def export_to_markdown(
        self,
        file_path: str,
        scenes: List[Dict[str, Any]],
        include_title: bool = True,
        include_characters: bool = False,
        include_world: bool = False,
        characters: List[Dict[str, str]] = None,
        world_settings: Dict[str, str] = None,
        project_name: str = ""
    ):
        """
        Markdown形式でエクスポート

        Args:
            file_path: 保存先パス
            scenes: エクスポートするシーン
            include_title: タイトルを含めるか
            include_characters: キャラクター情報を含めるか
            include_world: 世界観設定を含めるか
            characters: キャラクター情報
            world_settings: 世界観設定
            project_name: プロジェクト名
        """
        content = []

        # タイトル
        if include_title and project_name:
            content.append(f"# {project_name}")
            content.append("")

        # キャラクター情報
        if include_characters and characters:
            content.append("## キャラクター情報")
            content.append("")
            for char in characters:
                content.append(f"### {char.get('name', '不明')}")
                content.append("")
                content.append(f"**性格**: {char.get('personality', '不明')}")
                content.append("")
                content.append(f"**外見**: {char.get('appearance', '不明')}")
                content.append("")
                content.append(f"**背景**: {char.get('background', '不明')}")
                content.append("")
            content.append("---")
            content.append("")

        # 世界観設定
        if include_world and world_settings:
            content.append("## 世界観設定")
            content.append("")
            content.append(f"**世界観名**: {world_settings.get('name', '不明')}")
            content.append("")
            content.append(f"**時代**: {world_settings.get('era', '不明')}")
            content.append("")
            content.append(f"**概要**: {world_settings.get('overview', '不明')}")
            content.append("")
            content.append("---")
            content.append("")

        # シーン
        for i, scene in enumerate(scenes, 1):
            content.append(f"## 第{i}話: {scene.get('title', '無題')}")
            content.append("")
            content.append(scene.get('content', ''))
            content.append("")
            content.append("---")
            content.append("")

        # 作成日時
        content.append(f"*作成日時: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}*")

        # ファイルに書き込み
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(content))

    def export_to_pdf(
        self,
        file_path: str,
        scenes: List[Dict[str, Any]],
        include_title: bool = True,
        include_characters: bool = False,
        include_world: bool = False,
        characters: List[Dict[str, str]] = None,
        world_settings: Dict[str, str] = None,
        project_name: str = ""
    ):
        """
        PDF形式でエクスポート

        Args:
            file_path: 保存先パス
            scenes: エクスポートするシーン
            include_title: タイトルを含めるか
            include_characters: キャラクター情報を含めるか
            include_world: 世界観設定を含めるか
            characters: キャラクター情報
            world_settings: 世界観設定
            project_name: プロジェクト名
        """
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)

        # PDFドキュメントの作成
        doc = SimpleDocTemplate(
            file_path,
            pagesize=A4,
            topMargin=20 * mm,
            bottomMargin=20 * mm,
            leftMargin=20 * mm,
            rightMargin=20 * mm
        )

        # スタイルの設定
        styles = self._create_pdf_styles()
        story = []

        # タイトル
        if include_title and project_name:
            story.append(Paragraph(project_name, styles['Title']))
            story.append(Spacer(1, 12))

        # キャラクター情報
        if include_characters and characters:
            story.append(Paragraph("キャラクター情報", styles['Heading1']))
            story.append(Spacer(1, 6))

            for char in characters:
                story.append(Paragraph(char.get('name', '不明'), styles['Heading2']))
                story.append(Spacer(1, 3))

                text = f"性格: {char.get('personality', '不明')}"
                story.append(Paragraph(text, styles['Normal']))
                story.append(Spacer(1, 3))

                text = f"外見: {char.get('appearance', '不明')}"
                story.append(Paragraph(text, styles['Normal']))
                story.append(Spacer(1, 6))

            story.append(PageBreak())

        # 世界観設定
        if include_world and world_settings:
            story.append(Paragraph("世界観設定", styles['Heading1']))
            story.append(Spacer(1, 6))

            text = f"世界観名: {world_settings.get('name', '不明')}"
            story.append(Paragraph(text, styles['Normal']))
            story.append(Spacer(1, 3))

            text = f"時代: {world_settings.get('era', '不明')}"
            story.append(Paragraph(text, styles['Normal']))
            story.append(Spacer(1, 3))

            text = f"概要: {world_settings.get('overview', '不明')}"
            story.append(Paragraph(text, styles['Normal']))
            story.append(Spacer(1, 6))

            story.append(PageBreak())

        # シーン
        for i, scene in enumerate(scenes, 1):
            title = f"第{i}話: {scene.get('title', '無題')}"
            story.append(Paragraph(title, styles['Heading1']))
            story.append(Spacer(1, 6))

            # 本文を段落に分割
            content = scene.get('content', '')
            paragraphs = content.split('\n\n')

            for para in paragraphs:
                if para.strip():
                    story.append(Paragraph(para.strip(), styles['Normal']))
                    story.append(Spacer(1, 6))

            if i < len(scenes):
                story.append(PageBreak())

        # 作成日時
        story.append(Spacer(1, 12))
        date_text = f"作成日時: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}"
        story.append(Paragraph(date_text, styles['Footer']))

        # PDFの生成
        try:
            doc.build(story)
        except Exception as e:
            raise Exception(f"PDFの生成に失敗しました: {e}")

    def _create_pdf_styles(self):
        """PDF用のスタイルを作成"""
        styles = getSampleStyleSheet()

        # タイトルスタイル
        styles.add(ParagraphStyle(
            name='Title',
            parent=styles['Title'],
            fontName=self.japanese_font,
            fontSize=24,
            alignment=TA_CENTER,
            spaceAfter=20
        ))

        # 見出し1
        styles.add(ParagraphStyle(
            name='Heading1',
            parent=styles['Heading1'],
            fontName=self.japanese_font,
            fontSize=18,
            spaceAfter=12
        ))

        # 見出し2
        styles.add(ParagraphStyle(
            name='Heading2',
            parent=styles['Heading2'],
            fontName=self.japanese_font,
            fontSize=14,
            spaceAfter=6
        ))

        # 本文
        styles.add(ParagraphStyle(
            name='Normal',
            parent=styles['Normal'],
            fontName=self.japanese_font,
            fontSize=10,
            leading=16,
            alignment=TA_LEFT
        ))

        # フッター
        styles.add(ParagraphStyle(
            name='Footer',
            parent=styles['Normal'],
            fontName=self.japanese_font,
            fontSize=8,
            alignment=TA_CENTER
        ))

        return styles
