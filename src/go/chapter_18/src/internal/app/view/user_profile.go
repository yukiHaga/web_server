package view

import "fmt"

func UserProfile(id string) string {
	return fmt.Sprintf(
		`<!doctype html>
		<html lang="ja">
		<head>
		  <meta charset="UTF-8">
		  <title>HenaServer: now</title>
		</head>
		<body>
		  <h1>ようこそ。ユーザー: %vさん</h1>
		</body>
		</html>`,
		id,
	)
}
