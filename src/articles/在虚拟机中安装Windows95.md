---
uuid: "5725ea26-0d1f-e95b-4611-5e40d236f79f"
title: "在虚拟机中安装 Windows95"
english: "install-Windows95-in-oracle-virtual-box"
date: 2023-07-20
category: "考古"
outdated: false
draft: false
ref: 
  - name: "How to convert .img to usable VirtualBox format"
    url: "https://superuser.com/questions/554862/"
  - name: "Windows95 镜像下载"
    url: "https://winworldpc.com/product/windows-95/osr-2"
  - name: "FIX95CPU_V3_FINAL"
    url: "https://archive.org/details/fix-95-cpu-v3-final"
  - name: "Windows 95 2.1GHz CPU Limit BROKEN!"
    url: "https://msfn.org/board/topic/141402-windows-95-21ghz-cpu-limit-broken/"
  - name: "While initializing device NDIS: Windows protection error"
    url: "https://web.archive.org/web/20040302015309/http://support.microsoft.com/?id=312108"
  - name: "Missing VXD and DLL files on Windows 95"
    url: "https://www.streetinfo.lu/computing/sysadmin/windows/win95_missing.html"
---

我想要安装 FreeDOS 来考古，以及安装 Windows95 和 Borland C++ 游玩。安装 FreeDOS 和普通操作系统有些不同，以下做一个记录。

:::{.note .red}
|     |
| --- |
| ℹ️ 如果你要参考，请**完整的阅读完这篇文章**！ |
:::

## 转换安装镜像

首先你需要一个[安装镜像文件](https://www.ibiblio.org/pub/micro/pc-stuff/freedos/files/distributions/1.3/official/FD13-FullUSB.zip)，这是一个 ZIP 压缩包，而不是期望的 ISO 镜像。
解压以后，会有一个 img 文件，同样无法直接挂载使用。这玩意实际上是一个完整的磁盘镜像文件。VirtualBox 提供了对应的工具转换其为 VDI 格式：

```sh
$ VBoxManage convertfromraw --format VDI [filename].img [filename].vdi
```

然后就会得到一个可用的 VDI 镜像了。

## 创建虚拟机

按照一半流程创建虚拟机，但注意**不要添加任何磁盘**：

![创建虚拟机](./assets/%E5%88%9B%E5%BB%BA%E8%99%9A%E6%8B%9F%E6%9C%BA.jpg)

接下来配置磁盘，打开新建的虚拟机的配置页面：

- 在原有的 IDE 控制器上增加一个新的磁盘，选定刚才转换好的 VID 镜像
- 新增一个 AHCI 控制器，创建一个新的空 VID 介质

最后的配置应该是这样：

![磁盘配置结果](./assets/%E9%85%8D%E7%BD%AE%E7%A3%81%E7%9B%98.png)

然后启动。

## 安装系统

启动的第一屏是选择语言：

![选择语言](./assets/boot1.png)

接下来一路 Enter 下去，按照它的要求给磁盘分区，然后重新启动。**但是，重启之后又会回到同样的步骤**。你需要在第一次分区完毕以后，关掉虚拟机，打开虚拟机设置，将 IDE 控制器中的安装镜像 VDI 删除，再重新添加这个 VDI，再重新启动虚拟机。按照原来的方式 Enter 下去，这一次要求分区确认后，会得到不一样的显示界面：

![不同的界面](./assets/boot2.png)

这就是真正的安装了。选择键盘布局，选择完全安装：

![选择安装类型](./assets/install3.png)

安装完毕以后会自动重启，然后**又一次回到安装界面**，这一次需要做的是在设置中将 IDE 控制器中的安装镜像 VDI 移除。再次启动应该就能看到已经安装好的 FreeDOS 了。

![安装完毕](./assets/ins4.png)

![启动的 FreeDOS](./assets/ok4.png)

## 安装 Windows95

也许 DOS 之于 Windows95 有点类似于「内核」与「桌面环境」的关系？总之，需要单独安装 Windows95。

首先下载镜像，可以在一些地方找到它，例如[这里](https://winworldpc.com/product/windows-95/osr-2)。这一次下载下来的应该是 ISO 格式的镜像。先别急着挂载，为了保证速度，建议的方法是解压到磁盘，然后通过 VirtualBox 的工具将磁盘文件作为 ISO 虚拟镜像挂载。无论采用什么方法，挂载的磁盘会出现在 `D:\`。挂载完毕后，键入 `D:` 进入对应目录，使用 `dir` 列出文件，应该能看到 `setup.exe`，使用 `.\setup.exe` 运行它。如果一切正常，就能够看到安装前的自检：

![安装前的检查](./assets/win95_1.png)

**注意：如果它提示遇到 FAT 文件系统错误，不要自动修复，那会搞坏 DOS 系统，检查你的安装介质。**

然后是图形化的安装界面，并没有什么难度。为了通过喜闻乐见的输入密钥环节，密钥的规律如下：

```go
dddyy-OEM-xxxxx-zzzzz
```

其中：

- ddd 是密钥发布天 (范围 001-366)
- yy 是二位数的年份 (范围 95-02)
- xxxxx, 第一个数字必须为零，最后一个数字不能是 0、8 或 9。这些数字加在一起时必须能被 7 整除。

一个示例：`06197-OEM-0014907-15227`

![安装过程中](./assets/win95_2.png)

在询问是否创建 *startup disk* 时，选择否。

然后就是慢慢的等待并祈祷这玩意不要卡住：

![薛定谔的安装程序](./assets/win95_3.png)

最后安装完毕，重启

## 解决 2.1GHz 问题 

再次启动，会遇到这个问题：

![Windows Protection Error](./assets/win95_5.png)

这是因为 Windows 95 不支持运行速度高于 2.1GHz 的处理器，如果 CPU 以 2.1 GHz 或更快的速度运行，网络驱动程序接口规范 (NDIS) 驱动程序中的时序校准代码会导致除以零。以 2.1 GHz 或更低速度运行的 CPU 不会出现此问题。

为了解决这个问题，需要进行人工 patch。在[此处](https://archive.org/details/fix-95-cpu-v3-final)下载 patch，解压其中的 ISO 作为引导，继续启动：

![Patch](./assets/hspd.png)

然后按照提示操作就行：

![完成](./assets/patchok.png)

再次重启，如果还是不行，说明**内存给多了**，降到 256MB 以下。

## 文件复制问题

再次开机，但别忘了还没装玩呢（

![复制文件](./assets/win95_6.png)

然而，安装介质中是**没有**这些文件的，而如果你鬼迷心窍的点击的取消，那系统就会死机，只能重启，这样做意味着文件系统损坏，然后 ScanDisk 会自作聪明的移除所有受到波及的文件，然后......就只能重新安装整个系统了。

![重装吧...](./assets/badluck.png)

是的，你甚至连桌面都没看到，系统就自己把自己搞坏了。所以在虚拟机玩的时候，一定要**步步为营，做好快照**。

为了能够正常的进入系统，需要做的就是：Skip。跳过所有找不到的文件。实际上它们就在 ISO 中的某个 CAB 文档中，但 Windows 就是会告诉你：找不到。最后我进入了安全模式：

![安全模式](./assets/savemode.png)
