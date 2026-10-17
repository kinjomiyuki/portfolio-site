#!/usr/bin/env python3
"""
BLANC DE BLANC カードをポートフォリオに追加するスクリプト
"""
import sys
import base64
from pathlib import Path

def get_base64_image(image_path):
    """画像を base64 に変換"""
    try:
        with open(image_path, 'rb') as f:
            image_data = f.read()
        return base64.b64encode(image_data).decode('utf-8')
    except FileNotFoundError:
        print(f"エラー: 画像ファイルが見つかりません: {image_path}")
        sys.exit(1)

def create_card_html(image_base64):
    """カード HTML を生成"""
    card_html = f'''          <article class="work-card" data-category="web">
            <div class="work-thumb">
              <div class="work-thumb-inner">
                <img src="data:image/gif;base64,{image_base64}">
              </div>
              <div class="work-overlay">
                <a href="https://blanc-de-blanc-okinawa.netlify.app/" target="_blank" rel="noopener" class="work-detail-btn">詳細を見る →</a>
              </div>
            </div>
            <div class="work-info">
              <p class="work-category-tag">RESTAURANT BRAND</p>
              <h3 class="work-title">BLANC DE BLANC — ダイニングバー ブランドサイト</h3>
              <p class="work-desc">沖縄・那覇のラグジュアリーダイニングバー「BLANC DE BLANC」のブランドサイト。上質な空間とサービスを体験させるために、余白を活かしたミニマルデザインと高質感な画像で、ブランドの世界観を表現。</p>
              <div class="work-tags">
                <span>Web Design</span><span>Brand</span><span>Luxury</span>
              </div>
            </div>
          </article>'''
    return card_html

def add_card_to_portfolio(html_file, card_html):
    """ポートフォリオ HTML にカードを追加"""
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # 最後のカードの後に新しいカードを挿入
    # </article> の後の改行を探す
    insert_pos = content.rfind('</article>')
    if insert_pos == -1:
        print("エラー: ポートフォリオ HTML の構造が不正です")
        sys.exit(1)

    # </article> の直後の位置に挿入
    insert_pos = content.find('\n', insert_pos) + 1

    new_content = content[:insert_pos] + '\n' + card_html + content[insert_pos:]

    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(new_content)

    print(f"✅ カードを {html_file} に追加しました")

def main():
    # ポートフォリオディレクトリ
    portfolio_dir = Path(__file__).parent
    html_file = portfolio_dir / 'index.html'
    image_file = portfolio_dir / 'images' / 'blanc-hero.gif'

    # 画像があるか確認
    if not image_file.exists():
        print(f"エラー: 画像ファイルが見つかりません: {image_file}")
        print(f"画像を {image_file} に配置してください")
        sys.exit(1)

    # HTML ファイルがあるか確認
    if not html_file.exists():
        print(f"エラー: HTML ファイルが見つかりません: {html_file}")
        sys.exit(1)

    # 画像を base64 に変換
    print(f"📸 画像を base64 に変換中: {image_file}")
    image_base64 = get_base64_image(image_file)
    print(f"✅ 画像変換完了（{len(image_base64)} 文字）")

    # カード HTML を生成
    print("🎨 カード HTML を生成中...")
    card_html = create_card_html(image_base64)

    # ポートフォリオに追加
    print("📝 ポートフォリオに追加中...")
    add_card_to_portfolio(html_file, card_html)

    print("\n✨ 完了！ BLANC DE BLANC カードが追加されました")
    print(f"   URL: https://blanc-de-blanc-okinawa.netlify.app/")

if __name__ == '__main__':
    main()
