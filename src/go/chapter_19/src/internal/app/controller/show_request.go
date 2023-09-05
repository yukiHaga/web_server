package controller

import (
	"github.com/yukiHaga/web_server/src/internal/app/view"
	"github.com/yukiHaga/web_server/src/pkg/henagin/http"
	"github.com/yukiHaga/web_server/src/pkg/web/utils"
)

type ShowRequest struct{}

func NewShowRequest() *ShowRequest {
	return &ShowRequest{}
}

func (c *ShowRequest) Action(request *http.Request) *http.Response {
	body := view.Render(
		"src/internal/app/view/templates/show_request.html",
		[]any{
			request.Method,
			request.TargetPath,
			request.HttpVersion,
			utils.PFormatForHeader(request.Headers),
			string(request.Body),
		},
	)

	return http.NewResponse(
		http.VersionsFor11,
		http.StatusSuccessCode,
		http.StatusReasonOk,
		request.TargetPath,
		body,
	)
}
