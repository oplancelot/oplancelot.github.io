---
title: Use the REST API to delete repositories on GitHub
weight: 3
date: 2023-07-06
description: 调用github api 批量删除github 仓库
# draft: true
categories: [shell]
tags: [shell,github,api]
---

https://docs.github.com/zh/rest/overview/resources-in-the-rest-api?apiVersion=2022-11-28

fork 的github repositories 太多了，一个个删除需要确认很多步骤。需要调用api处理

```
  #!/bin/bash

  set -e # 启用退出状态检查

  # 替换为您的 GitHub 用户名
  USERNAME="<YOUR_USERNAME>"

  # 替换为您的个人访问令牌
  #Personal access tokens
  ACCESS_TOKEN="<YOUR_ACCESS_TOKEN>"

  # 使用 GitHub API 获取存储库列表并提取完整的存储库名称
  # 详细参考https://docs.github.com/zh/rest/repos/repos?apiVersion=2022-11-28#list-repositories-for-a-user
  # 格式参考https://docs.github.com/zh/rest/guides/getting-started-with-the-rest-api?apiVersion=2022-11-28&tool=curl#using-query-parameters
  # 对于 curl 命令，向路径末尾添加 ?，然后采用 parameter_name=value 形式追加查询参数名称和值。 使用 & 分隔多个查询参数。

  # 设置每页显示的数量
  PER_PAGE=30

  #List repositories for a user
  # 获取第一页的存储库列表

  response=$(curl -s -I -H "Accept: application/vnd.github+json" -H "Authorization: Bearer $ACCESS_TOKEN" "https://api.github.com/users/$USERNAME/repos?per_page=$PER_PAGE&page=1")

  # 提取总页数
  link_header=$(echo "$response" | grep -iE 'Link:' | tr -d '\r')
  total_pages=$(echo "$link_header" | grep -oE '<[^>]+>; rel="last"' | sed -n 's/<\(.*\)>.*/\1/p' | grep -oE '&page=[0-9]+' | sed -n 's/&page=\([0-9]*\)/\1/p')

  # echo ${last_link}
  echo "总页数: $total_pages"

  # 生成临时文件名
  temp_file=$(mktemp /tmp/del_repos_XXXXXX)

  echo "临时文件名: $temp_file"

  # 保存存储库列表到临时文件中
  # 需要安装jq
  for ((page = 1; page <= $total_pages; page++)); do
    echo "正在处理第 $page 页..."
    repos=$(curl -s -H "Accept: application/vnd.github+json" -H "Authorization: Bearer $ACCESS_TOKEN" "https://api.github.com/users/$USERNAME/repos?per_page=$PER_PAGE&page=$page" | jq .[].name -r)
    echo "$repos" >>"$temp_file"
  done

  echo "存储库列表已保存到 $temp_file 文件中。"

  # 编辑 del.txt 文件以修改存储库列表
  vim $temp_file

  # 从编辑后的 del.txt 文件中读取存储库列表
  SORTED_REPOS=$(cat $temp_file)

  echo "存储库列表已编辑。"

  # 列出所有名称或描述中包含 'del' 的存储库
  echo -e "${SORTED_REPOS}"
  echo ""

  read -p "确定要删除所有这些存储库吗？ (y/n): " CONFIRM
  if [ "${CONFIRM}" == "y" ]; then
    for REPO in ${SORTED_REPOS}; do
      echo ""
      echo "正在删除存储库 ${REPO}..."

      curl -L \
        -X DELETE \
        -H "Accept: application/vnd.github+json" \
        -H "Authorization: Bearer ${ACCESS_TOKEN}" \
        -H "X-GitHub-Api-Version: 2022-11-28" \
        "https://api.github.com/repos/${USERNAME}/${REPO}"

    done
    echo ""
    echo "存储库已删除。"
  else
    echo ""
    echo "已取消删除。"
  fi

```