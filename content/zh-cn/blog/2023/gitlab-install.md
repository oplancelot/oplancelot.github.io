---
title:  Use your own wildcard certificate  install  gitlab on minikube 
weight: 3
date: 2023-07-03
description: 记录使用自定义证书在minikube安装gitlab的关键步骤
# draft: true
categories: [k8s]
tags: [minikube,gitlab,TLS]
---


1: Use your own wildcard certificate

使用自己的通配符证书

Add your full chain certificate and key to the cluster as a Secret, e.g.:

将完整链证书和密钥作为 Secret 添加到集群，例如：

kubectl create secret tls <tls-secret-name> --cert=<path/to-full-chain.crt> --key=<path/to.key>
```bash
$ kubectl create secret tls 550w.dev --cert=fullchain.pem --key=privatekey.pem -n gitlab

$ kubectl get secret
NAME                                  TYPE                 DATA   AGE
550w.dev                              kubernetes.io/tls    2      15s
```


2.编辑values-minikube.yaml

注意tls

```yaml
# values-minikube.yaml
# This example intended as baseline to use Minikube for the deployment of GitLab
# - Services that are not compatible with how Minikube runs are disabled
# - Configured to use 192.168.99.100, and nip.io for the domain

# Minimal settings
global:
  ingress:
    configureCertmanager: false
    class: "nginx"
    tls:
      enabled: true
      secretName : "550w.dev" 
  hosts:
    domain: 550w.dev 
    externalIP: 192.168.49.2
  shell:
    # Configure the clone link in the UI to include the high-numbered NodePort
    # value from below (`gitlab.gitlab-shell.service.nodePort`)
    port: 32022
# Don't use certmanager, we'll self-sign
certmanager:
  install: false
# Use the `ingress` addon, not our Ingress (can't map 22/80/443)
nginx-ingress:
  enabled: false
# Map gitlab-shell to a high-numbered NodePort cloning over SSH since
# Minikube takes port 22.
gitlab:
  gitlab-shell:
    service:
      type: NodePort
      nodePort: 32022
# Provide gitlab-runner with secret object containing self-signed certificate chain
gitlab-runner:
  certsSecretName: gitlab-wildcard-tls-chain
  install: true
  runners:
    privileged: true
# postgres
postgresql:
        image:
          tag: 13.6.0
```

3.使用helm安装
提前pull chart 到本地，可以节约时间。
ingress-nginx 也要提前安装

```bash
git clone https://gitlab.com/gitlab-org/charts/gitlab.git
cd gitlab

helm dependency update

helm upgrade --install gitlab . --timeout 600s -f values-minikube.yaml -n gitlab
  ```
如果是不使用自定义证书
```bash
helm upgrade --install gitlab . \
  --timeout 600s \
  -f https://gitlab.com/gitlab-org/charts/gitlab/raw/master/examples/values-minikube.yaml  \
  --set global.hosts.domain=$(minikube ip).nip.io \
  --set global.hosts.externalIP=$(minikube ip)

#minikube ip 是默认的minikube 容器地址
#minikube ssh可以登陆
$ minikube ip
192.168.49.2

$ minikube tunnel

Status: 
 machine: minikube
 pid: 1743956
 route: 10.96.0.0/12 -> 192.168.49.2
 minikube: Running
 services: [balanced]
    errors:
  minikube: no errors
  router: no errors
  loadbalancer emulator: no errors

```

4.登陆gitlab
```bash
#取得root 密码

$ kubectl get secret gitlab-gitlab-initial-root-password -ojsonpath='{.data.password}' | base64 --decode ; echo
YPEMHZa6zCnKD4bJAvUEucbYXcsF4veIAG8JegvSq27X2QaIgeZdQnqIAMGzA5eM

#取得minio accesskey&secretkey
$ kubectl get secret gitlab-minio-secret -ojsonpath='{.data.accesskey}' | base64 --decode ; echo
hFpWJwsjVOudH6T7Fve9OUvTAum356hOcb5RMVju3Ib6hQXLk2n2WrCJYSAa7Jyr
[lance@lance-workstation ~/gitlab]
$ kubectl get secret gitlab-minio-secret -ojsonpath='{.data.secretkey}' | base64 --decode ; echo
1WOOlSo3GANyLffOnhkv3qBSWbu2DGSip7H8h1QqYKLLc7eM5Be3OKtFcldbQMal

```
dns解析
`/etc/hosts`添加如下一行
```
192.168.49.2 gitlab.550w.dev registry.550w.dev minio.550w.dev
```

然后就可以浏览器登陆 `gitlab.550w.dev` 

5.ingress 提供外部访问的入口

```bash
$ kubectl get ingress -n gitlab
+ kubectl get ingress -n gitlab
NAME                        CLASS   HOSTS               ADDRESS        PORTS     AGE
gitlab-kas                  nginx   kas.550w.dev        192.168.49.2   80, 443   3d3h
gitlab-minio                nginx   minio.550w.dev      192.168.49.2   80, 443   3d3h
gitlab-registry             nginx   registry.550w.dev   192.168.49.2   80, 443   3d3h
gitlab-webservice-default   nginx   gitlab.550w.dev     192.168.49.2   80, 443   3d3h
[lance@lance-workstation ~/gitlab]
$ 
```


主要参考

[Developing for Kubernetes with minikubeCONTRIBUTE](https://docs.gitlab.com/charts/development/minikube/)

[Configure TLS for the GitLab chart ](https://docs.gitlab.com/charts/installation/tls.html#option-2-use-your-own-wildcard-certificate)

[minikube star](https://minikube.sigs.k8s.io/docs/start/)

[ingress-minikube](https://kubernetes.io/zh-cn/docs/tasks/access-application-cluster/ingress-minikube/)