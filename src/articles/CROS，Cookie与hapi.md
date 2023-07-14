---
uuid: "86894309-f881-4d14-b82f-6f3e755f2866"
title: CROS，Cookie与hapi
date: 2023-02-07
category: 技术
---

最近做项目，用到了 [hapi.js](https://hapi.dev/tutorials/gettingstarted/?lang=zh_CN) 作为后端，但前端是放在不同域名的静态页面，于是喜闻乐见的遇到了无数 CROS 问题。虽然以前也遇到过，并且用各种瞎猫碰到死耗子的方法绕了过去，但没有真的留意过，直到这次需要大规模用到 CROS 请求，还要跨域传送 Cookie，这才仔细学了一下。

CROS，全称是 Cross-Origin Resource Sharing，跨源资源共享。就是说，一个网站上的脚本要访问不在同一个域名的资源。主要的 CROS 请求来源有 XHR 请求， `fetch` 调用以及字体文件。

CROS 有两种，一种是「简单请求」，一种是「复杂请求」。简单请求，简单的来讲就是请求方法是 `get`，`head`，`post`，并且请求的 `header` 里面没有奇奇怪怪的自定义数据，里面的标头只能是[这里提到的](https://fetch.spec.whatwg.org/#cors-safelisted-request-header)。第二种是「复杂请求」，它需要「预检」。也就是对这个资源发送一个 `options` 请求，所以在 F12 工具里面能看到两个请求。

# 简单请求

简单请求中，浏览器会给目标服务器添加标头 `Origin` 来表明来源，目标服务器必须要有一个 `Access-Control-Allow-Origin` 标头，表示允许请求，不然请求的资源会被浏览器拦截。**这个拦截在 js 层面是无法检测的**，但会在浏览器 Console 中显示出来。具体的显示是：

```
Access to fetch at '...' from origin '...' has been blocked by CORS policy: 
    No 'Access-Control-Allow-Origin' header is present on the requested resource.
    If an opaque response serves your needs, 
    set the request's mode to 'no-cors' to fetch the resource with CORS disabled.
```

作为服务器端，必须在返回的头中带有 `Access-Control-Allow-Origin` 字段。如果是公共的 API 和资源，直接设置为 「*」即可，否则需要添加对应的调用方地址。

举例来讲，对于一个这样的请求：

```js
fetch('http://target.api/api')
```

对应的 hapi 路由应该这样写：

```js
server.route({
    method: "GET",
    path: "/api",
    handler: async (req, h) => {
        return h.response("Something something").header('Access-Control-Allow-Origin','*');;
    }
});
```

或者这样：

```js
server.route({
    method: "GET",
    path: "/api",
    options: {
        cors: {
            preflightStatusCode: 200,
            origin: CONFIGURE.environment.frontend_location,
        }
    },
})
```

这样就可以了。

# 复杂请求

复杂请求必须首先使用 `OPTIONS` 方法发起一个预检请求到服务器，以获知服务器是否允许该实际请求。在开发人员工具的「网络」中会显示其 Method 是 `OPTIONS`，之后才是真正的请求，显示为 `XXX + Preflight`。其中 `XXX` 是请求的方法。

对于 Preflight 请求，需要两个字段：`Access-Control-Request-Method` 和 `Access-Control-Request-Headers`。前者是实际请求的方法，后者是实际请求所携带的额外头部。

对于服务器相应的 Preflight 请求，有四个额外字段：`Access-Control-Allow-Origin`，`Access-Control-Allow-Methods`，`Access-Control-Allow-Headers`，`Access-Control-Max-Age`。分别为允许的域名，允许的方法，允许的额外标头，可供缓存的时间长短（秒）。

之后进行实际请求，其标头和一个简单的 CROS 请求一样。

```js
server.route({
    method: "POST",
    path: "/api/commonUserLogin",
    options: {
        cors: {
            origin: CONFIGURE.frontend_location,    // Access-Control-Allow-Origin
            additionalHeaders: ["your-headers"],    // Access-Control-Allow-Headers
            additionalExposedHeaders: ["your-headers"],
            maxAge: 1000        // Access-Control-Max-Age
        }
    },
    handler: async (req, h) => {...}
})
```

对于浏览器的 fetch 请求，请求头会自动添加。

# 跨域 Cookie

正常情况，一个站点的 Cookie 只能一个站点使用。想要跨站点发送 Cookie 需要：

1. 在 `fetch` 的请求中设置 `credentials` 为 `"include"`;
2. 服务器的相应中需要有 `Access-Control-Allow-Credentials: true` 标头;
3. 当响应的是附带身份凭证的请求时，服务端必须明确 `Access-Control-Allow-Origin` 和 `Access-Control-Allow-Headers` 的值，而不能使用通配符。

对于服务器，首先需要设置好 Cookie，hapi 中的 Cookie 叫做 `state`：

```js
Server.state('something', {
  ttl: 1000 * 60 * 60 * 60 * 60,
  isSecure: true,
  isHttpOnly: true,
  isSameSite: 'None',
})
```

对应 router 的 options ：

```js
options: {
   cors: {
       origin: CONFIGURE.frontend_location,
       additionalHeaders: ["your-headers"], 
       additionalExposedHeaders:  ["your-headers"], 
       credentials: true,
       maxAge:100
   }
},
```

设置 Cookie 则是：

```typescript
return h.response("Ok")
    .code(200)
    .state('something',
        jwt.sign("Your data",
            CONFIGURE.jwt_secret, { expiresIn: '100d' }).toString())
```

# 参考

- [CROS 交互式检测和教学](https://httptoolkit.com/will-it-cors/)
- [跨源资源共享（CORS）](http://developer.mozilla.org/zh-CN/docs/web/http/cors)
- [hapi.js -- route.options.cors](https://hapi.dev/api/?v=21.1.0#-routeoptionscors)