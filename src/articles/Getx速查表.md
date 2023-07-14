---
uuid: "7f58b9f5-d420-4722-8d41-6191a9453397"
title: Getx速查表
date: 2023-06-01
category: 备忘
---

## 安装

在 `pubspec.yaml` 中添加：

```dart
dependencies:
  get:
```

注意不用添加版本号。然后在文件中可以使用 `import 'package:get/get.dart';` 引入。

## 路由

所有的路由都不需要传入 `BuildContext`。

### 简单路由

- 导航到新的页面：`Get.to(()=>NextScreen());`
- 返回到之前的页面，也包括关闭 `snackbars`，`dialogs` 和 `bottomsheets` 等元素：`Get.back();`
- 导航到新的页面，不能返回：`Get.off(()=>NextScreen());`
- 导航到新的页面，把之前的东西统统关掉：`Get.offAll(()=>NextScreen());`

路由也可以传输数据，像这样获取页面数据：

```dart
final data = await Get.to(Payment());
```

对应的页面这样返回数据：

```dart
Get.back(result: 'success');
```

### 命名路由

首先需要定义路由：

```dart
GetMaterialApp(
      initialRoute: '/',
      unknownRoute: GetPage(name: '/notfound', page: () => UnknownRoutePage()),     // 错误路由
      getPages: [
        GetPage(name: '/', page: () => MyHomePage()),
        GetPage(name: '/second', page: () => Second()),
        GetPage(
            name: '/profile/:user',     // :user 是一个参数
            page: () => UserProfile(),
        ),
        GetPage(
          name: '/third',
          page: () => Third(),
          transition: Transition.zoom  // 动画效果
        ),
      ],
    )
```

使用方法还是类似无名路由：

```dart
Get.toNamed("/NextScreen", arguments: 'Something...');
Get.offNamed("/NextScreen");
Get.offAllNamed("/NextScreen");
```

可以看到给路由加参数也是可以的，在对应的页面的控制器或类中使用 `Get.arguments` 就可以获取到。除此以外还可以使用类似 Web URL 的方法传递 `arguments`:`Get.toNamed("/profile/34954?flag=true&country=italy");`。获取它们是这样：

```dart
print(Get.parameters['user']);
print(Get.parameters['flag']);
print(Get.parameters['country']);
```

还可以给路由加上 `Middleware`:

```dart
GetMaterialApp(
  routingCallback: (routing) {
    if(routing.current == '/second'){
      openAds();
    }
  }
)
```

### Snakebar 和 Dialog

```dart
Get.snackbar(
  "Hey i'm a Get SnackBar!", // title
  "SnackBar without context, without boilerplate, without Scaffold!", // message
  icon: Icon(Icons.alarm),
  shouldIconPulse: true,
  onTap:(){},
  barBlur: 20,
  isDismissible: true,
  duration: Duration(seconds: 3),
);

Get.defaultDialog(
  onConfirm: () => print("Ok"),
  middleText: "Dialog made in 3 lines of code"
);

```

无需 `BuildContext`。

### BottomSheet

BottomSheet 就是在页面底部从下往上弹出的那个菜单一样的东西：

```dart
Get.bottomSheet(
  Container(
    child: Wrap(
      children: <Widget>[
        ListTile(
          leading: Icon(Icons.music_note),
          title: Text('Music'),
          onTap: () {}
        ),
        ListTile(
          leading: Icon(Icons.videocam),
          title: Text('Video'),
          onTap: () {},
        ),
      ],
    ),
  )
);
```

## 状态管理

有了 `Getx`，再也不需要使用 `StatefulWidget` 了。

### 常用模式

一个通常的模式是这样的：一个页面对应一个控制器(`controller`)，这个控制器扩展了 `GetxController`。在一个 Controller 类中，一个 `Obs` 会**自动更新**订阅了它的组建，其他不是 `Obs` 的数据必须在修改它们的方法中使用 `update();` 才行。

对于响应式的变量，有特殊的类型来处理：

```dart
final name = RxString('');
final isLogged = RxBool(false);
final count = RxInt(0);
final balance = RxDouble(0.0);
final items = RxList<String>([]);
final myMap = RxMap<String, int>({});
```

当然，要获取它们的实际值就需要 `xxx.value` 了。

如何使用：

```dart
GetX<Controller>(
  builder: (controller) {
    print("count 2 rebuild");
    return Text('${controller.count2.value}');
  },
),
```

注意事项：如果要在控制器里面初始化什么东西（网络连接，文件，数据库），**不要使用类初始化函数**，而是使用 `onInit()`。同样的，使用 `onClose()` 而不是 `dispose`。  

### Workers

当特定事件在某个值上发生时的 callback：

```dart
/// Called every time `count1` changes.
ever(count1, (_) => print("$_ has been changed"));

/// Called only first time the variable $_ is changed
once(count1, (_) => print("$_ was changed once"));

/// Anti DDos - Called every time the user stops typing for 1 second, for example.
debounce(count1, (_) => print("debouce$_"), time: Duration(seconds: 1));

/// Ignore all changes within 1 second.
interval(count1, (_) => print("interval $_"), time: Duration(seconds: 1));
```

### StateMixin

```dart
class DataType {
  final String name;
  final int age;

  DataType(this.name, this.age);
}

class Repo {
  Future getData() async {
    sleep(Duration(seconds: 1));
    return "hello!";
  }
}

class MyController extends GetxController with StateMixin<DataType> {
  final Repo repository;

  MyController(this.repository);

  @override
  void onInit() {
    repository.getData().then((resp) {
      change(DataType("name", 10), status: RxStatus.success());
    }, onError: (err) {
      change(
        null,
        status: RxStatus.error('Error get data'),
      );
      super.onInit();
    });
  }
}

class MyHomePage extends GetView<MyController> {
  const MyHomePage({super.key});

  @override
  Widget build(BuildContext context) {
    Get.put(MyController(Repo()));
    return Scaffold(
      appBar: AppBar(),
      body: controller.obx(
        (state) => Text(state!.name),
        onLoading: const CircularProgressIndicator(),
        onError: (error) => Text(error.toString()),
      ),
    );
  }
}
```

## 依赖管理

### 何时初始化

```dart
class Controller extends GetxController {
  static Controller get to => Get.find();
    [...]
}
// on you view:
GetBuilder<Controller>(
  init: Controller(), // use it only first time on each controller
  builder: (_) => Text(
    '${Controller.to.counter}', //here
  )
),
```

### 细节  

最常见的插入依赖关系的方式：`Get.put` 和 `Get.lazyPut`

```dart
Get.put<SomeClass>(SomeClass());
Get.put<LoginController>(LoginController(), permanent: true);
Get.put<ListItemController>(ListItemController, tag: "some unique string");
Get.lazyPut<Controller>( () => Controller() )
```

文档有中文版本。（[依赖管理](https://github.com/jonataslaw/getx/blob/master/documentation/zh_CN/dependency_management.md)）

### Bindings  

啥时候去 Put 你的 Controller 总是个问题，Bindings 就是解决这个问题的，它将路由、状态管理器和依赖管理器完全集成。首先创建 binding 类：

```dart
class HomeBinding implements Bindings {
  @override
  void dependencies() {
    Get.lazyPut<HomeController>(() => HomeController());
    Get.put<Service>(()=> Api());
  }
}
```

然后在路由中使用它们：

```dart
GetPage(
    name: '/',
    page: () => HomeView(),
    binding: HomeBinding(),
),

Get.to(DetailsView(), binding: DetailsBinding())
```

## 参考

- [官方中文文档](https://github.com/jonataslaw/getx/tree/master/documentation/zh_CN)
- [GetX Docs](https://chornthorn.github.io/getx-docs/)
- [GetX Handbook](https://tabpole.github.io/getx/)
