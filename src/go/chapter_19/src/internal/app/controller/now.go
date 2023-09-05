package controller

import (
	"time"

	"github.com/leekchan/timeutil"
	"github.com/yukiHaga/web_server/src/internal/app/view"
	"github.com/yukiHaga/web_server/src/pkg/henagin/http"
)

type Now struct{}

func NewNow() *Now {
	return &Now{}
}

func (c *Now) Action(request *http.Request) *http.Response {
	t := time.Now()
	formatedTime := timeutil.Strftime(&t, "%a, %d %b %Y %H:%M:%S")
	body := view.Render("src/internal/app/view/templates/now.html", []any{formatedTime})

	return http.NewResponse(
		http.VersionsFor11,
		http.StatusSuccessCode,
		http.StatusReasonOk,
		request.TargetPath,
		body,
	)
}
