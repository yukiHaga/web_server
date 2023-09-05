package controller

import (
	"net/url"

	"github.com/yukiHaga/web_server/src/internal/app/view"
	"github.com/yukiHaga/web_server/src/pkg/henagin/http"
)

type MyPage struct{}

func NewMyPage() *MyPage {
	return &MyPage{}
}

func (c *MyPage) Action(request *http.Request) *http.Response {
	if cookie, isThere := request.GetCookieByName("email"); isThere {
		email, _ := url.QueryUnescape(cookie.Value)
		body := view.Render("src/internal/app/view/templates/my_page.html", email)
		return http.NewResponse(
			http.VersionsFor11,
			http.StatusSuccessCode,
			http.StatusReasonOk,
			request.TargetPath,
			body,
		)
	} else {
		response := http.NewResponse(
			http.VersionsFor11,
			http.StatusRedirectCode,
			http.StatusReasonRedirect,
			request.TargetPath,
			[]byte{},
		)
		response.SetHeader("Location", "/login_form.html")
		return response
	}
}
