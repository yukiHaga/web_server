import os
import settings
# htmlファイルを読み込むときに、
# ファイルを開く (open())
# ファイルを読み込む (read())
# 変数を置き換えるためのメソッドを呼び出す (format())
# などの処理を毎回呼び出す必要がある。
# なので、rendererで抽象化した


def render(template_name: str, context: dict):
    template_path = os.path.join(settings.TEMPLATES_DIR, template_name)
    with open(template_path) as f:
        template = f.read()

    return template.format(**context)
