---
uuid: "d335a295-647a-4f5e-b15b-140178c18782"
title: v2ray 结合 cgproxy 全局代理方案
date: 2023-06-25
category: 备忘录
---

`cgproxy` 是使用 Linux `cgroup` 功能实现全局代理的工具。一般在 Linux 上使用代理工具难以设置全局代理，不同的桌面环境，不同的软件行为都不一样，有的读取桌面环境的配置，有的认可环境变量，有的在软件内配置，有的根本不提供代理设置方式。一般对于终端中的程序可以使用 `proxychains` 来强制走代理，但这个工具是基于 `LD_PRELOAD`，对于静态链接的程序就不行。所以需要一个统一的解决方案。

## 前提准备

### 确保 cgroup 支持

运行 `findmnt -t cgroup2`，如果出现类似

```log
TARGET               SOURCE  FSTYPE  OPTIONS
/sys/fs/cgroup       cgroup2 cgroup2 rw,nosuid,nodev,noexec,relatime
/run/cgproxy/cgroup2 none    cgroup2 rw,relatime
```

则支持。

### v2ray

首先需要安装代理工具核心。可以使用发行版提供的版本，也可以使用安装脚本。`v2fly` 有提供一个安装脚本。执行即可。

```sh
bash <(curl -L https://raw.githubusercontent.com/v2fly/fhs-install-v2ray/master/install-release.sh)
```

当然，访问 `githubusercontent` 需要代理......所以你可以使用手机共享网络+分享 vpn 的方式。不过似乎中国的大部分 Android 发行版都不支持(?)

这个脚本将各个文件安装在如下位置：

```yaml
installed: /usr/local/bin/v2ray
installed: /usr/local/bin/v2ctl
installed: /usr/local/share/v2ray/geoip.dat
installed: /usr/local/share/v2ray/geosite.dat
installed: /usr/local/etc/v2ray/config.json
installed: /var/log/v2ray/
installed: /var/log/v2ray/access.log
installed: /var/log/v2ray/error.log
installed: /etc/systemd/system/v2ray.service
installed: /etc/systemd/system/v2ray@.service
```

值得注意的是配置文件路径：`/usr/local/etc/v2ray/config.json`

接下来启用和运行 `systemd` 单元即可：

```sh
sudo systemctl enable --now v2ray
sudo systemctl start v2ray
```

### 配置文件

当然是你自己搞到配置文件。无论如何，你需要得到一个完整的 json 配置文件来替换 `/usr/local/etc/v2ray/config.json`，关于如何从订阅链接或者从各种链接转换就不展开说明了。

其中一个办法是从手机导入，在 v2rayNG 中导出配置到剪贴板再复制到文件，然后复制到电脑上。

### 安装 cgproxy

首先，你的 Linux 发行版不能太旧。不然都不支持 cgroup v2。

在编译安装之前需要各种工具和相关的库：

- `cmake`, `gcc`, `g++` 等编译工具：对于 Debian 系列的发行版，是`sudo apt-get install build-essential`；对于 openSUSE，是 `zypper install -t pattern devel_basis`。`cmake` 可能不在里面，再额外安装一下就行。

- `bpftool`, `libbpf-devel`, `nlohmann_json-devel`：`cgproxy` 的依赖。对于 openSUSE，软件包就是前面的名字，安装即可。对于其他发行版，请查阅文档。

接下来编译安装：

```sh
git clone https://github.com/springzfx/cgproxy
cd cgproxy && mkdir build
cd build
# generate
cmake -DCMAKE_BUILD_TYPE=Release \
      -DCMAKE_INSTALL_PREFIX=/usr \
      -Dbuild_execsnoop_dl=ON \
      -Dbuild_static=OFF \
      ..
# compile
make
```

如果 `cmake` 报错，就按照错误找缺失的包安装。如果 `make` 报错，可能是 `bpftool` 没有安装。

接下来 `sudo make install` 安装到系统。并启用 `systemd` 单元：

```sh
sudo systemctl enable --now cgproxy.service
```

如果一切顺利，则会提示

```log
Created symlink /etc/systemd/system/multi-user.target.wants/cgproxy.service → /usr/lib/systemd/system/cgproxy.service.
```

## 修改配置文件

首先确保你的 `v2ray` 核心运行良好，请启动它并自行寻找一个方式验证。一般来讲配置的默认入站地址有 `socks://127.0.0.1:10808`，所以可以在火狐中设置一下代理。总之确保目前的 `v2ray` 配置无误。

`cgproxy` 的运行机制可以理解成这样：所有程序网路请求都会被它“拦截”并转发到 `v2ray`，但转发的协议不是 `http` 或者 `socks` 而是 `dokodemo-door`。所以你需要额外在自己的 `v2ray` 配置文件里面加入 `dokodemo-door` 的透明代理监听入站。

假设原来的配置是这样：

```json
{
  "dns": {...},
  "inbounds": [
    {
      "listen": "127.0.0.1",
      "port": 10808,
      "protocol": "socks",
      "settings": {
        ...
      },
      "sniffing": {
        ...
      },
      "tag": "socks"
    },
    {
      "listen": "127.0.0.1",
      "port": 10809,
      "protocol": "http",
      "settings": {
        ...
      },
      "tag": "http"
    }
  ],
  "log": {
    "loglevel": "warning"
  },
  "outbounds": [...],
  "routing": {
    ...
  }
}
```

可以看见 `inbounds` 区域里面有两个入站设定，现在把第三个添加到 `inbounds` 里面：

```json
{
    "tag": "transparent",
    "port": 12345,
    "protocol": "dokodemo-door",
    "settings": {
        "network": "tcp,udp",
        "followRedirect": true
    },
    "sniffing": {
        "enabled": true,
        "destOverride": [
            "http",
            "tls"
        ]
    },
    "streamSettings": {
        "sockopt": {
            "tproxy": "tproxy"
        }
    }
}
```

便于查错，你可以使用 `vscode` 等工具打开配置文件修改和添加内容。**以防万一，注意备份你的配置**。

这里设置的 `dokodemo-door` 监听端口是 `12345` 端口。修改完毕后保存，然后测试：

```sh
v2ray test -c /usr/local/etc/v2ray/config.json
```

如果没有问题：

```log
V2Ray 5.7.0 (V2Fly, a community-driven edition of V2Ray.) Custom (go1.20.4 linux/amd64)
A unified platform for anti-censorship.
Configuration OK.
```

<del>那就是没有问题</del>

接下来重启 `v2ray` 服务：

```sh
sudo systemctl restart v2ray
```

现在开始修改 `cgproxy` 的配置文件，其位于 `/etc/cgproxy/config.json`。

默认情况下：

```json
{
    "port": 12345,
    "program_noproxy": ["v2ray", "qv2ray"],
    "program_proxy": [],
    "cgroup_noproxy": ["/system.slice/v2ray.service"],
    "cgroup_proxy": [],
    "enable_gateway": false,
    "enable_dns": true,
    "enable_udp": true,
    "enable_tcp": true,
    "enable_ipv4": true,
    "enable_ipv6": true,
    "table": 10007,
    "fwmark": 39283
}
```

就已经够用。其中 `port` 就是之前新增的 `dokodemo-door` 监听端口，而 `program_noproxy` 是不进行代理的程序名称。`v2ray` 当然要排除在外，不然就是循环代理了。

保存配置文件。

## 启用

确认都配置好了以后，`sudo systemctl restart cgproxy.service` 启动服务，使用以下命令测试：

```sh
cgproxy curl -vI https://www.google.com
```

注意，先取消之前设置的代理。(清除环境变量，设置等)。如果没有任何问题，就可以稳定运行了。

## 其他

要查看 `v2ray` 的日志：

```sh
sudo journalctl -u v2ray --follow --output cat
```

要停止 `cgproxy`:

```sh
sudo systemctl disable --now cgproxy.service
```

**注意**：**必须**使用 `sudo systemctl disable --now cgproxy.service` 来关闭服务，否则下一次启动可能会失效！

## 参考

- [v2fly/v2ray-core](https://github.com/v2fly/v2ray-core)
- [springzfx/cgproxy](https://github.com/springzfx/cgproxy)
- [Control Group v2](https://docs.kernel.org/admin-guide/cgroup-v2.html)
