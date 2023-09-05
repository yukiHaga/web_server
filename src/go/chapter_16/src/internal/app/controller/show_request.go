package controller

import (
	"github.com/yukiHaga/web_server/src/internal/app/view"
	"github.com/yukiHaga/web_server/src/pkg/http"
	"github.com/yukiHaga/web_server/src/pkg/web/utils"
)

func ShowRequest(request *http.Request) *http.Response {
	view := view.ShowRequest(
		request.Method,
		request.TargetPath,
		request.HttpVersion,
		utils.PFormatForHeader(request.Headers),
		string(request.Body),
	)
	body := []byte(view)

	return http.NewResponse(
		http.VersionsFor11,
		http.StatusSuccessCode,
		http.StatusReasonOk,
		request.TargetPath,
		body,
	)
}
