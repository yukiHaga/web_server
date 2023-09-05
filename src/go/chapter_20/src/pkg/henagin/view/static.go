package view

import (
	"os"
	"path"
	"strings"

	"github.com/yukiHaga/web_server/src/internal/app/config/settings"
	"github.com/yukiHaga/web_server/src/pkg/henagin/http"
)

type View struct{}

// lstripの処理は何の目的で行われているのか、その目的を関数やメソッドにする
// 静的ファイルを返す処理
func (v View) Action(request *http.Request) *http.Response {
	STATIC_ROOT, _ := settings.GetStaticRoot()
	targetFile := strings.TrimPrefix(request.TargetPath, "/")
	responseBody, err := os.ReadFile(path.Join(STATIC_ROOT, targetFile))
	if err != nil {
		responseBody, _ = os.ReadFile(path.Join(STATIC_ROOT, "404.html"))
		return http.NewResponse(
			http.VersionsFor11,
			http.StatusNotFoundCode,
			http.StatusReasonNotFound,
			request.TargetPath,
			responseBody,
		)
	}
	return http.NewResponse(
		http.VersionsFor11,
		http.StatusSuccessCode,
		http.StatusReasonOk,
		request.TargetPath,
		responseBody,
	)
}
