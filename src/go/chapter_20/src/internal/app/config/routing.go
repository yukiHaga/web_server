package config

import (
	"github.com/yukiHaga/web_server/src/internal/app/controller"
	// 循環インポートだるいな
	"github.com/yukiHaga/web_server/src/pkg/henagin/urls/pattern"
)

// var Routing = map[string]controller.Controller{
// 	"/now":               controller.NewNow(),
// 	"/show_request":      controller.NewShowRequest(),
// 	"/parameters":        controller.NewParameters(),
// 	"/users/:id/profile": controller.NewUserProfile(),
// }

// 本当はメソッドを使う構造にしたい
var Routing = []*pattern.URLPattern{
	pattern.NewURLPattern("/now", controller.NewNow()),
	pattern.NewURLPattern("/show_request", controller.NewShowRequest()),
	pattern.NewURLPattern("/parameters", controller.NewParameters()),
	pattern.NewURLPattern("/users/:id/profile", controller.NewUserProfile()),
	pattern.NewURLPattern("/cookie_request", controller.NewCookieRequest()),
	pattern.NewURLPattern("/login", controller.NewLogin()),
	pattern.NewURLPattern("/mypage", controller.NewMyPage()),
}

// // URLパラメータを扱うのでこっちのデータ構造を採用した
// var Router = []controller.Action{
// 	get("/now", controller.Now{}),
// 	get("/show_request", controller.ShowRequest{}),
// 	get("/parameters", controller.Parameters{}),
// 	// get("/users/:id/profile", controller.UserProfile{}),
// }

// func get(path string, controller controller.Controller) controller.Action {
// 	return controller.Index
// }
