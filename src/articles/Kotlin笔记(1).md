---
uuid: "49154284-8978-4e9b-81d9-e5cfa757dcea"
title: Kotlin笔记(1)
date: 2022-11-24
category: 学习
---
# 开发环境

## IDE

- IDEA ([JetBrains IDEA 下载]( https://www.jetbrains.com/idea/download))
- VS Code ([VSCode](https://code.visualstudio.com/)) + Kotlin 插件([插件](https://marketplace.visualstudio.com/items?itemName=fwcd.kotlin))

## REPL

打开`  Tools → Kotlin → Kotlin REPL`使用REPL

# 数据

## val

`val`是不可变类型（只读变量）。运行时指定，不可修改。

```kotlin
val x:String = "Hello!"
val y = "Hello!"
val z:String = readLine()
```

## var

`var`是可变变量类型。

```kotlin
var x;
x = 1024
```

## const val

`const val`是**编译时常量**，必须在编译时是已知的基本数据类型。必须放在最外层。

```kotlin
const val x="sss"
```

## 基本数据类型

|类型|描述|举例|
|---|---|---|
|String|字符串|"Hello!\n"|
|char|单个字符|'x'|
|Boolean|`true/false`|true|
|Int|整数|114514|
|Long|长整数|999999999|
|Byte|8位整数|126|
|Short|16位整数|32767|
|Float|32位浮点数|3.488|
|Double|浮点数|1919.810|
|List|列表|略|
|Set|集合|略|
|Map|散列表/字典|略|

### 字符串

1. 字符串截取：使用`substring`
2. 字符串分割：使用`split`
3. 字符串替换字符：使用`replace+lambda`:

    ```Kotlin
    fun toDragonSpeak(phrase: String) =
        phrase.replace(Regex("[aeiou]")) {
            when (it.value) {
                "a" -> "4"
                "e" -> "3"
                "i" -> "1"
                "o" -> "0"
                "u" -> "|_|"
                else -> it.value
            }
        }
    ```

4. 字符串比较：可以直接使用`==`(与Java不同)：

    ```Kotlin
    val phrase = if (name == "Dragon's Breath") {
        "Madrigal exclaims ${toDragonSpeak("Ah, delicious $name!")}"
    } else {
        "Madrigal says: Thanks for the $name."
    }
    ```
    
5. 遍历字符串： 一个字符串就是一个不可变的字符列表，所以能用在list上的都能用在字符串上。

### 数字

#### 字符串转数字

- toFloat
- toDouble
- toDoubleOrNull
- toIntOrNull
- toLong
- toBigDecimal

等。每一种都有`toXXXOrNull`版本，返回可空类型，便于使用`?:`运算符避免抓异常。

#### 数字格式化

按照C语言的格式化字符串规则展开即可。

#### 位运算

- `Integer.toBinaryString()`直接把数字转换为二进制
- `shl`:按位左移
- `shr`:按位右移
- `inv`:按位取反
- `xor`:按位异或

### List列表

列表是kotlin的基本类型。分为两种，可变列表`mutableList`和不可变列表`List`。

#### 创建

```Kotlin
val patronList: List<String> = listOf("Eli", "Mordoc", "Sophie")
val patronMutableList = mutableListOf<String>("Eli", "Mordoc", "Sophie")

val tmp= mutableListOf<String>()
val lines: List<String>? = File("file").takeIf { it.canRead() }?.readLines()
```

#### 获取与遍历

##### 获取

1. `get()` : 可能抛出异常。
2. `getOrNull()` : 便于使用`?:`处理null值
3. `getOrElse()` : 使用lambda获取默认值，例如`tmp.getOrElse(15) { "ss" }`

##### 遍历

1. `forEachIndexed(action: (index: Int, T) -> Unit)` : 带索引的遍历
2. `forEach(action: (T) -> Unit)` : 没有索引的遍历

都是携带一个lambda函数。**注意要使用`run`来执行lambda!!!**

#### 修改

只有mutableListOf才能修改。有add和addAll两个方法。

#### 解构

List 集合支持以解构的方式获取其中的元素。
`val (type, name, price) = TargetString.split(',')`

split 函数返回集合数据后,集合里的前三个元素就分别赋值给了 type、 name 和 price 这
三个字符串变量。通过使用_符号过滤不想要的元素。

### Set集合

Set是会自动去重的集合类型。和List类似，有可变与不可变两种。Set和List可以互相转换。使用`toList`和`toSet`即可。
Set的创建方法如下：

```kotlin
val planets = setOf("Mercury", "Venus", "Earth")
val uniquePatrons = mutableSetOf<String>()
```

类似的，使用`add`,`addAll`,`remove`,`removeAll`,`clear`等函数处理**可变**的Set。

对于线性的容器，可以使用`uniquePatrons.shuffled().first()`这种方法方便快捷的取得随机元素。

### Map散列表

Map即类似于python中的dict或C++中的map。现代的常用程式语言没有在语言内置散列表的功能是说不过去的。Kotlin的Map用来存放
一组元素,默认只读。创建方法如下：

```kotlin
val the_map = mapOf("Eli" to 10.5, "Mordoc" to 8.0, "Sophie" to 5.5)
the_map += "Sophie" to 6.0
```

其中`to`是个省略了点号和参数圆括号的特殊函数，把它两边的元素转换为一个`Pair`（`Pair("Mordoc", 8.00)`）。
读取方法是简单的方括号，也可以使用`getOrElse()`,`getOrDefault()`来防止null异常。注意`getOrElse()`使用匿名函数。
一般情况下，需要使用类似这样的代码来检查和添加元素：

```python
x = dict()
try:
    result = x['nohere']
except Exception as e:
    x['nohere'] = 'default'
    result = 'default'
```

但在kotlin中只需要一个`getOrPut()`函数即可，很方便。

**其实，有IDEA这样的IDE并不需要记住这些函数的原型，一般只需要猜即可。放入操作大凡是put，取出则大凡是get。**

## 控制流

if,else,while,for等等控制流不必多言。

导入的话，可以类似python用`import XXX as XXX`了。

`import com.a.b.c.d as myHappyFunc`

由于Kotlin比较灵活的语法，可以写的更舒服。有一种TMTOWTDI的意思了。

(话说回来我觉得Python的不好之处就在于一些全局函数，比如不得不使用`map(),str()`之类的**函数**，而不是在各种对象上调用`xxx.map().str()`的方法。
即使对象有内置的`__str__()`方法，而且Python的lambda比较弱)

## 函数

### 匿名函数

<del>约翰·麦卡锡和阿隆佐·丘奇们的英灵可以告慰啦！现代语言几乎都支持匿名函数和函数式写法，哪怕
大家并不知道啥alpha转换，beta规约（</del>

再加上几个标准函数，真的可以做到函数式一把梭。（apply, let, with, run, also, takeIf, takeUnless)

稍举一例：
```kotlin
val fileContents = File("myfile.txt").takeIf { it.canRead() && it.canWrite() }?.readText()
```

### 扩展函数

扩展可以在不直接修改类定义的情况下增加类功能。javascript可以使用这样的方法给已有的类添加方法：

```js
String.prototype.ddd = () => { console.log('Hello!') }
"Hello!".ddd()
```

```kotlin
fun String.myFunc(amount: Int = 1) = this + "!".repeat(amount)
fun main(args: Array<String>) {
    println("Hello!".myFunc())
}

fun Any.easyPrint() = println(this) // 超类亦可
fun main(args: Array<String>) {
    42.easyPrint()
}
```

## null安全

在类型后面加个问号表示可空类型。例如`String?`。

使用`?.`（安全调用运算符）来防止在null上调用函数出现`NPE`，可以使用`!!.`来强制调用，跳过检查。
使用`?:`来实现类似Javascript中`undefined || "default"`的取值。