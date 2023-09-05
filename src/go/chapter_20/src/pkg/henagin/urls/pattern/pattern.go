package pattern

import (
	"github.com/yukiHaga/web_server/src/internal/app/controller"
)

type URLPattern struct {
	Pattern    string
	Controller controller.Controller
}

func NewURLPattern(pattern string, controller controller.Controller) *URLPattern {
	return &URLPattern{
		Pattern:    pattern,
		Controller: controller,
	}
}
