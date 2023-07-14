---
uuid: "fa8435d4-54a4-4d3a-bb65-d26f913e009e"
title: 给Apache2安装ModSecurity
date: 2023-03-10
category: 技术
---

我想要禁止服务器发送 Server: Apache 的 Header，但是不能通过直接配置的方法实现，需要使用第三方模块来实现。也就是这个 ModSecurity。除了这个功能以外 ModSecurity 就像它的名字那样包含了大量的的安全加强功能。

首先你需要安装一系列前置:编译器套件不用多说，在 SUSE 上还需要额外安装 gcc-c++ 。除此以外还有其他的前置需要安装，`zypper in libyajl libyajl-devel` 即可。

接下来编译安装 ModSecurity 主体：

```bash
git clone https://github.com/SpiderLabs/ModSecurity
cd ModSecurity/
git submodule update
git submodule init
./build.sh
make -j4
sudo make install
```

接下来手动拷贝一下模块文件：

```bash
cp /usr/local/modsecurity/lib/libmodsecurity.so /usr/local/apache2/modules/
```

这样主体安装完成。**对于 Apache 服务器还需要安装对应的连接器**：

```bash
./configure
./autogen.sh
cd ModSecurity-apache/
git clone https://github.com/SpiderLabs/ModSecurity-apache
```

如果提示找不到 `libmodsecurity` 说明需要手动寻找一下安装位置。一般就是在 `/usr/local/` 之中：

```bash
make install
make
./configure --with-libmodsecurity=/usr/local/modsecurity/
```

接下来开启模块：

```conf
LoadModule security3_module modules/mod_security3.so

modsecurity on
```

注意添加配置文件。日志里面可以看到这个：

`[Fri Mar 10 08:54:55.965949 2023] [:notice] [pid 14761:tid 4396092952880] ModSecurity: ModSecurity-Apache v0.1.1-beta configured.`

- [ModSecurity](https://github.com/SpiderLabs/ModSecurity/)
- [默认配置](https://github.com/SpiderLabs/ModSecurity/blob/v3/master/modsecurity.conf-recommended)