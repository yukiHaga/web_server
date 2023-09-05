package controller

import (
	"time"

	"github.com/leekchan/timeutil"
	"github.com/yukiHaga/web_server/src/internal/app/view"
	"github.com/yukiHaga/web_server/src/pkg/henagin/http"
)

func Now(request *http.Request) *http.Response {
	t := time.Now()
	formatedTime := timeutil.Strftime(&t, "%a, %d %b %Y %H:%M:%S")
	view := view.Now(formatedTime)
	body := []byte(view)

	return http.NewResponse(
		http.VersionsFor11,
		http.StatusSuccessCode,
		http.StatusReasonOk,
		request.TargetPath,
		body,
	)
}
