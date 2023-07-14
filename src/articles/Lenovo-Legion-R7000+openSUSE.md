---
uuid: "27229a58-7f89-47b6-b217-54f35d638fb1"
title: Lenovo Legion R7000 安装 openSUSE
date: 2022-07-13
category: 杂项
---

# Lenovo Legion R7000 2021 + openSUSE + i3wm 配置

1. 不要使用openSUSE Leap，目前的Leap(15.3)无法识别无线网卡驱动。Tumbleweed可以识别。
  
2. 在BIOS设置里将输出设置从"集显输出"改为"混合输出"，否则在suspend后无法苏醒。
  
3. 如果使用KDE，避免使用Wayland模式，否则CPU占用会暴涨导致无法使用。
  

## 1. 操作系统安装

我原本使用的是KDE Neon系统，它在我的老电脑上运作的很好，但我打算在新的电脑上使用非基于Ubuntu和dpkg的系统。Arch太复杂了，最后选择了openSUSE。

openSUSE有Leap和Tumbleweed两个分发，由于滚动更新曾经搞坏过我的系统，我首先选择了Leap。但是安装出现了两个问题：

- 无线网卡没法显示出来。安装以后也识别不出来。可能是因为Leap的内核版本太老了。
  
- Xorg无法正常启动。虽然我安装的时候选择的默认启动模式是图像界面，但进去还是tty，并且没法`startx`启动Xorg。不知道是什么问题。
  

所以我最后安装了Tumbleweed。滚动更新那就两个星期滚一次。而且之后我了解到SUSE使用的btrfs有快照功能，就不用怕滚坏掉系统了。

安装的过程很顺利，Tumbleweed可以识别所以的硬件，并且安装以后(保险起见我还是安装了KDE全家桶)也可以正常的启动。

## 2. Nvidia驱动安装

这台电脑用的是RTX 3050显卡，我不懂这些型号而且也不玩游戏。不过有一个超棒的显卡似乎也不错，那我就觉得要安装一下Nvidia的私有驱动。我按照指南上的成功安装了。

```shell
sudo zypper addrepo --refresh https://download.nvidia.com/opensuse/tumbleweed NVIDIA
sudo zypper in x11-video-nvidiaG05
```

不过注意安装要在tty模式进行不然可能会出现什么幺蛾子(

安装完毕以后就可以打开`nvidia-settings`调控显卡啦！

## 3. 窗口管理器安装

我以前一直使用KDE全家桶，不过一来我想尝尝鲜，二来买这台电脑没有送我鼠标，最重要的是这个电脑左右两侧的USB口只有一个，导致我根本不够用，所以我打算使用平铺式窗口管理器。

我参考了一些最后选择使用i3-gap，因为它不只是只有平铺一种模式，也可以切换为浮动模式，这样要是我愿意也可以换回去。而且比起原版的i3，它多一个gap，所以不同的窗口之间可以有空隙，更加好看！软件源里面就有i3-gap所以只需要

```bash
sudo zypper install i3-gap 
```

就可以了。然后众所周知平铺式窗口管理器强烈依赖于键盘(好在Fn+Space切换键盘灯依旧可以用)，所以需要大量的配置。我把大量的快捷键重新map了一遍，<del> 这样其他人就没法用我的电脑啦！</del> 这其实蛮困难的因为总是有好多矛盾的键。我使用了Mod1(Alt)和$Mod(Super)这两个功能键。我打算以后配置完整了上传github备份一下免得丢了。

## 4. 多媒体解码器安装

openSUSE没法直接播放mp3之类的格式，据说是因为版权原因巴拉巴拉的什么，总之，要想正常播放多媒体，直接安装vlc肯定是不行啦。所以需要一个叫做`packman`的第三方源来安装<del>甩锅</del>这些解码器。具体的来讲就是：

```bash
sudo zypper ar -cfp 90 https://ftp.gwdg.de/pub/linux/misc/packman/suse/openSUSE_Tumbleweed packman
sudo zypper dup --from packman --allow-vendor-change
sudo zypper install --from packman ffmpeg mpv libavcodec-full vlc-codecs
```

三条指令执行下来就可以播放电影和音乐啦！

## 5. 下拉终端

这个对我来说很重要，就像对一个人讲话一样，时不时对电脑讲一两句，专门打开一个shell再关掉就太麻烦了。所以需要下拉终端。

我考虑了我以前使用的KDE的`Yakuake`，但是它有一些问题，首先是没法正确的混成。导致只有一半的窗口被渲染；其次是它没法正确的被对待为一个"下拉窗口"，总是被i3当作普通的窗口，一下子就占满整个屏幕；最后kde系列软件需要的软件包好多啊。所以我选择了另外一个下拉终端`guake`，虽然我真的很不喜欢它的名字"挂科"......

## 6. 终端模拟器

默认的终端模拟器(就是$mod+Shift+Enter启动的那个)是很丑很丑的`uxterm`。虽然配置一下也可以很好看，但是我决定使用其他的模拟器。我选择了`alacritty`。本来是想用`kitty`的，但是它对于中文输入法似乎支持不够友好，所以即使有很多好功能，比如标签页功能(可以用`termux`替代)，也没有选择它。

## 7. 壁纸

壁纸当然是使用`feh`来设置。我本来想使用`mpv`搞一个动态的视频壁纸，但好像和混成器起了冲突。

```bash
feh --bg-scale wallpaper_file.jpg
```

记得加在i3的配置文件里面自启动。

## 8. 状态栏

当然是使用`polybar`啦！我在github上下载了著名的`adi1090x/polybar-themes`里面的主题。不过要注意，里面的东西**不能直接用**而是要按照自己电脑的实际情况改动。比如里面关于显示wifi状态的网络接口名称每一台电脑都不一样，又比如显卡的亮度读取amd和intel也不一样。

这些东西，包括栏的显示的内容都可以直接改它的主题文件。具体的就是`~/.config/polybar/主题名字/config.ini`里面的`modules-left`,`modules-center`和`modules-right`这些内容。可用的模块可以在同目录里面的`modules.ini`和`user_modules.ini`    里面找到和更改。最后启动`polybar`只需要在i3 config里面exec 主题文件夹里面的`launch.sh`就可以了。

另外，原版的`i3-status`也可以保留。我是默认隐藏，只有按特殊键才会显示。里面的内容是一些诸如IP地址之类的不常用的信息。

## 9. 混成器

混成器我使用的是`picom`，还有一个`compton`可以选择，但是两个软件似乎是矛盾的，安装一个就会自动卸载另外一个。不管怎么说其实都很好啦！

不管需要注意的是，zypper安装的`picom`只有`kernel`这一个模糊方式，如果需要其他的实验性模糊后端必须自己编译github上的源码。

## 10. 网络管理

<del>其实也不是是不能用`nmtui`</del> 使用`nm-applet`就解决了。

但还是有问题：总是扫描不出wifi网络。不知道是驱动的问题还是`NetworkManager`的问题了。总之思考一下以后我使用另外一个方法上网，使用手机的USB tethering功能，即插即用完全不用密码什么的。

## 11. 输入法

如果在安装时候选择中文，或者安装以后在yast2里面更改语言为中文，那么中文输入法，词库，字体都会一股脑自动安装上来直接就可以使用，但是，一旦把语言改回英文，yast2就会自作聪明的把这一切都删光光......

所以，最好的方法就是自己手动安装一下了。我安装的是`ibus`和`rime`输入法。

```bash
sudo zypper install ibus ibus-rime
```

安装成功以后，还需要在`ibus-setup`里面启用安装的输入法才可以使用。最后不要忘记把守护进程添加到i3的自启动里面。

```bash
exec-always --no-startup-id ibus-daemon -drx
```

## 12. 锁屏

锁屏是很必要的。然而i3lock实在是太简陋了，所以有很多加强版的快捷锁屏。

- **i3lock-fancy**
  
  仓库地址是 https://github.com/meskarune/i3lock-fancy.git
  
  这其实是一个shell脚本，用来调用原来的i3lock，可以设置截图背景模糊灰度之类的。其实和自己写一个脚本调用convert和scort差不多但是别人写的更方便通用一些。
  
- **i3lock-color**
  
  仓库地址是 https://github.com/Raymo111/i3lock-color
  
  这个是fork的原来的i3lock并且加入了许多高级功能，比如可以更改显示位置，显示时间日期什么的。需要自己编译，或者也可以直接下载release。在仓库里面`example`目录里面有demo脚本可以自己改。
  
- xsecurelock
  
  这个和i3lock没有关系，是谷歌的独立项目。好处在于首先是安全，其次是可以使用mpv作为后端来搞动态锁屏。需要自己编译。
  

## 13. 背光调节

<del>我看网上的i3背光调节都是使用`xbacklight`但是我的完全不起作用，所以我自己用`xrandr`写了一个脚本绑定快捷键，聊胜于无吧.</del>

`xbacklight` 不起作用的原因：

**`xbacklight` only works with Intel. Other drivers (e.g. Radeon) did not add support for the RandR backlight property.**

``` sh
#!/bin/bash
B_FILE=~/Ramdisk/backlight

if [ ! -f $B_FILE ];then
        echo 'No backlight file found.'
        echo '1.0' > $B_FILE
fi

old_light=$(cat ~/Ramdisk/backlight)

if [ $1 == inc ];then
        new_light=$(echo $old_light '+0.1' | bc )
else
        new_light=$(echo $old_light '-0.1' | bc )
fi

xrandr --output eDP --brightness $new_light
echo $new_light > $B_FILE
```

## 14. 通知管理

其实通知并不是很多。所以简单地使用dunst再抄一份官网上的配置文件就足够了。

## 15. U盘自动挂载

相比与完整的桌面环境，i3好像没有可以自动挂载的机制，所以需要手动操作。但是每次sudo mount实在是太麻烦，我找了一下，可以使用`udiskie`来自动操作。那就下载一个好了。

缺点在于，现在i3的自启动daemon有六七个之多......