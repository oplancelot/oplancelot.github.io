---
layout: post
title: local custom provider with Terraform & install terraform providers locally
description: local custom provider with Terraform & install terraform providers locally
category: posts
tags: terraform
draft: false
mermaid: false

---

##  local custom provider with Terraform & install terraform providers locally



### 架构图

 ![图：Terraform 如何使用插件](https://mktg-content-api-hashicorp.vercel.app/api/assets?product=terraform-cdk&version=v0.10.4&asset=website%2Fdocs%2Fcdktf%2Fconcepts%2Fimages%2Fterraform-plugin-overview.png) 

https://github.com/mumoshu/terraform-provider-eksctl

https://github.com/scottwinkler/terraform-provider-shell

以上两个项目自己研发了provider，terraform是允许开发自己的providers 的，可以方便的调用自己定义的资源，服务，以自定义的方式和`terraform core`交互，实现了更大的自由和可能。

这些自己开发的 (甚至官方的比如aws)providers在没有公网的环境，或者外网环境不佳的情况下，在terraform init 初始化下载的时候是很痛苦的，有些provider有几百兆大小。

https://www.terraform.io/cli/config/config-file这个官方文档解释了如何配置。

下面是实际的例子说明了如何使用自定义providers(How to use a local custom provider with Terraform? )，以及如何存放从`https://releases.hashicorp.com/`下载的providers(How to install terraform providers locally?)



### 如何使用自定义providers(How to use a local custom provider with Terraform) 

[cdktf.json](https://github.com/orgs/hashicorp/repositories?q=cdktf-provider-) 会生成 [.terraformrc](https://www.terraform.io/cli/config/config-file#implied-local-mirror-directories) 这个文件定义了所有provider如何存放

[filesystem_mirror](https://www.terraform.io/cli/config/config-file#filesystem_mirror)部分就是自定义的`custom providers`存放的位置，同时需要根据版本平台版本等定义路径

Terraform expects the given directory to contain a nested directory structure where the path segments together provide metadata about the available providers. The following two directory structures are supported:

- Packed layout: `HOSTNAME/NAMESPACE/TYPE/terraform-provider-TYPE_VERSION_TARGET.zip` is the distribution zip file obtained from the provider's origin registry.

- Unpacked layout: `HOSTNAME/NAMESPACE/TYPE/VERSION/TARGET` is a directory containing the result of extracting the provider's distribution zip file.

-  In both layouts, the `VERSION` is a string like `2.0.0` and the `TARGET` specifies a particular target platform using a format like `linux_amd64`,`darwin_amd64`, `linux_arm`, `windows_amd64`, etc. 

- `HOSTNAME/NAMESPACE/TYPE/VERSION/TARGET` 举例如下`example.com/mumoshu/eksctl/0.16.2/linux_amd64`

   [.terraformrc](https://www.terraform.io/cli/config/config-file#implied-local-mirror-directories) 

```haskell
plugin_cache_dir  = "$HOME/.terraform.d/plugin-cache" 
disable_checkpoint = true

provider_installation {
 filesystem_mirror {
  path   = "/home/debian/.terraform.d/plugin-cache"
  include = ["example.com/mumoshu/eksctl"]
 }
 direct {
  exclude = ["example.com/*/*"]
 }

}
```

在`main.tf` 里使用providers，按如下定义source

```haskell
terraform {
  required_providers {
    eksctl = {
      source = "example.com/mumoshu/eksctl"
      version = "0.16.2"
    }
  }
}
provider "eksctl" {
  # Configuration options
}
```

实际的目录结构如下图`registry.terraform.io`是direct默认下载的位置`example.com `与之平级

```shell
debian@debian:~/.terraform.d/plugin-cache$ pwd
/home/debian/.terraform.d/plugin-cache
.
├── example.com
│   └── mumoshu
│       └── eksctl
│           └── 0.16.2
│               └── linux_amd64
│                   └── terraform-provider-eksctl_v0.16.2
└── registry.terraform.io
    └── hashicorp
        ├── aws
        │   ├── 2.70.1
        │   │   └── linux_amd64
        │   │       └── terraform-provider-aws_v2.70.1_x4
        │   └── 4.11.0
        │       └── linux_amd64
        │           └── terraform-provider-aws_v4.11.0_x5
        ├── http
        │   └── 2.1.0
        │       └── linux_amd64
        │           └── terraform-provider-http_v2.1.0_x5
        ├── null
        │   └── 3.1.1
        │       └── linux_amd64
        │           └── terraform-provider-null_v3.1.1_x5
        └── template
            └── 2.2.0
                └── linux_amd64
                    └── terraform-provider-template_v2.2.0_x4

21 directories, 6 files

```

使用`terraform 1.19`正常，可能`0.14`版本就是正常的

```shell
debian@debian:~/terraform/terraform-provider-eksctl/examples/simple$ terraform119 init

Initializing the backend...

Initializing provider plugins...

- Finding example.com/mumoshu/eksctl versions matching "0.16.2"...
- Using example.com/mumoshu/eksctl v0.16.2 from the shared cache directory

Terraform has created a lock file .terraform.lock.hcl to record the provider
selections it made above. Include this file in your version control repository
so that Terraform can guarantee to make the same selections by default when
you run "terraform init" in the future.

Terraform has been successfully initialized!

You may now begin working with Terraform. Try running "terraform plan" to see
any changes that are required for your infrastructure. All Terraform commands
should now work.

If you ever set or change modules or backend configuration for Terraform,
rerun this command to reinitialize your working directory. If you forget, other
commands will detect it and remind you to do so if necessary.


```

同时会在`main.tf`所在的位置生成文件`.terraform.lock.hcl`

```haskell
debian@debian:~/terraform/terraform-provider-eksctl/examples/simple$ cat .terraform.lock.hcl

# This file is maintained automatically by "terraform init".

# Manual edits may be lost in future updates.

provider "example.com/mumoshu/eksctl" {
  version     = "0.16.2"
  constraints = "0.16.2"
  hashes = [
    "h1:SraYIYrtiYUKeWc6ur3dqOT+tFdqS9jl2qYJKi7ba2g=",
  ]
}
```



但是在`terrafrom 0.13` 版本local providers会有bug

```shell
debian@debian:~/terraform/terraform-provider-eksctl/examples/simple$ terraform init

Initializing the backend...

Initializing provider plugins...

- Finding example.com/mumoshu/eksctl versions matching "0.16.2"...
- Using example.com/mumoshu/eksctl v0.16.2 from the shared cache directory

Error: Failed to install provider from shared cache

Error while importing example.com/mumoshu/eksctl v0.16.2 from the shared cache
directory: after linking example.com/mumoshu/eksctl from provider cache at
/home/debian/.terraform.d/plugin-cache it is still not detected in the target
directory; this is a bug in Terraform.
```

此时可以把这个providers当成从`https://releases.hashicorp.com/`官方下载的providers一样处理，如何处理呢？

**### 如何存放从`https://releases.hashicorp.com/`下载的providers**

### How to install terraform providers locally?



处理方法是可以把`roviders` 放在默认的位置，`main.tf` 定义`source`时`hostname`不再需要`example.com`，不屑的话默认就是`registry.terraform.io`，所以目录是如下结构

```
registry.terraform.io
    ├── hashicorp
    │   ├── aws
    │   │   ├── 2.70.1
    │   │   │   └── linux_amd64
    │   │   │       └── terraform-provider-aws_v2.70.1_x4
    │   │   └── 4.11.0
    │   │       └── linux_amd64
    │   │           └── terraform-provider-aws_v4.11.0_x5
    │   ├── http
    │   │   └── 2.1.0
    │   │       └── linux_amd64
    │   │           └── terraform-provider-http_v2.1.0_x5
    │   ├── null
    │   │   └── 3.1.1
    │   │       └── linux_amd64
    │   │           └── terraform-provider-null_v3.1.1_x5
    │   └── template
    │       └── 2.2.0
    │           └── linux_amd64
    │               └── terraform-provider-template_v2.2.0_x4
    └── mumoshu
        └── eksctl
            └── 0.16.2
                └── linux_amd64
                    ├── LICENSE
                    ├── README.md
                    ├── terraform-provider-eksctl_0.16.2_linux_amd64.zip
                    └── terraform-provider-eksctl_v0.16.2

```

Let's say you use `0.16.2` as the dummy version number:

```
terraform {
  required_providers {
    eksctl = {
      source = "mumoshu/eksctl"
      version = "0.16.2"
    }
  }
}
```

You place the binary under:

```
VER=0.16.2

~/.terraform.d/plugin-cache/registry.terraform.io/mumoshu/eksctl/$(VER)/linux_amd64/terraform-provider-eksctl_v$(VER)
```

```shell
debian@debian:~/terraform/terraform-provider-eksctl/examples/simple$ terraform init

Initializing the backend...

Initializing provider plugins...

- Using previously-installed mumoshu/eksctl v0.16.2

Terraform has been successfully initialized!

You may now begin working with Terraform. Try running "terraform plan" to see
any changes that are required for your infrastructure. All Terraform commands
should now work.

If you ever set or change modules or backend configuration for Terraform,
rerun this command to reinitialize your working directory. If you forget, other
commands will detect it and remind you to do so if necessary.
debian@debian:~/terraform/terraform-provider-eksctl/examples/simple$ 
```





参考

[Easiest way to use a local custom provider with Terraform 0.13](https://discuss.hashicorp.com/t/easiest-way-to-use-a-local-custom-provider-with-terraform-0-13/12691)