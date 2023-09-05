package constants

import (
	"fmt"
	"os"
	"path"
	"path/filepath"
)

func GetBaseDir() (string, error) {
	// カレントディレクトリの取得
	currentDir, err := os.Getwd()
	if err != nil {
		fmt.Println("カレントディレクトリを取得できませんでした:", err)
		return "", err
	}

	// 絶対パスの取得
	BASE_DIR, err := filepath.Abs(currentDir)
	if err != nil {
		fmt.Println("絶対パスを取得できませんでした:", err)
		return "", err
	}

	return BASE_DIR, nil
}

func GetStaticRoot() (string, error) {
	BASE_DIR, err := GetBaseDir()
	if err != nil {
		return "", err
	}

	return path.Join(BASE_DIR, "src", "static"), nil
}
