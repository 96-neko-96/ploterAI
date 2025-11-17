"""
Gemini APIクライアント
物語生成、キャラクター生成、世界観生成を管理
"""
import google.generativeai as genai
from typing import Dict, List, Optional, Any


class GeminiClient:
    """Gemini APIとの通信を管理するクラス"""

    def __init__(self, api_key: str, model: str = 'gemini-2.0-flash-exp'):
        """
        初期化

        Args:
            api_key: Gemini APIキー
            model: 使用するモデル名
        """
        genai.configure(api_key=api_key)
        self.model_name = model
        self.model = None
        self._initialize_model()

    def _initialize_model(self):
        """モデルの初期化"""
        try:
            self.model = genai.GenerativeModel(self.model_name)
        except Exception as e:
            raise Exception(f"モデルの初期化に失敗しました: {e}")

    def test_connection(self) -> bool:
        """
        API接続テスト

        Returns:
            接続成功かどうか
        """
        try:
            response = self.model.generate_content("こんにちは")
            return response.text is not None
        except Exception:
            return False

    def generate_character(self, concept: str, additional_info: str = "") -> Dict[str, str]:
        """
        キャラクター設定の生成

        Args:
            concept: キャラクターのコンセプト
            additional_info: 追加情報

        Returns:
            生成されたキャラクター情報
        """
        prompt = f"""
以下のコンセプトに基づいて、魅力的なキャラクター設定を作成してください。

コンセプト: {concept}
追加情報: {additional_info}

以下の項目について、詳細に記述してください:

1. 名前: キャラクターの名前（ふりがな付き）
2. 性格: 主な性格特性、価値観、行動パターン
3. 外見: 身長、体格、髪型、服装、特徴的な外見
4. 背景・経歴: 生い立ち、過去の出来事、現在の状況
5. 特技・能力: 得意なこと、特殊な能力、スキル
6. 口調・話し方: セリフの特徴、よく使う言葉、話し方の癖
7. 人間関係: 家族、友人、恋人、ライバルなど
8. 目標・動機: 何を目指しているか、行動の原動力

各項目を詳しく、具体的に記述してください。キャラクターが生き生きと感じられるように、細かなディテールも含めてください。

出力は以下のJSON形式で返してください（JSON以外の文字は含めないでください）:
{{
  "name": "名前",
  "personality": "性格の説明",
  "appearance": "外見の説明",
  "background": "背景・経歴の説明",
  "skills": "特技・能力の説明",
  "speech": "口調・話し方の説明",
  "relationships": "人間関係の説明",
  "goals": "目標・動機の説明"
}}
"""
        try:
            response = self.model.generate_content(prompt)
            text = response.text.strip()

            # JSONマーカーの除去
            if text.startswith("```json"):
                text = text[7:]
            if text.startswith("```"):
                text = text[3:]
            if text.endswith("```"):
                text = text[:-3]
            text = text.strip()

            import json
            character_data = json.loads(text)
            return character_data

        except Exception as e:
            raise Exception(f"キャラクター生成に失敗しました: {e}")

    def generate_world(self, genre: str, keywords: str) -> Dict[str, str]:
        """
        世界観設定の生成

        Args:
            genre: ジャンル（ファンタジー、SF、現代など）
            keywords: キーワード

        Returns:
            生成された世界観情報
        """
        prompt = f"""
以下の情報に基づいて、魅力的な世界観設定を作成してください。

ジャンル: {genre}
キーワード: {keywords}

以下の項目について、詳細に記述してください:

1. 世界観名: この世界の名称
2. 時代設定: いつの時代か（過去、現代、未来など）
3. 概要・説明: 世界全体の概要と特徴
4. 地理・環境: 地形、気候、主要な場所
5. 社会体制: 政治体制、経済システム、階級構造
6. 特殊ルール: 魔法、科学技術、超常現象など
7. 文化・習慣: 宗教、祭り、慣習、価値観
8. 歴史・背景: 重要な歴史的出来事、伝説

各項目を詳しく、具体的に記述してください。この世界が実在するかのように、リアリティのある設定にしてください。

出力は以下のJSON形式で返してください（JSON以外の文字は含めないでください）:
{{
  "name": "世界観名",
  "era": "時代設定",
  "overview": "概要・説明",
  "geography": "地理・環境",
  "society": "社会体制",
  "special_rules": "特殊ルール",
  "culture": "文化・習慣",
  "history": "歴史・背景"
}}
"""
        try:
            response = self.model.generate_content(prompt)
            text = response.text.strip()

            # JSONマーカーの除去
            if text.startswith("```json"):
                text = text[7:]
            if text.startswith("```"):
                text = text[3:]
            if text.endswith("```"):
                text = text[:-3]
            text = text.strip()

            import json
            world_data = json.loads(text)
            return world_data

        except Exception as e:
            raise Exception(f"世界観生成に失敗しました: {e}")

    def generate_plot(
        self,
        title: str,
        overview: str,
        characters: List[Dict[str, Any]],
        world_setting: Dict[str, Any],
        writing_style: Dict[str, str]
    ) -> str:
        """
        プロット生成（第1段階：500-1000文字）

        Args:
            title: シーンタイトル
            overview: シーン概要
            characters: 使用するキャラクター情報
            world_setting: 世界観設定
            writing_style: 文体スタイル

        Returns:
            生成されたプロット
        """
        # キャラクター情報の整形
        character_info = self._format_characters(characters)
        world_info = self._format_world(world_setting)
        style_info = self._format_style(writing_style)

        prompt = f"""
以下の情報を基に、物語のプロット（あらすじ）を500〜1000文字で作成してください。

【シーン情報】
タイトル: {title}
概要: {overview}

【キャラクター情報】
{character_info}

【世界観設定】
{world_info}

【文体スタイル】
{style_info}

プロットには以下の要素を含めてください:
- シーンの導入
- 主要な出来事・転換点
- キャラクター間の関係性や葛藤
- シーンの結末または次への展開

500〜1000文字で、簡潔かつ魅力的なプロットを作成してください。
"""
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            raise Exception(f"プロット生成に失敗しました: {e}")

    def expand_to_medium(
        self,
        plot: str,
        title: str,
        characters: List[Dict[str, Any]],
        world_setting: Dict[str, Any],
        writing_style: Dict[str, str]
    ) -> str:
        """
        中編化（第2段階：2000-3000文字）

        Args:
            plot: 元のプロット
            title: シーンタイトル
            characters: キャラクター情報
            world_setting: 世界観設定
            writing_style: 文体スタイル

        Returns:
            拡張された中編
        """
        character_info = self._format_characters(characters)
        world_info = self._format_world(world_setting)
        style_info = self._format_style(writing_style)

        prompt = f"""
以下のプロットを2000〜3000文字の中編に拡張してください。

【元のプロット】
{plot}

【シーンタイトル】
{title}

【キャラクター情報】
{character_info}

【世界観設定】
{world_info}

【文体スタイル】
{style_info}

拡張時には以下の要素を追加してください:
- 詳細な情景描写（場所、時間、雰囲気）
- 登場人物の感情描写（心情、表情、仕草）
- 会話・セリフ（キャラクターの個性が出る自然な会話）
- 細かな行動描写（動き、反応、変化）
- 五感に訴える表現（視覚、聴覚、触覚、嗅覚、味覚）

2000〜3000文字で、読者を引き込む豊かな描写の物語を作成してください。
"""
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            raise Exception(f"中編化に失敗しました: {e}")

    def expand_to_long(
        self,
        medium_story: str,
        title: str,
        characters: List[Dict[str, Any]],
        world_setting: Dict[str, Any],
        writing_style: Dict[str, str]
    ) -> str:
        """
        長編化（第3段階：5000文字以上）

        Args:
            medium_story: 中編の物語
            title: シーンタイトル
            characters: キャラクター情報
            world_setting: 世界観設定
            writing_style: 文体スタイル

        Returns:
            拡張された長編
        """
        character_info = self._format_characters(characters)
        world_info = self._format_world(world_setting)
        style_info = self._format_style(writing_style)

        prompt = f"""
以下の中編を5000文字以上の長編に拡張してください。

【中編】
{medium_story}

【シーンタイトル】
{title}

【キャラクター情報】
{character_info}

【世界観設定】
{world_info}

【文体スタイル】
{style_info}

拡張時には以下の要素を追加してください:
- 内面描写の深掘り（キャラクターの思考、記憶、葛藤）
- 会話の充実（より自然で長い会話、やりとりの詳細）
- 場面転換の丁寧な描写（時間や場所の移り変わり）
- サブプロット（副次的なエピソードや伏線）
- 伏線・細かな描写（後につながる要素、世界観の詳細）
- 読者を引き込む表現技法（比喩、対比、象徴など）

5000文字以上で、読み応えのある本格的な物語を作成してください。
文学的で完成度の高い作品に仕上げてください。
"""
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            raise Exception(f"長編化に失敗しました: {e}")

    def _format_characters(self, characters: List[Dict[str, Any]]) -> str:
        """キャラクター情報を整形"""
        if not characters:
            return "なし"

        formatted = []
        for char in characters:
            char_text = f"名前: {char.get('name', '不明')}\n"
            char_text += f"性格: {char.get('personality', '不明')}\n"
            char_text += f"外見: {char.get('appearance', '不明')}\n"
            char_text += f"口調: {char.get('speech', '不明')}"
            formatted.append(char_text)

        return "\n\n".join(formatted)

    def _format_world(self, world_setting: Dict[str, Any]) -> str:
        """世界観情報を整形"""
        if not world_setting:
            return "特に指定なし"

        formatted = f"世界観: {world_setting.get('name', '不明')}\n"
        formatted += f"時代: {world_setting.get('era', '不明')}\n"
        formatted += f"概要: {world_setting.get('overview', '不明')}\n"
        formatted += f"特殊ルール: {world_setting.get('special_rules', '不明')}"

        return formatted

    def _format_style(self, writing_style: Dict[str, str]) -> str:
        """文体スタイルを整形"""
        formatted = f"視点: {writing_style.get('perspective', '三人称')}\n"
        formatted += f"時制: {writing_style.get('tense', '過去形')}\n"
        formatted += f"トーン: {writing_style.get('tone', '標準')}\n"
        formatted += f"描写レベル: {writing_style.get('description_level', '中程度')}\n"
        formatted += f"会話スタイル: {writing_style.get('dialogue_style', '標準')}"

        return formatted

    def update_generation_config(self, temperature: float, max_tokens: int, top_p: float):
        """
        生成パラメータの更新

        Args:
            temperature: 温度パラメータ
            max_tokens: 最大トークン数
            top_p: Top-pサンプリング
        """
        generation_config = genai.GenerationConfig(
            temperature=temperature,
            max_output_tokens=max_tokens,
            top_p=top_p
        )
        self.model = genai.GenerativeModel(self.model_name, generation_config=generation_config)
