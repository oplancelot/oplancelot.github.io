---
layout: post
title: 使用azure devops 更新github博客
description: pipeline更新博客
category: posts
tags: jekyll azure devops pipeline
draft: false
mermaid: false

---
github 上的博客网站支持jekyll,本来就可以提交MD文档，动态生成静态页面了。
为什么我还要使用pipeline来处理呢？

以前的workflow 是
1.md文字编辑
2.VS上传到remote host
3.vs执行脚本
4.remote host 预览
5.vs提交到github
也算方便。

使用pipeline后，只需要
1.md文字编辑
2.提交到azure devops repos

pipeline 处理
1.添加tag
2.push github


如果哪天需要迁移blog到其他只支持静态页面的环境，比如S3，pipeline里添加jekyll的build步骤再上传即可。