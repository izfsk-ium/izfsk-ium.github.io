---
uuid: "92a3c86b-baca-4a5d-bf87-e4b091adfd74"
title: scrcpy+sndcpy+kdeconnect多屏协作
date: 2022-12-19
category: 备忘录
---

「多屏协作」是很多电子设备厂商的卖点，本着 [Live free or die](https://unix.org/license-plate.html) 的头铁原则，使用 Linux 也可以利用各种工具实现这样的功能，并且，效果还不错。

# 目标

要达到我心目中的「多屏协作」，至少需要：

- 手机屏幕投射
- 双向文件互传
- 剪贴板分享
- 双向远程控制
- 媒体转接
- 通知传递

另外这一切都不应该借助数据线，经过一番折腾，我基本实现了这些目标，虽然免不了有一种自由软件大杂烩以后经典的「它能跑，但是毛毛糙糙」的感觉。

# scrcpy

`scrcpy`是一个命令行应用，用于把安卓设备的屏幕投射到电脑上，支持交互功能。你可以在[这里](https://scrcpy.org)下载。除此以外，你还需要在电脑上安装 adb 调试工具链接电脑，并在手机上打开 USB 调试功能。

最简单的使用就是直接用 USB 链接手机，允许 USB 调试，之后终端执行

```shell
$ scrcpy 
```

即可。scrcpy 自带了键盘模拟输入，鼠标代替触摸操作等。除此以外，系统剪贴板和手机剪贴板可以自动互通，拖放电脑文件到手机窗口会把文件 push 到 `/storage/emulated/0/Downloads/` 目录，也就是手机默认的「下载」目录。

## 手机关闭显示

如果你觉得手机一直亮着很费电，添加 `-S` 参数在连接电脑后自动熄灭屏幕即可。当然，如果再次操作物理手机还是能够正常使用的。

## 多个设备连接

如果你有很多设备连接，要么指定设备序列号，要么使用无线调试。先使用 `adb devices` 列出所有设备，第一列的就是设备编号，scrcpy 使用 `-s` 参数来辨别你要连接的设备。

```shell
$ scrcpy -S -s your-device
```

## 无线调试

在同一个局域网下，可以使用无线调试功能，解放 usb 插口。

:::{.note .blue}
|     |
| --- |
| 💭 **无线调试比较费带宽，如果 wifi 信号不好，或者正在下载什么东西，可能会卡顿明显。** |
:::

首先，你需要 USB 连接手机，确保 adb 畅通，接下来，启用无线调试：

```shell
$ adb tcpip 5555
```

默认的端口是 5555，当然你也可以自定义。接下来你要知道你的手机的 IP 地址：

```shell
$ adb shell ip addr
```

和 PC 不同，Android 设备会密密麻麻显示出几十个网络接口，一般 wlan 接口就是 `wlan0` 之类的，局域网地址一般以 `192.168` 开头。找到以后，输入 connect 连接：

```shell
$ adb connect 192.168.1.114:5555
```

如果没有问题，会显示 `connected to 192.168.1.114:5555`，这时候再 `adb devices` 会显示出无线调试的设备。此时就可以拔出 USB 线，直接远程连接了。如上所述，远程连接会比较耗费带宽，如果卡顿，可以试试限制视频大小。使用 `-m` 参数限制视频的宽度和高度，长宽比会被保留。实际上 1024 就可以用了，除非是列文虎克，否则看不太出来差别。

```shell
$ scrcpy -S --tcpip=192.168.1.114 -m 1024
```

如果出现问题或者找不到设备：

1. 再三检查自己的手机有没有连接 wifi，并且和电脑在同一个网域。
2. 尝试 `adb kill-server` 重新来过。 

连接结束后，可以使用 `adb disconnect` 结束连接。

## 录屏

使用 `-r` 参数加文件名录屏。格式是 mp4 或者 mkv，按照文件扩展名自动选择。

```shell
$ scrcpy -m 1024 -r record.mp4
```

实际测试一段 8 秒钟的视频，使用 mp4 格式， `-m 1024` 参数，大小是 4MB 左右（无声音）。

:::{.note .red}
|     |
| --- |
| ⚠️ **scrcpy 很诚实，它会把所有的一切录下来，包括你的锁屏和锁屏密码！** |
:::

注：Android 13 以后不再有这个问题。

## 多重虚拟屏幕

Android 开发人员选项有一个 Simulate secondary displays 的选项，可以设置虚拟显示屏。如果你的手机支持「桌面模式」，可以尝试开启，在手机和电脑上各开一个显示。

你可以使用 adb 命令开启一个虚拟显示输出：

```shell
$ adb shell settings put global overlay_display_devices 3840x2160/480
```

然后通过

```shell
$ adb shell dumpsys display | grep mDisplayId=
```

来获取虚拟显示输出的编号。编号 0 是手机的物理屏幕。接下来就可以使用 scrcpy 连接指定的虚拟屏幕了：

```shell
$ scrcpy -m 1024 --display 11
```

**注意，不是每一个型号的手机都可以支持「桌面模式」，大部分手机的虚拟显示器投屏以后只是灰屏。**

如果你想关闭虚拟显示屏，在「开发人员选项」里面找到 Simulate secondary displays 选取一个再关闭即可。

# sndcpy

`scrcpy` 只能投送屏幕，不能接管音频。如果想要把手机的音频也接管到电脑上来，需要其他的工具。你可以在[这里](https://github.com/rom1v/sndcpy)下载。要运行这个工具，你需要：

1. Android 10 或者以上的操作系统
2. 你的 PC 上安装了 VLC 并且在 path 里面
3. 你可以 adb 连接你的手机

解压 release 的压缩包以后，是运行脚本和一个 apk。主要就是依靠这个 apk 来完成音频转发。使用方法：

```shell
./sndcpy <serial>  # replace <serial> by the device serial
```

运行以后有可能会有报错，无妨，稍等即可。尝试表明，音乐应用等的音频可以转发，但是腾讯会议的音频在目前版本 (v1.1) 无法转发。

# kdeconnect

在 KDE 上使用 KDE Connect 和手机进行消息通知同步等可以使得你的「多屏协作」体验更好。使用 KDE Connect 需要：

1. 你的手机和电脑在同一个网络下
2. 你的手机安装 KDE Connect
3. 防火墙放行相关端口

**并不是只有 KDE 才能使用 KDE Connect，Gnome 乃至 Windows 平台都可以享受它**。在 Gnome 上你可以使用 [GSConnect](https://extensions.gnome.org/extension/1319/gsconnect/) 来替代，在 Windows上你可以直接在[微软应用商店](https://apps.microsoft.com/store/detail/9N93MRMSXBF0?hl=zh-cn&gl=CN)下载它。当然，KDE 不可能向国内的手机应用商店交钱上架，所以你需要在 [F-Droid](https://f-droid.org/en/packages/org.kde.kdeconnect_tp/) 下载最新的手机应用。

KDE Connect 的使用非常简单，一看就能明白。如果你还是无法检测到设备，检查一下你的 PC 防火墙设置。KDE Connect 使用 UDP 和 TCP 端口 1714-1764，确保你的防火墙放行了它们。

```shell
# 如果你使用 ufw
sudo ufw allow 1714:1764/udp
sudo ufw allow 1714:1764/tcp
sudo ufw reload

# 如果你使用 firewall-cmd
sudo firewall-cmd --permanent --zone=public --add-service=kdeconnect
sudo firewall-cmd --reload

# 如果你非要用 iptables...
sudo iptables -I INPUT -i <yourinterface> -p udp --dport 1714:1764 -m state --state NEW,ESTABLISHED -j ACCEPT
sudo iptables -I INPUT -i <yourinterface> -p tcp --dport 1714:1764 -m state --state NEW,ESTABLISHED -j ACCEPT

sudo iptables -A OUTPUT -o <yourinterface> -p udp --sport 1714:1764 -m state --state NEW,ESTABLISHED -j ACCEPT
sudo iptables -A OUTPUT -o <yourinterface> -p tcp --sport 1714:1764 -m state --state NEW,ESTABLISHED -j ACCEPT
```

# 附录：scrcpy 快捷键

首先，需要设定 `mod` 键作为前缀。默认是 `lalt, lsuper` 使用 ` --shortcut-mod key` 来设置。

序列|作用|
|:---|:--|
`Mod + f`|进入/退出全屏模式
`Mod + Left/Right`|旋转方向
`Mod + h`| Home 键
`Mod + b`| Back 键盘（右击鼠标亦可）
`Mod + s`| 最近应用列表
`Mod + m`| 应用菜单键
`Mod + Up/Down`|调节音量
`Mod + Shift + o`|关闭屏幕
`Mod + Shift + n`|下拉系统菜单
`Mod + Shift + v`|从系统剪贴板输入序列

# 参考

- [scrcpy有关「桌面模式」的 issue ](https://github.com/Genymobile/scrcpy/issues/1413)
- [sndcpy 仓库](https://github.com/rom1v/sndcpy)
- [KDE Connect 手册](https://userbase.kde.org/KDEConnect)