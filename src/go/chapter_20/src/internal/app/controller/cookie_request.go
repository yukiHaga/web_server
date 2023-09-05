package controller

import (
	"fmt"
	"time"

	"github.com/leekchan/timeutil"
	"github.com/yukiHaga/web_server/src/internal/app/view"
	"github.com/yukiHaga/web_server/src/pkg/henagin/http"
)

type CookieRequest struct{}

func NewCookieRequest() *CookieRequest {
	return &CookieRequest{}
}

func (c *CookieRequest) Action(request *http.Request) *http.Response {
	body := view.Render("src/internal/app/view/templates/cookie_request.html")

	currentTime := time.Now()
	t := currentTime.Add(time.Hour)

	response := http.NewResponse(
		http.VersionsFor11,
		http.StatusSuccessCode,
		http.StatusReasonOk,
		request.TargetPath,
		body,
	)

	response.SetHeader(
		"Set-Cookie",
		fmt.Sprintf("hoge_fuga=first_Cookie; Expires=%v", timeutil.Strftime(&t, "%a, %d %b %Y %H:%M:%S")),
	)

	return response
}
