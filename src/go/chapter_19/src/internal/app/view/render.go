package view

import (
	"fmt"
	"os"
	"regexp"
)

// テンプレートエンジンのコア機能
// 呼び出し時にキーワード引数で渡せたら最高だけど、なんかめんどくさそうだからやめた。ビューで使われる変数の順番を覚えていないと使えないのがネック
func Render(templatePath string, context []any) []byte {
	bytes, _ := os.ReadFile(templatePath)
	fileContent := string(bytes)

	re := regexp.MustCompile(`{(.+?)}`)
	// fileContentの中の全ての変数展開を%vにリプレイスする
	replacedFileContent := re.ReplaceAllString(fileContent, "%v")
	view := fmt.Sprintf(replacedFileContent, context...)
	body := []byte(view)

	return body
}
