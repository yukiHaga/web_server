package config

import (
	"github.com/yukiHaga/web_server/src/internal/app/controller"
)

var UrlController = map[string]controller.Controller{
	"/now":          controller.Now,
	"/show_request": controller.ShowRequest,
	"/parameters":   controller.ShowRequest,
}
