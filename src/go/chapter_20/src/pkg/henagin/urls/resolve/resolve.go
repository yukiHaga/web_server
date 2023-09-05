package resolve

import (
	"fmt"
	"regexp"

	"github.com/yukiHaga/web_server/src/internal/app/config"
	"github.com/yukiHaga/web_server/src/internal/app/controller"
	"github.com/yukiHaga/web_server/src/pkg/henagin/http"
	"github.com/yukiHaga/web_server/src/pkg/henagin/view"
)

type URLResolver struct{}

func NewURLResolver() *URLResolver {
	return &URLResolver{}
}

// URL解決を行う
// pathにマッチするURLパターンが存在した場合は、対応するviewを返す
// 存在しなかった場合は、static viewを返す
// 元々の戻り値の型は、controller.Controller, boolだった
func (r *URLResolver) Resolve(request *http.Request) controller.Controller {
	for _, pattern := range config.Routing {
		re := regexp.MustCompile(`:([^/]+)`)
		// urlパラメータが含まれているパスを見つける
		matches := re.FindAllStringSubmatch(pattern.Pattern, -1)

		if len(matches) > 0 {
			// keyは:idの場合は、id。:user_idの場合は、user_id。
			key := matches[0][1]
			// pathから正規表現パターンを作る
			rePattern := re.ReplaceAllString(pattern.Pattern, fmt.Sprintf("(?P<%s>[^/]+)", key))
			re = regexp.MustCompile(rePattern)
			match := re.FindAllStringSubmatch(request.TargetPath, -1)

			if len(match) > 0 {
				value := match[0][1]
				request.Params[key] = value

				return pattern.Controller
			}
		} else {
			if pattern.Pattern == request.TargetPath {
				return pattern.Controller
			}
		}
	}

	// return nil, false
	// ルーティングでマッチするパスがなかったら、静的ファイルを求めているかも。
	// なので、静的ファイルを返す
	return view.View{}
}
