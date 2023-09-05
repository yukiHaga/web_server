package utils

import "fmt"

func PFormatForHeader(data map[string]string) string {
	formatedData := ""

	for key, value := range data {
		formatedData += fmt.Sprintf("%v: %v\r\n", key, value)
	}

	return formatedData
}
