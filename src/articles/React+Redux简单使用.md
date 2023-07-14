---
uuid: "8535e383-e302-48c1-849a-d0c4447265f4"
title: React+Redux简单使用
date: 2022-12-04
category: 学习
---

# 缘起

我需要使用到 redux，找到的教程要么是阐释 redux 设计的大道至简精深奥妙超凡脱俗出类拔萃，要么是只有方案没有解释的片段，难遂我意。所以我在自己摸索以后做一个简单记录。

# 场景

Redux 所适应的场景是需要处理很多复杂数据，并且这些数据被页面上不同的组件依赖和改变。例如，需要制作一个日历 APP ，包括一个日历，显示事件的窗格，显示这一天心情的窗格，
用户点击更改日历上的日期，另外两个窗格也需要更改内容，那么它们都依赖于一个全局的数据源，如果使用传统的方法，在各个 React 组件里面传入一个函数处理，很快就会凌乱不堪，
所以需要一个统一管理这个「全局变量」的东西，实现各个组件订阅数据，一旦改变，各个组件都能够接收到改变的功能。那就是 redux 了。

我设想的情景就是这么一个网页 App ，并且需要使用 React 实现三个组件。在改变日期时还需要从服务器动态获取数据异步加载。

# 使用

## Redux 方面

首先需要安装 redux 。使用的是 `yarn add @reduxjs/toolkit react-redux` 。react 项目直接用 `creat-vite` 来创建一个脚手架项目。

使用到 redux 的项目一般不是一个 `index.js` 就能够解决的。一般来讲需要创建几个不同的目录：

- store.js 
用来保存初始状态和整个 redux 的配置
- features 
一个目录，用来保存 app 的各个功能需要用到的数据 `Slice`。

一个 app 是复杂的，比如本文的 app 三个组件，日历组件可能需要时间，日期，这一天星期几；事件查看机需要一个事件列表；而心情窗格需要心情，额外文本等。每个部分的功能所需要的
数据某种程度上独立，但都统合在 store 里面相互影响，比如，星期几的改变会改变另外两个的内容，所以每一个组件所定义的「全局数据片段」保存在单独的 feature 文件里面。所得到的就是各自的 `features/XXXSlice.js`。

如果把redux想象成全局变量管理器，这个全局变量，也就是store需要有一个初始值，分解到每一个Slice，它们各自都需要定义自己的初始状态，才能成为整个store的初始状态。
Slice文件不仅定义的这个组件（功能片段）的数据定义和初始状态，也定义了改变状态的方法，也就是`reducer`。对于redux来讲，reducer需要是一个**纯函数**，
接收一个状态，返回一个状态。白话来讲，就是：`(state, action) => newState`，其中`state`是老的状态，`action`是这个reducer的发起者（比如点击日历日期后的事件处理函数）
发送的关于怎么改数据的action，返回一个新的状态。这个`action`有具体的格式，必须是这样的：

```typescript
actions: {
    payload: any;   // 一般是一个String, 或者可以序列化的类型
    type: string;   // 类似 'calendarSlice/changeDate' 这样的字符串
}
```

进行reduce的操作叫做`dispatch`。
幸运的是，react-redux 这个toolkit给了很多便捷的方法来创建这些东西。

一个slice（日期组件）的举例：

```typescript
import { createSlice } from '@reduxjs/toolkit'

export const calendarSlice = createSlice({
    // name是必须的，用来合成各个reducer的payload中的type
    name: "CalendarSlice",
    // 初始状态
    initialState: {
        currentDisplayDate: new Date().getTime(),
        numberOfEventsToday: 0,
        isHoliday: false
    },
    reducers: {
        // 设置日期的reducer，这里的payload是一个action类型
        setNewDate: (state, payload) => {
            state.currentDisplayDate = payload.payload
        },
        // 设置事件数量的reducer
        modifyEvents: (state, payload) => {
            if (payload.payload === 'minus') 
                    state.numberOfEventsToday -= 1;
            else    state.numberOfEventsToday += 1;
        },
        // 是否是假期，如果不需要，reducer可以不带payload
        toggleIsHoliday: (state) => {
            state.isHoliday = !state.isHoliday;
        }
    }
})

export const { setNewDate, toggleIsHoliday, modifyEvents } = calendarSlice.actions

export default calendarSlice
```

这就成功的创建的一个slice了。一般就保存为`features/calendarSlice.js`。

其他的几个组件都是类似的定义，那么最后还需要一个总的store的设置：

```typescript
import { configureStore }   from '@reduxjs/toolkit'
import EditorSlice          from './features/editorSlice'
import globalSlice          from './features/globalSlice'
import calendarSlice        from './features/calendarSlice'

export const applicationStore = configureStore({
    reducer: {
        calendarStatus: calendarSlice.reducer,
        globalStatus: globalSlice.reducer,
        editorStatus: EditorSlice.reducer,
    }
})
```

这就创建了一个全局的store，内含三个组件的Slice，共同组成一个“全局数据”。如果直接看的话，它的内容应该是这样的：

```typescript
interface applicationStore_T {
    calendarStatus: {
        currentDisplayDate: number,
        numberOfEventsToday: number,
        isHoliday: boolean
    },
    globalStatus: { /* 这个Slice的数据定义 */},
    editorStatus: { /* 这个Slice的数据定义 */}
}
```

那么比如要得到目前这一天是不是假期，就可以用`store.calendarStatus.isHoliday`来判断了。

## React方面

光有数据不行，还要能够显示和改变它们。redux的store需要一个“订阅者”来使用这些数据。也就是React组件。虽然React支持函数式和ES6 Class两种类型，但是react-redux更加偏向使用函数类型(<del>虽然我喜欢写class</del>)。

众所周知react组件需要props和state，那么在结合了redux以后，**和app整体的数据有关的，比如日历组件的日期和更改日期，就不再采用props，state了，而与app整体数据无关的，比如编辑器显示的目前输入的字符数量之类，既不需要全局数据，也不会对它产生影响，依然可以使用旧的方法处理**。

### “订阅”数据

只需要在根元素上面“订阅”一次就可以拿来使用了，redux会自动初始化各自的数据：

```typescript
import { applicationStore } from './store'
import { Provider } from 'react-redux'

ReactDOM.createRoot(root).render(
    <Provider store={applicationStore}>
        <Application />
    </Provider>
)
```

### 组件获取数据

各个组件需要自己的那一份slice，而不是把整个store的内容都拿来，这就需要对目前的store内容进行一个选择。
在react-redux中，`useSelector()`就是用来给组件自己的那一份数据的，以日历组件为例：

```typescript
import { useSelector } from 'react-redux'
import { useState } from "react";

export function PageHeader(props: any) {
    const [count, setCount] = useState(0)   // 一个和全局数据无关的state，照样使用
    const slice = useSelector((state: any) => state.calendarStatus) // 返回的就是Calendar这个组件需要的Slice内容
    ......
    return ({/* Calendar的相关jsx */})
}
```

每当store中的calendarStatus因为某种原因改变了，slice也会改变，并进行**重新渲染**，某种意义上来讲它类似一个`props`。

### 组件更改数据

一般在子组件需要更改外部数据，会在props里面设置一个状态提升的函数，当事件发生时调用它来传出去，在redux里面，一个组件要修改store的数据，需要使用dispatch的方法。`useDispatch()`相当于一个邮递员，帮助组件把信息传递给对应的`reducer`。依旧举例日历组件：

```typescript
import { useSelector, useDispatch } from 'react-redux'

export function PageHeader(props: any) {
    ......
    const dispatch = useDispatch()  // 请来邮递员先生！

    return (
        <div className="cal">
            {/* a lot of codes */}
            ......
                <div
                    className="day btn"
                    onClick={e => dispatch(setNewDate(114514))} />
            ......
        </div>
    )
}
```

在这里，使用了dispatch来调用之前`features/calendarSlice.js`预先定义的`reducer`函数，而`dispatch`的作用就是把消息包装成标准的action类型发送出去。包装出来类似这样：

```ts
{
    payload: 114514;
    type: "CalendarSlice/setNewDate";
}
```

然后再去调用`setNewDate(state, action)`，其中的state自动是原先的状态。改变之后，在通知所有的订阅者。流程就是这样。

## 异步操作和在组件外进行dispatch

### 初始化时fetch内容

没有ajax或者fetch的web是不可想象的，假如用户更改了时间，或者修改了这一天的事件，就要把数据传输回服务器或者请求过来。传输回去直接开一个fetch即可，但请求就有点麻烦，必须要考虑异步问题。

比如说，在初始化时fetch内容，这是很常见的需求，一般可以结合UI框架的`Skeleton`或者类似的组件实现一个"加载中请稍候"的功能，等到初始化完毕再显示。解决方法可以是，现在store里面保存一个全局的`isPageLoaded`，各个组件检测它，如果为真，就显示内容，否则加载中。这就涉及到在全局数据fetch完毕以后在react组件外部触发reducer。

其实是可以的，因为redux本身不依赖于任何框架。react-redux只是提供的快捷方式而已。且看dispatch的定义：

```typescript
ToolkitStore<{ /* Store的类型定义 */ }, AnyAction, [...]>.dispatch: <{
    payload: boolean;
    type: string;
}>(action: {
    payload: boolean;
    type: string;
}) => {
    payload: boolean;
    type: string;
}
```

所以，你需要生成对应的type字段。在例子中，假如这个`isPageLoaded`保存在`globalSlice`中(也就是这个Slice文件的`name`是`globalSlice`)，reducer名字是`togglePageLoaded`，那么手动触发的程式码如下：

```typescript
import { applicationStore } from './store'

applicationStore.dispatch((() => {
return {
    payload: true,
    type: "globalSlice/togglePageLoaded"
}
})())
```

### 组件内fetch内容

当用户点击一个日期后进行切换，那么另外两个组件在加载完毕数据之前应该显示一个"loading..."之类的提示，一旦加载完毕马上显示出来。

为此需要`createAsyncThunk()`这个功能。首先是在相应的Slice里面定义一个Thunk函数，且看定义：

```typescript
createAsyncThunk<any, void>(typePrefix: string, payloadCreator: AsyncThunkPayloadCreator<any, void, AsyncThunkConfig>, options?: AsyncThunkOptions<void, AsyncThunkConfig> | undefined): AsyncThunk<...>
```

三个参数 `typePrefix`，是一个string，也就是用来识别这个action的字符串。对应的就是类似`CalendarSlice/setNewDate`即action类型的`type`。`payloadCreator`是一个Promise，`options`可以省略。那么，如果要给日历组件写这个chunk，应该是这样：

```typescript
export const fetchData = createAsyncThunk('CalendarSlice/fetchData', async () => {
    const response = await fetch("/data")   // fetch函数
    return response.json();
})
```

其次是为这个slice创建额外的reducer，不同于一般的reducer函数，Promise有三个状态，`pending`,`fulfilled`,`rejected`三种情况都需要处理。react-redux为我们提供了`ActionReducerMapBuilder`来处理这个情况。在原本的`features/calendarSlice.js`中修改：

```typescript
export const calendarSlice = createSlice({
    name: "CalendarSlice",
    initialState: {...},
    reducers: {...},    // 同上
    extraReducers(builder) {
    builder
        .addCase(fetchData.pending, (state, action) => {
            state.isLoading = true      /* 正在加载 */
        })
        .addCase(fetchData.fulfilled, (state, action) => {
            state.isLoading = false;
            state.data = action.payload;    /* 可以处理获取的数据了 */
        })
        .addCase(fetchData.rejected, (state, action) => {
            /* 处理出错逻辑 */
        })
    },
})
```

# 参见

- [Redux 官方教程](https://redux.js.org/tutorials/index "Redux Tutorials")
- [关于createAsyncThunk的另外一个教程](https://jasonwatmore.com/post/2022/06/16/react-redux-toolkit-fetch-data-in-async-action-with-createasyncthunk "React + Redux Toolkit - Fetch Data in Async Action with createAsyncThunk")