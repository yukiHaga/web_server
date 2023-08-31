from typing import Callable, Optional
from henango.http.request import HTTPRequest
from henango.http.response import HTTPResponse
from henango.views.static import static
from urls import url_patterns


class URLResolver:
    def resolve(self, request: HTTPRequest) -> Optional[Callable[[HTTPRequest], HTTPResponse]]:
        """
        URL解決を行う
        pathにマッチするURLパターンが存在した場合、対応するviewを返す
        存在しなかった場合、Noneを返す
        """
        for url_pattern in url_patterns:
            match = url_pattern.match(request.path)
            if match:
                request.params.update(match.groupdict())
                return url_pattern.view

        # 静的ファイルに関する処理のインターフェースをview関数と同じに揃えたことで、このように他のviewと同じように扱えるようになりました。
        return static
