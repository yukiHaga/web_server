import re
from re import Match
from typing import Callable, Optional
from henango.http.request import HTTPRequest
from henango.http.response import HTTPResponse


class URLPattern:
    pattern: str
    # Callable[[HTTPRequest], HTTPResponse]は関数を表す型注釈で、この場合はHTTPRequestインスタンスを受け取り、HTTPResponseを返す関数を意味します。
    view: Callable[[HTTPRequest], HTTPResponse]

    def __init__(self, pattern: str, view: Callable[[HTTPRequest], HTTPResponse]):
        self.pattern = pattern
        self.view = view

    # Optional[Match]は、「Matchインスタンス、またはNone」を表す型です。
    # url_patternとpathのマッチング判定をWorker内のメソッドでやっていたところを、url_patternオブジェクト自身にやらせるようにしました。
    # これで、WorkerはURLのマッチング方法について何も知らなくてよくなり、責務が軽くなりました。
    def match(self, path: str) -> Optional[Match]:
        """
        pathがURLパターンにマッチするかを判定
        マッチした場合は、Matchオブジェクトを返す。マッチしなかった場合はNoneを返す
        """

        re_pattern = re.sub(r"<(.+?)>", r"(?P<\1>[^/]+)", self.pattern)
        return re.match(re_pattern, path)
