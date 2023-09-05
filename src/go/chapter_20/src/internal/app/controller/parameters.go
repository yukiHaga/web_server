package controller

import (
	"fmt"
	"net/url"
	"os"
	"path"

	"github.com/yukiHaga/web_server/src/internal/app/config/settings"
	"github.com/yukiHaga/web_server/src/internal/app/view"
	"github.com/yukiHaga/web_server/src/pkg/henagin/http"
)

type Parameters struct{}

func NewParameters() *Parameters {
	return &Parameters{}
}

func (c *Parameters) Action(request *http.Request) *http.Response {
	STATIC_ROOT, _ := settings.GetStaticRoot()
	var body []byte
	var statusCode string
	var statusReasonPhrase string

	if request.Method == http.Get {
		body, _ = os.ReadFile(path.Join(STATIC_ROOT, "405.html"))
		statusCode = http.StatusMethodNotAllowedCode
		statusReasonPhrase = http.StatusReasonMethodNotAllowed
	} else if request.Method == http.Post {
		// 多分ファイルの変換処理でミスっているかも
		// このパースの精度が安定しない。pythonのやり方の方が安定していた。
		// 使うメソッドを間違えたかな
		postParams, err := url.ParseQuery(string(request.Body))
		if err != nil {
			fmt.Printf("fail to parse post params: %v\n", err)
			body, _ := os.ReadFile(path.Join(STATIC_ROOT, "500.html"))
			statusCode = http.StatusInternalServerErrorCode
			statusReasonPhrase = http.StatusReasonInternalServerError
			return http.NewResponse(
				http.VersionsFor11,
				statusCode,
				statusReasonPhrase,
				request.TargetPath,
				body,
			)
		}

		formatedPostParams := ""
		for key, value := range postParams {
			formatedPostParams += fmt.Sprintf("%s: %v\r\n", key, value)
		}

		body = view.Render("src/internal/app/view/templates/parameters.html", formatedPostParams)
		statusCode = http.StatusSuccessCode
		statusReasonPhrase = http.StatusReasonOk
	}

	return http.NewResponse(
		http.VersionsFor11,
		statusCode,
		statusReasonPhrase,
		request.TargetPath,
		body,
	)
}
