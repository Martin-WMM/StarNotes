[[后端]] [[Spring Security]] [[Java]] [[Java Web]]
# Spring Security授权原理

## 一、授权简介

授权（Authorization）是对资源进行鉴权的过程。在Spring Security中，保护的资源有：

- Web资源URL
- 某些方法或者函数
## 二、URL授权
对URL授权方式是通过配置`SecurityFilterChain`实现。
## 三、方法授权

方法授权首先需要开启配置：

```java
@EnableMethodSecurity(securedEnabled = true, prePostEnabled = true, jsr250Enabled = true)
```

这里有三个核心的参数配置：

- `securedEnabled`表示是否启用`@Secured`注解
- `prePostEnabled`表示`@PreAuthorize`和`@PostAuthorize`两个注解
- `jsr250Enabled`表示是否启用JSR-250规范的注解，比如`@PermitAll`，`@DenyAll`，`@RolesAllowed`

## 四、自定义授权逻辑
## 五、授权原理

