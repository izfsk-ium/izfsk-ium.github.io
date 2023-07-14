---
uuid: "41a43b0c-279b-438f-9ee6-dbe98965ce46"
title: CommonLisp基础-分支和循环
date: 2023-01-19
category: 学习
---

# 分支

## `if`, `when`, 和 `cond`

`if` 的作用和效果和一般常识一致，其形式为 `(if condition then-form [else-form])`，使用 `and` `not` `or` 组合判断：

```lisp
(defun guess-name (name)
  (if (equalp name "izfsk")
      (print "Yes!")
      (print "No!")))
```

但是，`if` 只能执行一个表达式，所以如果需要组合执行很多任务，需要使用 `progn` 代码块：

```lisp
(if (is-target thing)
    (progn
        (do-something)
        (do-another thing)))
```

这个逻辑可以使用 `when` 宏重写：

```lisp
(when (is-target thing)
    (do-something)
    (do-another thing))
```

`unless` 是 `when` 的反过来版本。两者是建立在 `if` 上的宏。而 `if` 是**特殊操作符**。

## `cond`

类似于 C 中的 `switch...case...` 但是没有 `fallthrouth` 也不限制 int 类型：

```lisp
(cond
    (test-1 form*)
    ...
    ...
    (test-N form*))
```

# 循环

`lisp` 的循环可以很复杂，所有的循环操作宏都建立在底层的 `goto` 之上。

## `dolist` 和 `dotimes`

- `dotimes` 类似 `for (int i=0;i<100;i++)` 这样：

    ```lisp
    (defun multiples-of-3-or-5 ()
    (let ((all-sum 0))
        (dotimes (i 1000)
        (if (or (= (rem i 3) 0) (= (rem i 5) 0))
            (setf all-sum (+ all-sum i))))
        (print all-sum)))
    ```

- `dolist` 则类似 `for i in elements:` 这样：
    
    ```lisp
     (dolist (x '(1 2 3)) (print x))
     ; 使用 return 中断：
     (dolist (x '(1 2 3)) (print x) (if (evenp x) (return)))
    ```

## `do`

最基本的迭代操作符是 `do`，它可以同时迭代多个值，其基本形式如下：

```lisp
(do (variable-definition*)
    (end-test-form result-form*)
    statement*)
```

这个 `do` 有些晦涩难懂，第一个 `variable-defamations` 是一个列表，内容是 `(variable  initial  update)`，`initial` 与 `update` 形式是选择性的。若 `update` 形式忽略时，每次迭代时不会更新变量。若 `initial` 形式也忽略时，变量会使用 `nil` 来初始化。,例如：

```lisp
( 
    (x 1 (incf x))  ; 初始值 1
    (y 10 (decf y)) ; 初始值 10
    (z 0 (* x y))   ; 初始值 0
    (i) ; 初始值 nil
)
```

这就定义了三个变量。接下来是 `end-test-form` 中止条件，它也许要被括号括起来，因此，一个类似这样的 c 代码：

```c
#include <stdio.h>

int func(int target){
    int sum = 0;
    for (int i=0;i<target;i++){
        sum += i;
        printf("%d\n", i);
    }
    return sum;
}
```

可以写成：

```lisp
(defun func (target)
  (do
   ;; variable-definitions
   ((i 0 (incf i))(sum 0 (+ i sum)))
   ;; end-test-form and result-form
   ((= i target) sum)
   ;; no statements
   (format t "~d" i)
   ))
```

记住 do 需要三个部分即可，**哪怕其中没有需要操作的表达式**：

```lisp
 (do () ((= (random 10) (random 10))) (print ""))
```

简单来一个鸡兔同笼：

```lisp
(defun solve ()
  (do ((chicken 1 (incf chicken))
       (rabbit 34 (decf rabbit)))
      ((= 94 (+ (* chicken 2) (* rabbit 4)))
       (list :chicken chicken :rabbit rabbit))))
```

再举一例，计算斐波纳契数列：

```lisp
(defun fib (stop)
  (do ((n 0 (+ 1 n))
       (cur 0 next)
       (next 1 (+ cur next)))
      ((= stop n) cur)
    (print cur)))
```

## `loop`

很少有人能够真的搞懂 `loop` 的全部，这玩意是属于「高阶魔法」，比如， `loop` 可以写成这样的形式：

```lisp
 (loop for i from 1 to 10 collecting i)
 (loop for x across "the quick brown fox jumps over the lazy dog" counting (find x "aeiou"))
```

`loop` 提供了诸如「`across`、 `and` 、 `below` 、 `collecting` 、 `counting` 、 `finally` 、 `for` 、 `from` 、 `summing` 、 `then`」这样的关键字，实际上是一个专门用来写循环迭代的新的语言。

> 如果你是曾经计划某天要理解 loop 怎么工作的许多 Lisp 程序员之一，有一些好消息与坏消息。好消息是你并不孤单：几乎没有人理解它。坏消息是你永远不会理解它，因为 ANSI 标准实际上并没有给出它行为的正式规范。

> 这个宏唯一的实际定义是它的实现方式，而唯一可以理解它（如果有人可以理解的话）的方法是通过实例。ANSI 标准讨论 loop 的章节大部分由例子组成[^sn1]

最基础的 `loop` 句法是 `for` 句法，示例：

- 遍历一个列表：
  
  `(loop for i in '(1 2 3 4) do (print i))`

- 遍历多个范围：

  `(loop for i from 1 to 10 for j from 1 to 10 do (print i))`

- 控制起始和更新形式：

    ```lisp
    (loop for x = 8 then (/ x 2)
        until (< x 1)
        do (princ x))
    ```

- 各种谓词：

  ```lisp
  (loop for i from 0 downto -10 collect i)
  (loop for i from 10 to 20 collect i)
  (loop for i downfrom 20 to 10 do (print i))
  (loop for x in '(1 2 3 4 5)
	while (< x 4)
	collect x)
  ```

- 列表的过滤：

  ```lisp
  (loop for i in (list 10 20 30 40) by #'cddr collect i) -> (10 30)
  (loop for x on (list 10 20 30) collect x) -> ((10 20 30) (20 30) (30))
  (loop for x on (list 10 20 30 40) by #'cddr collect x) -> ((10 20 30 40) (30 40))
  ```

- 解构：

  ```lisp
    (loop for (a nil) in '((1 2) (3 4) (5 6)) collect a) →(1 3 5)
    (loop for (a b) in '((1 2) (3 4) (5 6)) do (format t "a: ~a; b: ~a~%" a b))
  ```

- 条件执行：

  ```lisp
  (loop for i from 1 to 10 do (when (evenp i) (print i)))
  ```

学 `loop` 要多用它（

[^sn1]:
  这段评价的来源是 《ANSI Common Lisp 中文版》 第十四章：进阶议题