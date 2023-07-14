---
uuid: "6f21a5a7-d7da-48e5-8afc-54d5644d73bf"
title: Chrome文件伪装摄像头
date: 2022-12-31
category: 备忘录
---

有时候需要用到伪装摄像头的功能，特别是使用某些网课平台考试的时候，有的建议是使用 OBS Studio 模拟一个摄像头，但是其实 Chrome 浏览器就可以把文件作为摄像头的视频来源采集。

# 文件准备

首先你需要有视频或者图片文件，但一般的 mp4, mkv 之类的格式是不行的。关于 Chrome 支持什么格式，手册页里面没有说明，但是源代码里面有：

```c++
// https://chromium.googlesource.com/chromium/src/+/3015459a9bf07f62ab7a8816ff88824568d87c04/media/capture/video/file_video_capture_device.cc
// line 286
if (base::EndsWith(file_name, "y4m",
                     base::CompareCase::INSENSITIVE_ASCII)) {
    file_parser.reset(new Y4mFileParser(file_path));
  } else if (base::EndsWith(file_name, "mjpeg",
                            base::CompareCase::INSENSITIVE_ASCII)) {
    file_parser.reset(new MjpegFileParser(file_path));
  } else {
    LOG(ERROR) << "Unsupported file format.";
    return file_parser;
  }
```

要作为流的来源你需要 y4m 或者 mjpeg 格式的视频。使用 ffmpeg 可以转换。

``` shell
$ ffmpeg -i input.mp4 output.y4m
```

# 开启选项

接下来你需要使用命令行参数启动 Chrome 浏览器，加上你的文件：

``` shell
$ google-chrome --use-fake-device-for-media-stream --use-file-for-fake-video-capture=test.y4m 
```

# 检测和注意事项

- y4m 格式是很大的，一分钟不到的视频都可能达到 700 MB。
- 可以使用[这个网站](https://webcamtests.com/)来测试。
- 网页检测到的「摄像头硬件名称」将会是你的文件名，注意起一个正常的名字。

# 参考

1. [How can I correctly provide a mock webcam video to Chrome?](https://stackoverflow.com/questions/52095416/how-can-i-correctly-provide-a-mock-webcam-video-to-chrome)