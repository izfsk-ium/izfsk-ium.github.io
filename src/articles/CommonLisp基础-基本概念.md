---
uuid: "f7127a84-86a8-41dc-8fdc-893cd1118438"
title: CommonLisp基础-基本概念
date: 2023-01-18
category: 学习
---

本文整理作为一门编程语言的 CommonLisp 的基本元素，以便「能够用它写出程序来」。

# 历史

[约翰麦卡锡](http://zh.wikipedia.org/zh-cn/%E7%BA%A6%E7%BF%B0%C2%B7%E9%BA%A6%E5%8D%A1%E9%94%A1)和他的学生于 1958 年展开 Lisp 的初次实现工作。 Lisp 是继 FORTRAN 之后，仍在使用的最古老的程序语言。 Lisp 是计算机科学领域的「经典语言」之一，完全是一门现代通用语言,其设计反映了尽可能高效和可靠地求解实际问题的实用主义观点。

# 概念

Lisp 是一门交互式语言。有一个叫做「顶层」的环境运行 Lisp 代码。

所有的 Lisp 代码都是「S-表达式」，但并不是所有的 S-表达式都是合法的 Lisp 代码。宏给了语言的用户一种扩展其语法的方式，把任意的 S-表达式转换成合法的 Lisp 代码。

使用 `quote` 可以防止表达式被求值。例如：

```lisp
'(+ 1 2 3)
```

# 基本类型

## 真和假

符号 `NIL` 是唯一的假值,其他所有的都是真值，符号 `T` 是标准的真值。

测试相等性有四种方法：

- `EQ`：测试「对象标识」，两个对象是同一个东西时才等价。**移植性差，避免使用**。

- `EQL`：类似 `EQ`， 保证当相同类型的两个对象代表相同的数字或字符值的时候是等价的。所以 `(eql 1 1)` 确保是真的。

- `EQUAL` ：将具有递归相同结构和内容的列表视为等价。`(eql '(1 2 3) '(1 2 3)` 为 `NIL`，而 `(equal '(1 2 3) '(1 2 3)'` 为 `T`。

- `EQUALP`：更加宽松的相等。

测试：

```lisp
(defun test-eq (a b)
  (progn
    (print (eq a b))
    (print (eql a b))
    (print (equal a b))
    (print (equalp a b))))
```

|          | a=1,b=1 | a=1,b=1.0 | a="hi",b="hi" | a='(),b='() |
| -------- | ------- | --------- | ------------- | ----------- |
| `eq`     | T       | NIL       | NIL           | T           |
| `eql`    | T       | NIL       | NIL           | T           |
| `equal`  | T       | NIL       | T             | T           |
| `equalp` | T       | T         | T             | T           |

## 数字

CommonLisp 支持整数，浮点数，复数等。

![](https://acl.readthedocs.io/en/latest/_images/Figure-9.1.png)

- 整数：
  
  可以使用常规的写法，也可以使用任意进制写法：
  
  常规写法：`10`，`22/2`，`-14`，`-17`
  
  任意进制写法：二进制：`#b101001`，八进制：`#o777`，使用 `#nR` 以 2 到 36 的其他进制书写有理数

- 浮点数：
  
  同样可以使用多种写法：`1.0`，`1e0`，`0.114514`，`124E-3`，`195d23`

四则运算的截断和舍入：

1. `ceiling`：向正无穷截断，**返回大于或等于参数的最小整数。**

2. `truncate`：向零截断。

3. `round`：舍入到最接近的整数上。如果参数刚好位于两个整数之间它舍入到最接近的偶数上。

4. `floor`：向负无穷方向截断，**返回小于或等于参数的最大整数。**

模和余数：

- 模：`(mod number divisor)`

- 余数：`(rem number divisor)`

变量的增减：`incf`，`decf`

其他：`min`，`max`，`evenp`（检测偶数），`oddp`（检测奇数）

**数字的比较使用 `=`**

## 字符串

### 字符

字符和数字是不同类型的对象，字符的表示：`#\+字符`，例如字符 `H`：`#\H`，字符`和`：`#\和`（`#\U548C`）,特定字符的替代语法是 #\ 后跟该字符的名字。例如 `#\Tab`

字符不是数字，不能使用数值比较函数。使用 `char-equal`。它接受任一数量的参数并
只在它们全是相同字符时返回真，相应的还有 `char-not-equal`，`char-lessp`，`char-not-lessp`，`char-greaterp`等对应 `>`，`<`等。

### 字符串

字符串是字符的一维数组，字面字符串写在闭合的双引号里，使用斜杠来转引 `\` 和 `"` 符号。字符串的比较使用 `string-equal` 系列函数，简单地来讲就是把字符比较系列中的 `char` 替换为 `string`。

```lisp
(string-equal 
    "foobarbaz" "quuxbarfoo"
    :start1 3 :end1 6 :start2 4 :end2 7)
```

## 函数类型

把函数的名字传给 function ，它会返回相关联的对象，用 `#'` 作为 function 的缩写。

使用 `lambda` 定义匿名函数：`(lambda (x) (+ x 100))`

`lambda` 函数：`(lambda (parameters) body)`

## 集合类型

列表和向量的区别应该可以类比为 C++ 中标准库容器和 C array 的区别(？)

### 列表（list）

列表使用括号直接创建：`'()`，也可以使用 `make-list` 来创建。列表是序列的子类型。列表是最常见的数据结构，可以用来模拟树，下推栈等数据结构。

列表的基本元素是 Cons，一个 Cons 可以看作是由一个保存元素的单元和指向下一个元素的指针， `CONS` 最初是动词 construct 的简称，除非第二个值是 NIL 或是另一个点对单元,否则一个点对将被打印两个值在括号中用一个点所分隔的形式，前面一个元素叫做 `car`，后面一个元素叫做 `cdr`。所以，一个包含 1，2 的列表类似于：

```
[O|O]--->[O|null]
 |        |
 1        2
```

它事实上是 `(cons 1 (cons 2 nil))` ，简单写作 `(list 1 2)`。

取出列表元素的基本函数是 car/first 和 cdr/rest 。对列表取 car 返回第一个元素，而对列表取 cdr 返回第一个元素之后的所有元素，你可以使用 setf 来设置一个 cons 单元的 car 或者 cdr：

```lisp
(defparameter *cons* (cons 1 2))
(setf (car *cons*) 10) 
(setf (cdr *cons*) 20) 
```

常用函数：

- `reverse`：翻转列表：`(reverse "hi!")` -> `"!ih"`
- `second` 到 `tenth`：获得某个元素。
- `nth`：接受两个参数,一个索引和一个列表,并返回列表中第 n 个(从 0 开始)元素
- 复合 `car/cdr` 函数：例如：`(cadadr list) ≡ (car (cdr (car (cdr list))))`

 参见：[The Common Lisp Cookbook – Data structures](https://lispcookbook.github.io/cl-cookbook/data-structures.html)

副作用和「破坏性操作」：

纯粹的「函数」是说函数完全基于其参数的值来计算结果，比如 `(+ 5 6)` 是完全「函数式」的。修改已有对象的操作被称作是破坏性的，原来的那个对象的状态改变来了。

### 排序和映射

- 排序使用 `sort` 和 `stable-sort`

  两者会破坏序列。参数是序列和谓词函数。例如：`(sort '(1 2 3 71 29) #'<)`，对一个序列排序并赋值一般使用 `(setf my-sequence (sort my-sequence #'string<))` 的形式。
  可以使用关键词参数 `:key` 来指定复杂数据结构中用来排序的元素。

- 映射

  映射是对高阶函数的使用。有六个用于列表的 map 函数，最常用的是这两个：

  1. `mapcar`：`(mapcar #'+ (list 1 2 3) (list 10 20 30)) → (11 22 33)`
  2. `maplist`：将列表的渐进的下一个 cdr 传入函数。
      `(maplist #'(lambda (x y) (list (first x) (first y))) '(1 2 3 4) '(1 2 3 4)`
      ->
      `((1 1) (2 2) (3 3) (4 4))`

### 树

Cons 对象可以想成是二叉树， car 代表左子树，而 cdr 代表右子树，Common Lisp 有几个内置的操作树的函数。copy-tree 接受一个树，并返回一份副本。

### 集合

CommonLisp 的列表可以看作是一个集合，使用一系列函数来把列表作为集合操作：

- `pushnew`：向一个集合添加元素。
- `member` 和 `member-if`：测试是否在集合中
- `INTERSECTION` 、 `UNION` 、及 `SET-EXCLUSIVE-OR`：集合论相关操作（交集，并集，异或）。

### 栈

`(push x y)` 把 x 放入列表 y 的前端。而 `(pop x)` 则是将列表 x 的第一个元素移除，并返回这个元素。

# 变量和常量

## 使用 `let` 来引入局部变量

`let` 的一般形式是：

```lisp
(let (variable*) body-form*)
;;举例
(let ((x 1) (y 2) z)  ;; z 是 nil
   (+ x y))
```

局部变量不会「污染」外部的变量，它们只在特定的上下文里有效，嵌套绑定同名变量，那么最内层的变量绑定将覆盖外层的绑定，所有的绑定形式都将引入词法作用域变量。

## 使用 `defparameter` 和 `defvar` 来引入全局变量

**命名约定：全局变量使用信号「*」包围起来。**，例如 `*global-counter*`。参数：变量名，初始值和文档字符串。其中文档字符串可选。`DEFPARAMETER` 总是将初始值赋给命名的变量,而 `DEFVAR` 只有当变量未定义时才这样做。

```lisp
(defvar *count* 0
  "Count of something.")
```

## 使用 `defconstant` 来引入全局常量

和 `defparameter` 类似：`(defconstant name initial-value-form [ documentation-string ])`，一些常量是预先定义的，例如 π 的值：`pi`。

## 使用 `setf` 来赋值

可以用来给全局或局部变量赋值，类似其他语言的 `=`。

```lisp
(setf x (setf y (random 10)))
```

# 注释

注释使用 `;` 来开头。

;;;; 四个分号用于文件头注释。

;;; 一个带有三个分号的注释将通常作为段落注释应用到接下来的
;;; 一大段代码上。

;; 两个分号说明该注释应用于接下来的代码上。

; 一个分号仅用于本行

另外可以使用「文档字符串」功能。

# 函数

所有 Lisp 程序的三个最基本组成部分是函数、变量和宏。要定义一个函数，使用 `defun`。`defun` 是一个宏。

```lisp
(defun name (parameter*)
  "Optional documentation string."
  body-form*)
```

## 参数

### 必要形参

  必要形式参数和预期的一样工作，按照传入的次序绑定。不能多也不能少。

  ```lisp
  (defun say-hello (name age)
    (format t "Hello ! ~s ~d." name age))
  
  (say-hello "izfsk" 10)
  ```

### 可选形参

  可选形参为调用者提供了一个默认的值，而关系它们的人可以提供一个指定的值。定义方法是在必要参数的名字之后放置符号&optional，后接可选形参的名字。默认的缺省值为 `nil`，将形参名替换成一个含有名字跟一个表达式的列表来指定该缺省值。

  ```lisp
  (defun optional-arguments (a b &optional (c 100) (d 100) (e (+ a 1)))
    (* a b c d e))

  (optional-arguments 1 2 3 4 5)
  ;; 120
  (optional-arguments 1 2 3 4)
  ;; 48
  (optional-arguments 1 2)
  ;; 40000
  ```

  可选形参表达式可以绑定第三个参数，用来判断这个参数是用户提供的还是默认的，例如 `(argument "default" argument-not-default)` 中的 `argument-not-default` 将会在用户指定值时为 `T`，否则为 `nil`。

### 剩余形参

  在符号 `&rest` 之后包括一个一揽子形参。如果一个函数带有一个 `&rest` 形参,任何满足了必要和可选形参之后的其余所有参数将被收集到一个列表里成为该 `&rest` 形参。

  ```lisp
  (defun many-arguments (&rest numbers)
    (format t "There are ~d arguments." (length numbers)))
  ```

### 关键字形参

  在任何必要的 `&optional` 和 `&rest` 形参之后可以加上符号 `&key` 以及任意数量的关键字形参标识符。

  ```lisp
  (defun foo (&rest rest &key a b c) (list rest a b c))
  (foo :a 1 :b 2 :c 3) ; ((:A 1 :B 2 :C 3) 1 2 3)
  ```

参数声明的顺序是：**首先是必要形参,其次是可选形参,再次是剩余形参,最后是关键字形参。**

正常情况下，函数的最后一行会作为返回值返回，如果需要在控制流程中返回，使用 `return-from`。