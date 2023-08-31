from typing import Optional


class HTTPResponse:
    # これはインスタンス変数の型アノテーション
    # クラス変数として型アノテーションしたいならtyping.ClassVarを使う。
    # おそらくここで普通に変数定義して代入しちゃうと、それはクラス変数として扱われる。あくまで型だけ
    status_code: int
    content_type: Optional[str]
    body: bytes

    def __init__(self, status_code: int = 200, content_type: str = None, body: bytes = b""):
        self.status_code = status_code
        self.content_type = content_type
        self.body = body
