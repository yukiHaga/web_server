package controller

import (
	"fmt"
	"net/url"
	"os"
	"path"

	"github.com/yukiHaga/web_server/src/internal/app/config/settings"
	"github.com/yukiHaga/web_server/src/pkg/henagin/http"
)

type Login struct{}

func NewLogin() *Login {
	return &Login{}
}

func (c *Login) Action(request *http.Request) *http.Response {
	STATIC_ROOT, _ := settings.GetStaticRoot()
	var statusCode string
	var reasonPhrase string
	var body []byte
	cookieHeaders := map[string]string{}

	if request.Method == http.Get {
		body, _ = os.ReadFile(path.Join(STATIC_ROOT, "405.html"))
		statusCode = http.StatusMethodNotAllowedCode
		reasonPhrase = http.StatusReasonNotFound
	} else if request.Method == http.Post {
		// urlエンコードされたボディをデコードしたいなら、このメソッドを使えば良い。
		// ボディは元々バイトだけどstringにキャストするのは本当はあんま良くない。画像データとかのバイナリデータは文字列に変換できないから
		// 今回は画像を送らないから、特別にやっている
		// email=oceansthirteen7510@gmail.com&password=ocean&submit_name=送信
		// 多分画像が入っていないから、URLエンコード成功した
		decodedBody, _ := url.QueryUnescape(string(request.Body))
		// 正規表現使わなくて済む
		values, _ := url.ParseQuery(decodedBody)
		fmt.Println("values", values)
		cookieHeaders["email"] = url.QueryEscape(values.Get("email"))
		cookieHeaders["password"] = url.QueryEscape(values.Get("password"))
		statusCode = http.StatusRedirectCode
		reasonPhrase = http.StatusReasonRedirect
	}

	// headerがオプショナル引数ならどんなだけ楽か。
	response := http.NewResponse(
		http.VersionsFor11,
		statusCode,
		reasonPhrase,
		request.TargetPath,
		body,
	)

	if request.Method == http.Post {
		for key, value := range cookieHeaders {
			fmt.Println("key", key)
			fmt.Println("value", value)
			response.SetCookieHeader(fmt.Sprintf("%s=%s", key, value))
		}
		response.SetHeader("Location", "/mypage")
	}

	return response
}
