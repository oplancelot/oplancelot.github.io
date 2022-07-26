---
layout: post
title: 使用azure devops 更新github博客
description: pipeline更新博客
category: posts
tags: jekyll azure devops pipeline
draft: false
mermaid: false

---
为什么我还要使用pipeline来处理呢？

以前的workflow 是
1. md文字编辑
2. VS上传到remote host
3. vs执行脚本
4. remote host 预览
5. vs提交到github
   


使用pipeline后，只需要
1. md文字编辑
2. 提交到azure devops repos

pipeline 处理
1. 添加tag
2. push github


如果哪天需要迁移blog到其他只支持静态页面的环境，比如S3，
pipeline里添加jekyll的build步骤再上传即可。

azure-pipeline.ymal

```
# Starter pipeline
# Start with a minimal pipeline that you can customize to build and deploy your code.
# Add steps that build, run tests, deploy, and more:
# https://aka.ms/yaml

trigger:
- main

pool:
  name: Default


# Note: github_pat should be configured as an environment variable in devops
#   -> create github pat here: https://github.com/settings/tokens
#   -> Create environment variable in dev.azure.com under pipelines -> edit (right top) -> variables (right top triple dots) -> called github_pat -> click the lock
variables:
  gh_user: oplancelot
  gh_repo: oplancelot.github.io
  gh_pass: $(github_pat)
  gh_email: oplancelot@gmail.com
  gh_auth_header: $(echo -n "${gh_user}:$(github_pat)" | base64);



# steps:
# # https://docs.microsoft.com/en-us/azure/devops/pipelines/yaml-schema?view=azdevops&tabs=schema#checkout
# - checkout: none # we are not going to sync sources, we will manually clone
#   persistCredentials: false # We disallow setting the persisting, since we want to have a verified push which requires a PAT token



# # 1. Setup our local repository and branch that we can work on
# - script: git clone https://$(github_pat)@github.com/$(gh_user)/$(gh_repo).git .
#   workingDirectory: $(Build.StagingDirectory)
#   displayName: "[Git] Clone GitHub Pages Repository"

steps:
- checkout: self  # self represents the repo where the initial Pipelines YAML file was found
  clean: "true" # whether to fetch clean each time
  # fetchDepth: number  # the depth of commits to ask Git to fetch
  # lfs: boolean  # whether to download Git-LFS files
  # submodules: true | recursive  # set to 'true' for a single level of submodules or 'recursive' to get submodules of submodules
  path: source # path to check out source code, relative to the agent's build directory (e.g. \_work\1)
  # persistCredentials: boolean  # set to 'true' to leave the OAuth token in the Git config after the initial fetch

- script: | 
   git remote rm github
   git remote add github  https://$(github_pat)@github.com/$(gh_user)/$(gh_repo).git
  workingDirectory: $(Agent.BuildDirectory)/source
  displayName: "[Git] add GitHub Pages Repository"

- script: |
    git config user.email $(gh_email)
    git config user.name $(gh_user)
  workingDirectory: $(Agent.BuildDirectory)/source
  displayName: '[Git] Configure User'

- script: |
    pwd;
    ls -la;
  workingDirectory: $(Agent.BuildDirectory)/source
  displayName: '[Shell] ls'

# 2. add/update tag
# default dir $(System.DefaultWorkingDirectory) 
- script: python $(Agent.BuildDirectory)/source/_tag_generator.py
  displayName: '[python] add tag'

# 3. Create our commit, merge into master, delete draft branch and push it
- script: |
    git add --all;
    git commit -m "Pipelines-Bot: Updated site via $(Build.SourceVersion)";
  workingDirectory: $(Agent.BuildDirectory)/source
  displayName: '[Git] Creating commit'

- script: |
    git pull github main;
    git push github HEAD:main;
  workingDirectory: $(Agent.BuildDirectory)/source
  displayName: '[Git] Push changes to remote'

# 4. Get GitHub Pages build status

- script: |
    curl https://api.github.com/repos/$(gh_user)/$(gh_repo)/pages/builds/latest -i -v \
    -X GET \
    -H "Accept: application/vnd.github.mister-fantastic-preview+json" \
    -H "Authorization: Basic $(gh_auth_header)"
  displayName: '[GitHub] Get Page Build Status'
```

