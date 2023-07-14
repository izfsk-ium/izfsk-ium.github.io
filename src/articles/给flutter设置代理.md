---
uuid: "79ef49e0-db49-4547-bfbf-78b6a511e91d"
title: 给 flutter 设置代理
date: 2023-06-28
category: 备忘录
---

## Dart 镜像站点

`flutter` 会读取两个环境变量作为镜像站点的地址：

- `PUB_HOSTED_URL`
- `FLUTTER_STORAGE_BASE_URL`

在 `.bashrc` 或者 `.zshrc` 添加：

```sh
export FLUTTER_STORAGE_BASE_URL="https://mirrors.tuna.tsinghua.edu.cn/flutter"
export PUB_HOSTED_URL="https://mirrors.tuna.tsinghua.edu.cn/dart-pub"
```

## 编译时 gradle 代理

当然也可以选择镜像仓库地址，但似乎很难配置正确，而 `flutter build apk` 又不吃 `proxychans` 和环境变量，但 `gradle` 可以配置全局的代理设置：

更改（或者创建）文件 `~/.gradle/gradle.properties`，并添加：

```sh
systemProp.http.proxyHost=127.0.0.1
systemProp.https.proxyPort=10809
systemProp.https.proxyHost=127.0.0.1
systemProp.http.proxyPort=10809
```

即可。

## 参考

- [Flutter build is still using an obsolete proxy address](https://stackoverflow.com/questions/55393142/flutter-build-is-still-using-an-obsolete-proxy-address)
- [清华大学开源软件镜像站 | Flutter 镜像安装帮助](https://mirrors.tuna.tsinghua.edu.cn/help/flutter/)
