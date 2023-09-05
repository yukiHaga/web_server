package controller

import (
	"github.com/yukiHaga/web_server/src/internal/app/view"
	"github.com/yukiHaga/web_server/src/pkg/henagin/http"
)

type UserProfile struct{}

func NewUserProfile() *UserProfile {
	return &UserProfile{}
}

func (c *UserProfile) Action(request *http.Request) *http.Response {
	id := request.Params["id"]
	body := view.Render("src/internal/app/view/templates/user_profile.html", []any{id})

	return http.NewResponse(
		http.VersionsFor11,
		http.StatusSuccessCode,
		http.StatusReasonOk,
		request.TargetPath,
		body,
	)
}
