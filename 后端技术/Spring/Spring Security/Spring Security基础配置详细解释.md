[[后端]] [[Spring Security]]
# Spring Security基础配置详细解释

## 一、配置Spring Security

Spring Security的配置文件中没有什么可以配置的内容，即`SecurityProperties`类中定义的。我们核心关注的是Spring Security的`SecurityFilterChain`的配置。

**配置方法**：在Spring Security 6.x版本后我们需要在容器中放入一个`SecurityFilterChain` Bean，并且通过一个叫做`HttpSecurity`的构建器来构建。并且在6.1以后，推荐使用函数式编程的方式进行配置，在Kotlin中类似于DSL的方式进行配置。

## 二、`HttpSecurity`配置

### 2.1 `authorizeHttpRequests`

`HttpSecurity`其中一项最重要的配置是授权各种HTTP Request资源，也就配置哪些URL请求可以被如何访问。

两点核心：

1. 哪些请求：即对请求的匹配，采用的是`RequestMatcher`
2. 能被怎么访问，就是权限控制

> ❕吐槽下，这里的配置完全无法对源代码进行分析，这里的`HttpSecurity`构建器实现及其复杂。

### 2.1.1 请求匹配（Request Match）

请求可以如下匹配：

1. 所有方法的某个路径或者多个路径
2. 某个方法的某个路径或者多个路径
3. 某个方法下的所有路径
4. 自定义的若干`RequestMatcher`

上述说的路径可以带有通配符，这里稍微提下路径匹配有两种模式：

- Spring MVC的路径匹配模式
- Ant风格的路径匹配模式

这里的规则其实挺复杂的，但是现如今不是特别在乎了，因为URL的设计通常比较有风格，因此不会使用到比较复杂的URL Pattern。

### 2.1.2 授权（Authorization）

在我们日常的软件开发中，会有以下几个场景：

1. 某个接口允许所有的请求者都可以访问：`permitAll()`
2. 某个接口不允许任何请求者访问：`denyAll`
3. 某个接口允许含有特定角色的用户访问：`hasRole("USER")`或者`hasAnyRole("ADMIN", "USER")`
4. 匿名访问：`anonymous()`
5. 某个接口必须用户登录后才能访问：`authenticated()`
6. 某个接口必须拥有某个权限的用户才能访问：`hasAuthority("read")`

这里有个小问题已经要注意，那就是**角色（Role）**和**权限（Authority）**的区别，在Spring Security中，角色必须要以**`ROLE_`**开头。

另外就是`permitAll`和`anonymous`绝对是不一样的，如果你使用了`permitAll`，那么这个接口谁都能访问，不管你登录没有登录，但是如果你设置了`anonymous`，你登录了就不能访问了。

授权配置可以反复调用，通常在最后使用：

```java
.anyRequest().authenticated()
```

将上述没有包含的接口全部要求登录后才能访问，就是保护起来。

---

> 其他的配置一方面和Spring Security的扩展原理有关，另一方面很多场景下我们已经不再使用，这里在后续进行补充。此外有很多功能在研究完源代码后更加能够理解。
