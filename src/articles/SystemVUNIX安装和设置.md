---
uuid: "ca4147da-03bf-e4cc-3d48-3e7cd2e44295"
title: "UNIX System V 的安装和设置"
english: "install-unix-system-v"
date: 2023-07-21
category: "考古"
outdated: false
draft: true
ref: 
  - name: "AT&T System V Unix 2.x"
    url: "https://winworldpc.com/product/att-system-v-unix/2-x"
  - name: "The BIOS IDE Harddisk Limitations"
    url: "http://www.steunebrink.info/bioslim.htm#Contents"
  - name: "Using floppies in AT&T UNIX System V"
    url: "https://www.linuxquestions.org/questions/other-*nix-55/using-floppies-in-at-and-t-unix-system-v-release-4-version-2-1-or-docs-link-4175428440/"
  - name: "How can I use ImageDiskimages with VirtualBox?"
    url: "https://retrocomputing.stackexchange.com/questions/7890/how-can-i-use-imagedisk-imd-images-with-virtualbox-winimage-etc"
  - name: "keirf / disk-utilities"
    url: "https://github.com/keirf/Disk-Utilities"
  - name: "UNIX System V, release 4 : programmer's guide"
    url: "https://archive.org/details/unixsystemvrelea0000unse_b3c8"
---

最近考古上瘾，这次打算安装一下 UNIX 的老祖：AT&T System V Unix。顺便装上 C 编译套件，体验一下上古编程的感觉。本来还想装一个图形化环境玩玩，但最终因为没有找到对应的软盘而放弃。

## 主系统

首先是要[下载安装镜像](./assets/AT%26T%20UNIX%20System%20V%20Release%204%20Version%202.1%20(3.5).7z)。这一次下载下来的是若干张 3.5 英寸软盘镜像。安装就从这些软盘镜像开始。创建一个虚拟机，添加 IDE 硬盘以及 I82078 软驱设备，记得不要调过高的 RAM，然后插入启动，软驱中插入 `Base 01 (2.1a).img`，启动：

![Panic!](./assets/panic.png)

然后系统就 Panic 了。原因是所谓的![「504MB 限制」](http://www.steunebrink.info/bioslim.htm#Contents)。

## 编译器
