#!/bin/bash

# 遍历当前目录下的所有文件（不包括目录）
find . -type f -name "*:*" | while read file; do
    # 使用sed命令生成新文件名，将冒号替换为下划线
    newname=$(echo "$file" | sed 's/:/_/g')
    # 移动（重命名）文件
    mv "$file" "$newname"
done

