---
uuid: "3f650bd0-bdbb-4ac4-a2a6-5c62da3749dd"
title: 使用fetch下载时获取进度信息
date: 2023-03-02
category: 学习
---

一般当要在前端动态的使用 `fetch` 下载某物的时候，常规的模式是这样的：

```typescript
async function downloadFiles() {
    return fetch("Address", {
        credentials: "include",
    })
    .then((resp) => {
        return resp.blob();
    })
    .then(async (b) => {
        const a = document.createElement("a");
        a.href = URL.createObjectURL(b);
        a.setAttribute("download", "下载.zip");
        a.click();
    })
    .catch((e) => {
        console.log(e.toString());
    });
}
```

这样做有一个坏处：**不能显示进度**。返回的 blob 必须要等到下载全部完毕以后，才能有反映。对于比较大的文件，用户的观感就是页面「卡住了」，然后不停的重复点击。更好的做法是把接收的流资源分成一个个小的分块，然后按位处理它。

# 流 API

在 `fetch` 第一步返回的 `Response` 类型中包含了请求的状态，大小长度，`headers` 等等的信息，而文件的大小就可以使用 `parseInt(resp.headers.get("content-length"), 10)` 来获得。为了获得每一块的状态则需要返回一个 `ReadableStream`。

具体的来讲第二步返回的内容是这样：

```typescript
return new Response(
    new ReadableStream({
        async start(controller) {
            const reader = resp.body.getReader();
            for (;;) {
                const { done, value } = await reader.read();
                if (done) break;
                loaded += value.byteLength;
                controller.enqueue(value);
            }
            controller.close();
        },
    })
);
```

这一步返回的东西依旧是一个 `Response`，所以下一步还是需要用 `r.blob()` 来获得最终的数据。

```typescript
let total = 0, loaded = 0;

function handleDownloadAppendix() {
fetch(`Something`)
    .then((resp) => {
        switch (resp.status) {
            case 429:
            case 404:
            case 400:
                throw Error(resp.statusText);
            default:
                total = parseInt(
                    resp.headers.get("content-length"),
                    10
                );
                return new Response(
                    new ReadableStream({
                        async start(controller) {
                            const reader = resp.body.getReader();
                            for (;;) {
                                const { done, value } =  await reader.read();
                                if (done) break;
                                loaded += value.byteLength;
                                promptText = `下载中 ${
                                    Math.floor(loaded / total) * 100 - 1
                                } %`;
                                controller.enqueue(value);
                            }
                            controller.close();
                        },
                    })
                );
        }
    }).then(async (r) => {
        let blob = await r.blob();
        const a = document.createElement("a");
        a.href = URL.createObjectURL(blob);
        a.setAttribute("download", file.name);
        a.click();
    });
```

# 上传进度（使用 XHR ）

很遗憾 `fetch` 不支持给上传请求提供进度信息，所以不得不使用更加古典的 `xhr` 请求：

```typescript
const xhr = new XMLHttpRequest();
xhr.open("POST", `URL`, true);
xhr.withCredentials = true;
xhr.onreadystatechange = function () {
    if (xhr.readyState == 4 && xhr.status == 200) {
        // OK
    }
};

xhr.onerror = (e) => {
    // Error
};

xhr.upload.onprogress = (e) => {
    if (e.lengthComputable) {
        /*
        * 获得总大小 ： e.total
        * 获取上传了的大小 ： e.loaded
        */
        hint = `总量：${Utils.formatBytes(
            e.total
        )} 上传：${Utils.formatBytes(e.loaded)} ${(
            (e.loaded / e.total) *
            100
        )
            .toString()
            .substring(0, 4)} %`;
    }
};

xhr.send(finalForm);
```

**注意是 `xhr.upload.onprogress` 而不是 `xhr.onprogress`**

# 参考

- 可显示进度的 `Fetch` 示例：[Basic Fetch() Progress Indicator](https://fetch-progress.anthum.com/fetch-basic/)
- ReadableStream [ReadableStream]([ReadableStream - Web API 接口参考 | MDN](https://developer.mozilla.org/zh-CN/docs/Web/API/ReadableStream))
