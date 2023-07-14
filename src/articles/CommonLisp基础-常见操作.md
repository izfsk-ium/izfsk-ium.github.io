---
uuid: "704f2611-4448-4f94-a4c1-7b797aad7a43"
title: CommonLisp基础-常见操作
date: 2023-01-20
category: 学习
---

本文记录 CommonLisp 的一些常见操作，记住，**[UIOP](https://quickdocs.org/uiop) 是你的好朋友**！

# 字符串操作

首先，在 CommonLisp 中，字符串既是 array 也是 sequence。所以，适用于它们的操作也适用于字符串。因此可以使用相应的操作：

```lisp
(length "Hello!") ;; 6
(elt "Hello!" 0) ;; #\h
(remove #\a "alpha") ;; "lph"
(count-if #'digit-char-p "Hello!114514") ;; 6
```

因此，字符串的拼接：

```lisp
 (concatenate 'string "hello" " " "world") ;; "hello world"
```

其他 String 类型专有的操作：

## 创建字符串

使用双引号创建字符串，除此以外，使用 `format nil` 返回一个新的字符串，使用 `make-string` 创建一个给定长度的字符串，如果需要从一个字符串创建字符，使用 `coerce`，反之使用 `string`：

```lisp
(string "Hello world")
(format nil "Hello!") ;; "Hello!"
(coerce "a") ;; #\a
(make-string 3 :initial-element #\a) ;; "aaa" 
```

## 字符串切片

使用 `subseq` 来获取字符串切片，格式为：`(subseq string start end)` ：

```lisp
(subseq "hello!" 2 4) ;; "ll"
```

## 获取单个字符

除了 `elt` 以外也可以使用 `char` ，`schar`来获取字符串的单个字符，结合 `setf` 来做到类似 `target[0] = 'A'` 这样的替换：

```lisp
(char "你好" 0) ;; #\U4F60
(setf (char *some-string* 6) #\a)
```

## 获取字符的码位

每一个字符都有一个数字和它对应，具体的数字与实现相关，一般就是 Unicode 。`code-char` 和 `char-code` 类似于 Python 中的 `chr` 和 `ord` 函数：

```lisp
(code-char 124) ;; #\|
(char-code #\和) ;; 21644
```

## 更改字符串

### 移除和替换

序列类型的标准操作，可以使用以下操作对字符串进行：

```lisp
(remove #\0 :start 2 "0000001") ;; "001"
(substitute #\a #\b "aaaabbb") ;; "aaaaaaa"
```

### 字符串拼接

使用 `concatenate` 来拼接字符串，**需要提供结果类型 `string`**：

```lisp
(concatenate 'string "hello" "world") ;; "helloworld"
```

如果你有 `UIOP` ，使用 `uiop:strcat` 亦可，除此以外，不要忘记 `format` 可以用来应对复杂的拼接和格式化操作。

## 大小写

```lisp
* (string-upcase "cool")    ;; "COOL"
* (string-upcase "Cool")    ;; "COOL"
* (string-downcase "COOL")    ;; "cool"
* (string-downcase "Cool")    ;;"cool"
* (string-capitalize "cool")    ;;"Cool"
* (string-capitalize "cool example")    ;;"Cool Example"
```

所有这些函数接收 `:start` 和 `:end` 参数指示开始和结束的位置。

**注意**：`STRING-UPCASE`, `STRING-DOWNCASE` 和 `STRING-CAPITALIZE` 不会修改原来的字符串。但是，如果字符串中没有字符需要转换，则结果可能是字符串或其副本，由实现自行决定。

## 去除空格

```lisp
* (string-trim " " " trim me ")    ;; "trim me"
* (string-trim " et" " trim me ")    ;; "rim m"
* (string-left-trim " et" " trim me ")    ;; "rim me "
* (string-right-trim " et" " trim me ")    ;; " trim m"
* (string-right-trim '(#\Space #\e #\t) " trim me ")    ;; " trim m"
```

## 寻找和搜索

在一个字符串中寻找特定字符和在序列中寻找元素类似。使用 `find` `find-if` 和 `position`  和 `position-if` 来达到目标，要寻找字符串，使用 `search`：

```lisp
(find #\e "Hello world!") ;; #\e
(find-if #'digit-char-p "Hello 1000!") ;; #\1
(position #\a "Hello alpha!") ;; 6
(search "we" "If we can't be free we can at least be cheap")    ;; 3
(search "FREE" "If we can't be free we can at least be cheap" :test #'char-equal)    ;; 15
```

## 类型转换

- string -> integer
  
    使用 `parse-integer` 来转换，使用 `junk-allowed` 来允许垃圾：
  
  ```lisp
  (parse-integer "100 is very good" :junk-allowed t)    ;; 100
  (parse-integer (prompt-read "Rating") :junk-allowed t)    ;; 获取用户输入，转换数字
  ```

- string -> float
  
    很遗憾，没有内置的方法。外部函数库 [parse-float](https://github.com/soemraws/parse-float) 可以做到这一点. 它不使用 `read-from-string` 所以可以安全使用。

- number -> string
  
    使用 `write-to-string` 来转换，当然也可以使用 `format`：
  
  ```lisp
  * (write-to-string 250)    ;; "250"
  * (write-to-string 250.02)    ;; "250.02"
  * (write-to-string 250 :base 5)    ;;"2000"
  * (write-to-string (/ 1 3))    ;;"1/3"
  ```

## 字符串切分

很遗憾，还是没有，不过 `uiop` 中提供了解决方案：

```lisp
 (uiop:split-string "hello world" :separator " ") ;; ("hello", "world")
```

# 输入输出

使用 `read-line` 来从标准输入读取，使用 `write-line` 来输出。除此以外，还可以使用 `print` 来打印，`format` 来执行复杂的格式化：

| 形式         | 描述          | 举例                      |
| ---------- | ----------- | ----------------------- |
| read-line  | 读取一行        | `(read-line)`           |
| read-char  | 读取一个字符，多余丢弃 | `(read-char)`           |
| write-line | 输出一行，自动换行   | `(write-line "Hello!")` |

没有标准的 `prompt` 之类的函数，你可以定义一个：

```lisp
(defun prompt-read (prompt)
    (format *query-io* "~a: " prompt)
        (force-output *query-io*)
        (read-line *query-io*))
```

## `format`

类似于 `C` 中的 `printf`，`format` 是一个强大的格式化工具。它接受两个必要参数：一个用于输出的目的地,另一个含有字面文本和嵌入指令的控制字符串，紧随其后的是一系列格式化参数。第一个输出目的地是 `T`、`NIL`、一个流或一个带有填充指针的字符串。如果输出对象是 `T`，那么就输出到标准输出，也就是 `*STANDARD-OUTPUT*`，如果是 `NIL`，直接返回字符串。控制字符串的作用类似于 C 中 `printf` 格式字符串的作用，本质上是一个用来描述格式的语言。<del>这就导致了很容易写出类似动物反刍噪音一般无法理解的东西</del>。

与 C 不同，**所有的格式指令以 `~` 开头，而不是以 `%` 开头**，指令不区分大小写。~之后的是单个英文字符的指令，以及一个可能的前缀，这个前缀可以是多个字符，使用逗号分割。

常见指令列表：

- `~a`：消耗一个格式化参数，转换成<del>它认为人类可读</del>的形式。例如：
  
  ```lisp
  (format t "~A ~A ~A ~A" '() 100 #'oddp "Hello!")
  ;; NIL 100 #<FUNCTION ODDP> Hello!
  (format t "~A ~A ~A ~A" nil (list 1 2 3) pi #\💗)
  ;; NIL (1 2 3) 3.141592653589793d0 💗
  ```

- `~s`：和 `~a` 效果类似，但将输出生成为可被 `READ` 读回来的形式：
  
  ```lisp
  (format t "~S ~S ~S ~S" nil "Hello!" pi #\💗)
  ;; NIL "Hello!" 3.141592653589793d0 #\GROWING_HEART
  ```

- `~%` 和 `~&`：产生新行。`~%` 总是产生一个换行,而 `~&` 只在当前没有位于一行开始处时才产生换行。可以添加前置参数指定要产生的换行的数量。例如：` (format t "~5&")` 将会产生 5 个空行。

- `~~`：产生波浪线，在之前使用数字控制产生多少个波浪线。

- `~c`：字符。

    打印单个字符，可以使用控制字符来控制特殊字符的展开方式：

    - 直接使用打印字符本身：`(format nil "~c" #\SPACE) -> 一个空格`
    - 使用 `:` 修改符号打印特殊字符的名称：`(format nil "~:c" #\SPACE) -> Space`
    - 使用 `@` 修改符号打印字符的 lisp 表示方式：`(format nil "~@c" #\SPACE) -> #\SPACE`
    - `:` 和 `@` 可以混合使用，并非所有的 Lisp 都实现了 `~C` 指令的这个方面。

- `~d`，`~x`，`~o` 和 `~b`：整数输出。

  `~d`：添加 `:` 在千位数字之间添加逗号；田间 `@` 总是显示正负号，第一个前置参数可以指定输出的最小宽度,第二个参数可以指定一个用作占位符的字符，第三个参数是给 `:` 作为分割符号的符号，第四个参数是 `:` 分割下每一组数字的数量。举例：

    ```lisp
    (format nil "~16,'_,'-,2:@d" 114514)
    "_______+11-45-14"
    ```
  
  参数是 `16,'_,'-,2:@`，四个参数分别是 `16`，`'_`，`'-`，`2`，以及开关 `:` 和 `@`。

  另外三个 `~x` `~o` 和 `~b` 和 `~d` 类似，但输出分别是 16 进制，8 进制和 2 进制：

    ```lisp
    (format nil "~16,'_,'-,2:@b" 114514)
    "+1-10-11-11-11-01-01-00-10"
    ```

- `~r`：更加复杂的整数控制。
  
  `~r` 可以输出为 2-36 进制，第一个参数即为输出进制数。其他参数和之前相同，另外，在没有第一个参数时，拼写成英文单词，按照选项的不同，还可以拼写成罗马数字。

  ```lisp
  (format nil "~36,8,'-:@r" 1000)
  "-----+RS"
  (format nil "~@r" 1514)
  "MDXIV"
  (format nil "~:@r" 1514)
  "MDXIIII"
  (format nil "~:r" 1514)
  "one thousand five hundred fourteenth"
  (format nil "~r" 1145141919810)
  "one trillion one hundred forty-five billion one hundred forty-one million nine hundred nineteen thousand eight hundred ten"
  ```

- `~f` 和 `~e`：浮点数
  
  `~f`：使用计算机科学记数法，十进制输出，第二个参数控制在十进制小数点之后打印的数位个数。`@` 选项开启正负号。

  ```lisp
  (format nil "~,5@f" pi)
  "+3.14159"
  ```

  `~e` 和 `~f` 类似，但是输出数字时总是使用科学计数法。

除此以外，还有英语指令，生成带有正确复数化单词的消息。使用 `~p` 即可，如果对应的参数大于 1 ，输出一个 `s`，所以，类似这样的 Python 代码：

```python
f"Total {number} {'element' if number == 1 else 'elements'}"
'Total 45 elements'
```

可以是：

```lisp
(format nil "Total ~d element~p" 14 14)
"Total 14 elements"
```

可以开启 `:` 和 `@`，让它重新处理前一个格式化参数，以及自动添加单词的复数：

```lisp
(format nil "~r file~:p" 1) → "one file"
(format nil "~r famil~:@p" 0) → "zero families"
```

对于大小写，可以使用 `~( ~)` 处理，它接收 `@`，`:` 开关：

```lisp
(format nil "~(~a~)" "tHe Quick BROWN foX")   ; => "the quick brown fox"
(format nil "~@(~a~)" "tHe Quick BROWN foX")  ; => "The quick brown fox"
(format nil "~:(~a~)" "tHe Quick BROWN foX")  ; => "The Quick Brown Fox"
```

以及更加复杂的条件格式化，迭代格式化和跳跃格式化。还能够生成表格。<del>希望不要用到它们</del>

# 文件

和很多其他编程语言一样，CommonLisp 也用「流」来表示输入和输出。而想 `format` 和 `read` 这样的函数，其作用对象也是一个流。读取和写入文件，需要几个函数：
`open`，`make-pathname` 等。

`make-pathname` 制造出合法的文件路径名称，它只接收关键词参数，有六个：`host`、`device`、`directory`、`name`、`type` 及 `version`，返回一个路径名称：

```lisp
(make-pathname :directory "/home/izfsk/" :name "file")
;; #P"//home/izfsk//file"
```

接下来是打开文件，使用 `open` 函数。这个函数很复杂，它接受一个路径名和大量关键字参数，开启成功时返回指向文件的流。常见的关键词参数有 `:direction`，决定是写入流还是读取流，选项有
`:input`，`:output`，`:io`，还能够指定文件存在时是否覆盖，使用 `:if-exist` 参数，使用 `:supersede` 覆盖。打开以后，你就可以使用 `format` 等函数写入读取了。在最后要记得使用 `close` 关闭流。举例：

```lisp
(let ((target-file-stream
        (open (make-pathname :directory "/home/izfsk" :name "file")
              :direction :output
              :if-exists :supersede)))
  (format target-file-stream "Hello!")
  (close target-file-stream))
```

就像 Python 有上下文管理器，使得你可以写出 `with open(file) as fp` 一样， CommonLisp 也有一个宏帮助你管理流，使用 `with-open-file` 可以管理，用它重写上面的例子：

```lisp
(with-open-file (target-file "/home/izfsk/file"
                             :direction :output
                             :if-exists :supersede
                             :if-does-not-exist :create)
  (format target-file "Hello!"))
```

读取示例：

```lisp
(let ((in (open "/some/file/name.txt")))
  (format t "~a~%" (read-line in))
  (close in))
```

# 参考

- [Common Lisp: Format](https://www.alexeyshmalko.com/20210927132804/)
- [Practical Common Lisp -- 14. Files and File I/O](https://gigamonkeys.com/book/files-and-file-io.html)
- [The Common Lisp Cookbook – Files and Directories](https://lispcookbook.github.io/cl-cookbook/files.html#writing-content-to-a-file)