---
uuid: "23d00329-9a40-41dc-96e4-673f89a6d1b6"
title: GNU・Parallel使用例
date: 2023-02-19
category: 整理
---

当需要并行处理一堆东西的时候，有时候会考虑 [GNU Parallel](https://www.gnu.org/software/parallel/)，但它真的很复杂，而且总的来讲比较混乱，最好的办法不是从头到尾学一遍，而是按照例子去操作。官方文档也考虑到了这个问题，提供了[例子大全](https://www.gnu.org/software/parallel/parallel_examples.html)，本文是对这些例子的转译，顺便添加一些注解。**注意，这里只保留了我认为有用的例子**，因为这样的工具实在不需要太过复杂的运用。

首先写一个验证程序，显示 `parallel` 到底是怎么给程序添加参数的：

```c
#include <stdio.h>
#include <unistd.h>

int main(int argc, char** argv){
    printf("[%d]Arguments: ", getpid());
    for (int i=0; i!=argc; i++){
        printf(" [%s]", argv[i]);
    }
    printf("\n");
    sleep(1);
    return 0;
}
```

## 替代 `xargs -n1` 使用

很简单，比如你有很多 html 文件要压缩：

`find . -name '*.html' | parallel gzip --best`

当然也可以

`find . -name '*.html' | xargs -n1 gzip --best`

区别就在 parallel 是并行的，使用 `xargs`：

```js
% time ls | xargs -n1 ./a.out
[27602]Arguments:  [./a.out] [31]
[27607]Arguments:  [./a.out] [32]
[27608]Arguments:  [./a.out] [a.out]
[27611]Arguments:  [./a.out] [show.c]
ls --color=tty  0.00s user 0.00s system 73% cpu 0.002 total
xargs -n1 ./a.out  0.00s user 0.00s system 0% cpu 4.006 total
```

而使用 `parallel`：

```js
% time ls | parallel ./a.out 
[27945]Arguments:  [./a.out] [31]
[27946]Arguments:  [./a.out] [32]
[27947]Arguments:  [./a.out] [a.out]
[27948]Arguments:  [./a.out] [show.c]
ls --color=tty  0.00s user 0.00s system 61% cpu 0.001 total
parallel ./a.out  0.08s user 0.03s system 9% cpu 1.076 total
```

可以看到 `parallel` **同时运行** 四个程序，只花了一秒。这也是为什么要用 `parallel` 的原因。所以，同样的，如果碰到视频转码之类的耗费时间的任务，使用 `parallel` 能加快速度不少。

## 简单网络扫描器

`prips 130.229.16.0/20 | parallel --timeout 2 -j0 'ping -c 1 {} >/dev/null && echo {}' 2>/dev/null`

由此可以过滤出返回数据的目标。在这个例子里面，一是要注意换行符号用来分割参数，二是注意使用 `{}` 来包含每一次的参数。另外 `-j` 参数用来控制每一批的操作数量。

## 从命令行读取参数

`parallel` 可以从命令行读取参数，而不是一定要找 `stdin`。例如第一个例子也可以写成：

`parallel gzip --best ::: *.html`

但是只能压缩目前级别的文件。命令行参数同样可以使用 `{}`，例如使用 `ffmpeg` 转码：

`parallel ffmpeg -i {} -o {.}.mp3 ::: *.wav`

在这里，`{.}` 是「取点号之前的字符串」，而 `:::` 则是分割。

```js
% ls
31   32   a.out  'Hello world'   show.c

% parallel ./a.out {} {.} ::: *
[4619]Arguments:  [./a.out] [31] [31]
[4620]Arguments:  [./a.out] [32] [32]
[4621]Arguments:  [./a.out] [a.out] [a]
[4622]Arguments:  [./a.out] [Hello world] [Hello world]
[4623]Arguments:  [./a.out] [show.c] [show]
```

## 突破参数长度限制

有时候你会碰见这样的问题：

```js
% ./a.out `find ~`     
zsh: argument list too long: ./a.out
```

这是因为文件太多了，超出参数长度限制。 传统的方法是使用 `xargs`，但也可以使用 `parallel`：

`find ~ | parallel ./a.out {}`

这会给**每一个操作**单独开一个程序。你可以把每一个的参数加到允许的最大范围来加速操作：

`find ~ | parallel -m ./a.out {} `

## 内容替换

使用

`seq -w 0 9999 | parallel rm pict{}.jpg`

或者

`seq -w 0 9999 | perl -pe 's/(.*)/pict$1.jpg/' | parallel -m rm`

来删除 pict0000.jpg 到 pict9999.jpg。第一个版本允许 `rm` 10000 次，第二个给每一个允许的 `rm` 添加刚好不至于突破参数长度限制的参数，更加快速，也可以这样做：

`seq -w 0 9999 | parallel -X rm pict{}.jpg`

`-X` 的作用是，如果多个作业并行运行，则将参数平均分配给作业。

##  计算密集型作业

你可以使用 `ImageMagick` 来给图片制作缩略图：

`convert -geometry 120 foo.jpg thumb_foo.jpg`

这个版本则能够充分利用你的 CPU：

`ls *.jpg | parallel convert -geometry 120 {} thumb_{}`

也可以递归的来处理所有的文件：

`find . -name '*.jpg' | parallel convert -geometry 120 {} {}_thumb.jpg`

如上所述，使用 `{.}` 来获取文件名，所以如果你想要 *./foo/bar_thumb.jpg* 的文件名，这样做：

`find . -name '*.jpg' | parallel convert -geometry 120 {} {.}_thumb.jpg`

将所有 `wav` 变成 `mp3`，并放到同一个目录：

`find sounddir -type f -name '*.wav' | parallel lame {} -o mydir/{/.}.mp3`

## 替换和重定向

你有很多 `.gz` 文件，你想要获得未压缩版本。你可以这样：

```shell
for file in ./*.gz;do
    zcat $file > "${file%.*}"
done
```

使用 `parallel` 的版本如下：

`parallel zcat {} ">"{.} ::: *.gz`

你需要把 `>` 用引号包围。否则这样做：

`parallel "zcat {} >{.}" ::: *.gz`

其他特殊符号也许要使用引号包围。例如：`* ; $ > < | >> <<`，否则它们会被 shell 解释，而不是传递给 `parallel`。

## 多个命令组合

一个作业可以包含若干条命令，它们之间使用 `;` 分割：

`ls | parallel 'echo {} ; ls {} '`

甚至可以输入一个小脚本：

```haskell
find . | parallel 'a={}; name=${a##*/};' \
  'upper=$(echo "$name" | tr "[:lower:]" "[:upper:]");'\
  'echo "$name - $upper"'

ls | parallel 'mv {} "$(echo {} | tr "[:upper:]" "[:lower:]")"'
``` 

批量下载不是问题。以下命令会打印出下载错误的 url 和行号：

`cat urlfile | parallel "wget {} 2>/dev/null || grep -n {} urlfile"`

创建一个具有相同文件名的镜像目录，除了所有文件和符号链接都是空文件。

`cp -rs /the/source/dir mirror_dir && find mirror_dir -type l | parallel -m rm {} '&&' touch {}`

在文件列表中过滤出不存在的文件：

`cat file_list | parallel 'if [ ! -e {} ] ; then echo {}; fi'`

很长的操作可以写成 shell 函数调用，不要忘记 export -f：

```js
doit() {
  echo Doing it for $1
  sleep 2
  echo Done with $1
}
export -f doit
parallel doit ::: 1 2 3
```

## 多重来源数据替换

举例：

```python
% parallel "./a.out {1} {2}" ::: {a..c} ::: {0..3}   
# Same as `parallel "./a.out {1} {2}" ::: {a..c} ::: 0 1 2 3`
[15696]Arguments:  [./a.out] [a] [0]
[15697]Arguments:  [./a.out] [a] [1]
[15699]Arguments:  [./a.out] [a] [2]
[15700]Arguments:  [./a.out] [a] [3]
[15701]Arguments:  [./a.out] [b] [0]
[15702]Arguments:  [./a.out] [b] [1]
[15703]Arguments:  [./a.out] [b] [2]
[15704]Arguments:  [./a.out] [b] [3]
[15705]Arguments:  [./a.out] [c] [0]
[15706]Arguments:  [./a.out] [c] [1]
[15707]Arguments:  [./a.out] [c] [2]
[15708]Arguments:  [./a.out] [c] [3]
```

可以看到它的替换效果类似于笛卡尔积。

## 移除参数中的特定字符串

如果只有一个后缀名，例如 `a.mp4` 可以使用 `{.}`，同样地，对于诸如 `a.tar.gz` 可以使用 `{..}`，**切记要加上 `--plus` 参数**。

举例：

```python
% ls
a.tar.gz   b.tar.gz   c.tar.gz   d.tar.gz   e.tar.gz

% parallel --plus './a.out {..}' ::: *.tar.gz
[27784]Arguments:  [./a.out] [a]
[27785]Arguments:  [./a.out] [b]
[27786]Arguments:  [./a.out] [c]
[27787]Arguments:  [./a.out] [d]
[27788]Arguments:  [./a.out] [e]
```

同样地，对于更多的 `.` 也可以处理： 

```perl
% ls
a.src.tar.xz   b.src.tar.xz   c.src.tar.xz   d.src.tar.xz   e.src.tar.xz 

% parallel --plus './a.out {...}' ::: *.src.tar.xz
[28960]Arguments:  [./a.out] [a]
[28961]Arguments:  [./a.out] [b]
[28962]Arguments:  [./a.out] [c]
[28963]Arguments:  [./a.out] [d]
[28964]Arguments:  [./a.out] [e]
```

对于任意字符串的替换使用 `%` （后缀）`#` （前缀）和 `/` 正则表达式：

```perl
% ls
aHello  bHello  cHello  dHello  eHello

% parallel --plus '../a.out {%Hello}' ::: *       
[29654]Arguments:  [../a.out] [a]
[29655]Arguments:  [../a.out] [b]
[29656]Arguments:  [../a.out] [c]
[29657]Arguments:  [../a.out] [d]
[29658]Arguments:  [../a.out] [e]

% parallel --plus '../a.out {/ello/}' ::: *
[29835]Arguments:  [../a.out] [aH]
[29836]Arguments:  [../a.out] [bH]
[29837]Arguments:  [../a.out] [cH]
[29838]Arguments:  [../a.out] [dH]
[29839]Arguments:  [../a.out] [eH]
```

用这种方法，可以快捷的重命名。再比如给文件加上时间戳：

`parallel mv {} '{= $a=pQ($_); $b=$_;' '$_=qx{date -r "$a" +%FT%T}; chomp; $_="$_ $b" =}' ::: *`

## 聚合文件内容

以下命令将会生成文件 `x1y01z1` 到 `x5y10z5`：

`parallel --header : echo x{X}y{Y}z{Z} \> x{X}y{Y}z{Z} ::: X {1..5} ::: Y {01..10} ::: Z {1..5}`

## 更好的 `for` 和 `while`

一般的 `for` 循环长这样：

``` haskell
(for x in `cat list` ; do
  do_something $x
done) | process_output
```

以及 `while` 循环：

``` haskell
cat list | (while read x ; do
  do_something $x
done) | process_output
```

可以重写成这样：

`cat list | parallel do_something | process_output`

## 步进

假如你有以下输入：

```
aardvark
babble
cab
dab
each
```

你想要这样：

```
aardvark babble
babble cab
cab dab
dab each
```

对于保存在文件里面的情况，使用这个命令：

`parallel echo {1} - {2} ::::+ <(head -n -1 in.txt) <(tail -n +2 in.txt)`

## 加速快速的任务

在本地机器上启动作业大约需要 3-10 毫秒，如果作业运行时间非常短，这可能是一个很大的开销。可以使用 -X 将小作业组合在一起。例如：

```haskell
seq -w 0 9999 | parallel touch pict{}.jpg
seq -w 0 9999 | parallel -X touch pict{}.jpg
```

## 远程运行

要在远程计算机上运行命令，需要设置 SSH，并且必须能够在不输入密码的情况下登录。

`seq 10 | parallel --sshlogin server.example.com echo`

要将命令分发到计算机列表，为所有计算机创建一个文件：

```
server.example.com
foo@server2.example.com
server3.example.com
:
```

然后运行:

`seq 10 | parallel --sshloginfile mycomputers echo`

其中的 `:` 代表本机。

GNU parallel 将尝试确定每台远程计算机上的 CPU 数量，并为每个 CPU 运行一个作业。

<br/>

本文档的部分来源是 [GNU PARALLEL EXAMPLES](https://www.gnu.org/software/parallel/parallel_examples.html)，其许可证为：

```
Permission is granted to copy, distribute and/or modify this documentation under the terms of the GNU Free Documentation License, Version 1.3 or any later version published by the Free Software Foundation; with no Invariant Sections, with no Front-Cover Texts, and with no Back-Cover Texts. A copy of the license is included in the file LICENSES/GFDL-1.3-or-later.txt.
```