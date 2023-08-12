---
uuid: "8f47beda-8cb7-4835-a463-a60e6ac2dcd5"
title: Adalang初探
date: 2023-03-24
category: 学习
draft: true
---

学习 Ada 的原因无非是两个：一是好奇这个从来没有接触过的语言，二是想要尝试一个不同「风格」的语言。

首先是要安装开发环境。Ada 语言是 GCC 编译器集合里面官方支持的。但光有编译器还不行，还需要工具链条，以及 IDE。具体的来讲就是：

- 安装 GNAT：`sudo zypper in gcc-ada`；
- 安装 GPRBuild，Ada 的项目管理工具，需要在 OBS 里面下载：[The GPRBuild Ada/multilanguage build tool](https://build.opensuse.org/package/show/home:vibondare:devel:languages:Ada/gprbuild)

创建和编译运行的简单示例：

1. 创建 gpr 项目文件:

    ```ada
    project Default is
        for Main use ("main.adb");
        for Object_Dir use "obj";
        for Source_Dirs use ("src/**");
    end Default;
    ```

2. 创建源文件：

    ```ada
    --- src/lib/hello.ads
    package hello is
        procedure SayHello;
    private
    end hello;

    --- src/lib.hello.adb
    with Ada.Text_IO; use Ada.Text_IO;
    package body hello is
        procedure SayHello is
        begin
            Put ("Hello!");
        end SayHello;
    end hello;

    --- src/main.adb
    with hello;

    procedure main is
    begin
        hello.SayHello;
    end main;
    ```

3. 编译运行：

    ```bash
    gprbuild && ./obj/main
    ```

可以看到相比于 C 系的大括号语言和 Python 系的游标卡尺语言，Ada 在语法上有明显的不同，举个例子：

```ada
 with Ada.Text_IO;                                       --  1
 procedure Hello is                                      --  2
 begin                                                   --  3
     Ada.Text_IO.Put ("Hello world!");                   --  4
     Ada.Text_IO.New_Line;                               --  5
 end Hello;                                              --  6
```

首先，Ada 是**严格区分「过程」和「函数」的**。函数**必须**返回一个值，而过程不一定需要。我印象里面似乎只有 Pascal 这样干。Functions 和 Procedures 都是 `Subprograms`。函数作为表达式的组成部分被调用，并返回一个值作为表达式的一部分，而过程就是「一组语句」。定义一个过程如下：

```ada
procedure 过程名 (参数) is
    --- 需要用到的变量等信息
begin
    --- 过程体
end 过程名;
```

调用过程则是：`过程名 + 括号`。比较奇特的是，如果过程没有参数，那么调用也不需要括号。所以直接调用 `New_Line` 是换行，加一个括号调用 `New_Line(10)` 则是 10 个空行：

```ada
with Ada.Text_IO;         use Ada.Text_IO;
with Ada.Integer_Text_IO; use Ada.Integer_Text_IO;
--- hello
package body hello is
    procedure SayHello (Name : in String := "Someone") 
        LengthOfName : Integer := Name'Length;
    begin
        Put ("Hello! ");
        Put (Name);
        Put (LengthOfName);
    end SayHello;
end hello;
```

这里还有几个点：首先是过程的参数有 `in` 和 `out` 两种，`in` 关键字表示参数在过程中是只读的，这意味着过程可以访问参数的值但不能修改它。`out` 关键字表示参数在过程中是只写的，这意味着过程可以修改参数的值但不能读取其原始值；其次获取一个对象的属性是使用 `'` 符号而不是其他语言的 `.` 表示方法，所以获取字符串的长度就变成了 `Name'Length`；再者，给一个变量赋值是使用 `:=` 符号而非 `=` 符号、指明类型（Ada 是强类型语言，必须指明类型）是使用 `:`，这一点倒是和 Typescript 一致，最后，注释使用 `---` 符号。所以可以很方便的框一个大框出来（

另外，Ada 中的定义变量**必须**在 begin 之前。

调用：

```ada
hello.SayHello ("izfsk");   --- 直接调用
hello.SayHello (Name => "izfsk");   --- 按照名字调用
hello.SayHello; --- 默认
```

相比之下，定义一个函数是这样的，必须要指明返回类型。调用方法和过程类似。

```ada
function add (a : Integer := 10; b : Integer := 20) return Integer is
begin
  return a + b;
end add;
```

接下来是喜闻乐见的基本 statements 环节，举例说明：

## If

```ada
-- Example 1: using multiple conditions in if statement
if A > 0 and then B < 30 then
   Put_Line("A is greater than 0 and B is less than 30.");
end if;

-- Example 2: using if statement with elsif and else clauses
if A > B then
   Put_Line("A is greater than B.");
elsif A < B then
   Put_Line("A is less than B.");
else
   Put_Line("A is equal to B.");
end if;

-- Example 3: using if statement with logical negation
if A /= B then
   Put_Line("Something");
end if;
```

**注意**，判断相等是 `=` 而不是 `==`，判断不相等是 `/=` 而非 `!=`。除此以外，判断是否在一个范围可以这样：`if Number in 1 .. 100 then`。

## case (switch)

```ada
procedure Greetings is
  Answer : Character;
begin
  Put ("Is it morning (m) or afternoon (a)? ");
  Get (Answer);
  case Answer is
      when 'M' | 'm' =>                    -- 1
          Put_Line ("Good morning!");
      when 'A' | 'a' =>                    -- 2
          Put_Line ("Good afternoon!");
      when others =>                       -- 3
          Put_Line ("Please type 'm' or 'a'!");
  end case;
end Greetings;
```

以及范围测试：

```ada
case Answer is
  when 'A' .. 'Z' | 'a' .. 'z' =>
      Put_Line ("Letter!");
  when others =>
      null;  -- 啥都不做
end case;
```

## loop

首先 Ada 中的 `do` 大致可以替换成 `loop`，所以：

```c
while (1){
    // do something
}
```

就是

```ada
while True loop
    --- do something
end loop;
```

## for

```ada
for N in 1..20 loop
  Put ("*");
end loop;
```

## 异常处理

Ada 内置了完整的异常处理机制：

```ada
procedure Calculator is
begin
  --- code to process data
exception
  when Constraint_Error =>
      Put_Line ("Value out of range");
  when Program_Error | Data_Error =>
      Put_Line ("Error in input -- integer expected");
end Calculator;
```

Ada 中有以下几种异常：

- `Constraint_Error`：当某个值不符合类型限制时抛出
- `Program_Error`：当程序出现逻辑错误时抛出
- `Storage_Error`：当程序无法分配足够的内存时抛出
- `Tasking_Error`：当任务相关的错误发生时抛出
- `Numerics_Error`：当数字计算出现错误时抛出
- `Check_Error`：当某些检查失败时抛出
- `System_Error`：当系统错误发生时抛出
- `Use_Error`：当程序使用不正确时抛出
- `Assertion_Error`：当程序中的断言失败时抛出

## MultiTasking

说起 `MultiTasking` 现在第一个想到的就是 `Golang`，但 Adalang 这个比我的年龄还大的语言也可以做到：而且一点也不勉强：

```ada
procedure Show_Simple_Tasks is
   task T;
   task T2;

   task body T is
   begin
      delay 1.25; --- sleep 1.25 秒
      Put_Line ("In task T");
   end T;

   task body T2 is
   begin
      delay 2.25; --- sleep 2.25 秒
      Put_Line ("In task T2");
   end T2;

begin
   Put_Line ("In main");
end Show_Simple_Tasks;
```

程序的输出是

```js
In main
In task T
In task T2
```

并且是并行的。

`select` 也可以轻松实现：

```ada
procedure Show_Rendezvous_Loop is
   task T is
      entry Reset;
      entry Increment;
   end T;

   task body T is
      Cnt : Integer := 0;
   begin
      loop
         select
            accept Reset do
               Cnt := 0;
            end Reset;
            Put_Line ("Reset");
         or
            accept Increment do
               Cnt := Cnt + 1;
            end Increment;
            delay 1.0;
            Put_Line ("In T's loop (" & Integer'Image (Cnt) & ")");
         or
            terminate;
         end select;
      end loop;
   end T;

begin
   Put_Line ("In Main");

   for I in 1 .. 4 loop
      T.Increment;
   end loop;

   T.Reset;

   for I in 1 .. 4 loop
      T.Increment;
   end loop;
end Show_Rendezvous_Loop;
```

结果：

```elisp
In Main
In T's loop ( 1)
In T's loop ( 2)
In T's loop ( 3)
In T's loop ( 4)
Reset
In T's loop ( 1)
In T's loop ( 2)
In T's loop ( 3)
In T's loop ( 4)
```

编译结果 `-rwxr-xr-x 1 izfsk izfsk 359K Mar 26 21:09 Show_Simple_Tasks`

总而言之，Ada 是一个超越时代的语言，它有类似 Golang 甚至 Rust 的一些特性，而且语法也很优雅，但时代局限了它。

## 参考

1. [Ada 语言参考](https://www.adaic.org/resources/add_content/docs/craft/html/appa.htm)
2. [Adacore 提供的学习资源](https://learn.adacore.com)
3. [学习资源列表](https://www.adaic.org/learn/materials/)
