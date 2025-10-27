
## 一、环境准备
创建一个SpringBoot项目，引入
```
org.springframework.boot:spring-boot-starter-security
```
本文档的目标是理解整个Spring Security的自动配置的原理，通过理解这个自动配置过程复习和理解Spring，Web等相关知识。
## 二、自动配置过程
首先我们需要关注两个类：
- `SecurityFilterAutoConfiguration`
- `SecurityAutoConfiguration`
**问题1**：这两个配置类的先后顺序是什么？
在两个自动配置类的注解部分中因为他们都是自动配置类，因此都有`@AutoConfiguration`注解。该注解中说明了两者的顺序：
```java
@AutoConfiguration(after = SecurityAutoConfiguration.class)  
@ConditionalOnWebApplication(type = Type.SERVLET)  
@EnableConfigurationProperties(SecurityProperties.class)  
@ConditionalOnClass({ AbstractSecurityWebApplicationInitializer.class, SessionCreationPolicy.class })  
public class SecurityFilterAutoConfiguration { ... }
```
和
```java
@AutoConfiguration(before = UserDetailsServiceAutoConfiguration.class)  
@ConditionalOnClass(DefaultAuthenticationEventPublisher.class)  
@EnableConfigurationProperties(SecurityProperties.class)  
@Import({ SpringBootWebSecurityConfiguration.class, SecurityDataConfiguration.class })  
public class SecurityAutoConfiguration { ... }
```
`SecurityFilterAutoConfiguration`头上的`@AutoConfiguration(after = SecurityAutoConfiguration.class)`表明`SecurityFilterAutoConfiguration`在`SecurityAutoConfiguration`之后起作用。

### 理解`SecurityAutoConfiguration`
```java
@AutoConfiguration(before = UserDetailsServiceAutoConfiguration.class)  
@ConditionalOnClass(DefaultAuthenticationEventPublisher.class)  
@EnableConfigurationProperties(SecurityProperties.class)  
@Import({ SpringBootWebSecurityConfiguration.class, SecurityDataConfiguration.class })  
public class SecurityAutoConfiguration { ... }
```
从上往下：
1. `ConditionalOnClass`是一个条件配置注解，Spring中有非常多的类似注解，比如：
	- `@Condition`：Spring的最原始的注解，该注解就是通过一个接口实现来判断这个Bean是否要注入到容器中。
	- `@ConditionalOnClass`：要求你环境中有某个类文件，这就是为什么你引入了某个库后可以自动启用某项功能了
	- `@ConditionalOnBean`：当有某个Bean的时候才启用该配置和注入行为
	- 其他，具体地功能需要单独讨论`@Condition`注解
	该功能非常重要，在实际开发中也非常有用。
2. `@EnableConfigurationProperties`：Spring和SpringBoot中有一类设计模式就是`@EnableXxx`，比如要启用异步`@EnableAsync`，再比如定时任务`@EnableScheduling`，再比如AOP编程`@EnableAspectJAutoProxy`等等。
	这一类设计模式的工作原理是通常会结合`@Import`来批量地注册各种Bean实现的。这里通常会有一个问题就是`@Import`中可以传哪些参数和类型。
	`@EnableConfigurationProperties`就是用来启用某个属性配置类，就是你可以在`application.[yml|properties]`等中进行配置相关属性。`SecurityProperties`中就解释了为什么你启动项目的时候会生成一个随机的密码，用户名是`user`。
3. `@Import({ SpringBootWebSecurityConfiguration.class, SecurityDataConfiguration.class }) `核心就是`@Import`注解。而`SpringBootWebSecurityConfiguration`中又遇到了`@ConditionalOnWebApplication`，表明必须是一个Servlet Web项目，Spring提供了两种Web模式，分别是Servlet和Reactive。
看完了注解后，它还注入了一个Bean，条件是要有`AuthenticationEventPublisher`类文件：
```java
@Bean  
@ConditionalOnMissingBean(AuthenticationEventPublisher.class)  
public DefaultAuthenticationEventPublisher authenticationEventPublisher(ApplicationEventPublisher publisher) {  
    return new DefaultAuthenticationEventPublisher(publisher);  
}
```
这个组件用作事件发布，具体要理解Spring中的事件传播机制，从事件多播器到事件发布、事件监听。
`SecurityAutoConfiguration`实际上并没有什么特别核心的组件。
###  理解`SecurityFilterAutoConfiguration`
Spring Security的核心是一个过滤器链。我们要解决的问题有两个：
1. 这个过滤器链是什么
2. 什么时候放到容器里的
#### 什么是过滤器链
`SecurityFilterAutoConfiguration`中放入了一个Bean，叫做`securityFilterChainRegistration`，类型是`DelegatingFilterProxyRegistrationBean`，接下来就来详细研究下他是如何工作的。
首先我们拆解下这个类型名字`DelegatingFilterProxyRegistrationBean`：
- `Delegating`：委托模式。委托就是两个角色A和B，有一件事应该是A做的，但是他委托给B做了。明确两件事：谁该做；谁真的做了；我们整个Web容器中需要有一个过滤器，但是这个过滤器是归Spring管理的，那么这个委托类就是一个中间桥梁。
- `FilterProxy`：代理模式。过滤器代理
- `RegistrationBean`：注册器Bean。这个要理解工厂模式，在整个Spring的应用中，核心是一个代理工厂模式。在工厂模式中要弄明白什么是产品，怎么造出来的。Spring中的产品是一个一个的Bean，这里什么是BeanFactory什么是FactoryBean就很明白了。FactoryBean本质是一个Bean，这个Bean被造出来后用于生产其他的产品；而BeanFactory就是用来制造Bean的工厂；有一点绕！
我们打一个比方：周杰伦和他的经纪人。一个甲方要找周杰伦唱歌，那么周杰伦会**委托**自己的经济人去接洽，但真正要唱歌还得是周杰伦。周杰伦将经济人作为自己的代理来传达自己的需求。
总的来说`DelegatingFilterProxy | RegistrationBean`的重心是`RegistrationBean`，最终产出的Bean是`DelegatingFilterProxy`，所以
```java
@Override  
public DelegatingFilterProxy getFilter() {  
    return new DelegatingFilterProxy(this.targetBeanName, getWebApplicationContext()) {  
  
       @Override  
       protected void initFilterBean() throws ServletException {  
          // Don't initialize filter bean on init()  
       }  
  
    };  
}
```
扒开`RegistrationBean`研究下`DelegatingFilterProxy`。有几个角度考虑：
1. 怎么理解委托代理
2. 委托和代理有什么区别
首先委托是职责转交、代理是行为转交；再举周杰伦的例子。甲方要周杰伦唱歌，周杰伦可以将和甲方对接的职责移交给经纪人，但是不能把行为移交给经纪人，难道经纪人上台唱歌粉丝会答应吗？此外，委托是一个行为，因此这是正在进行时的动名词`Delegating`。代理是什么就是，如果周杰伦找了个替身唱歌，这就是代理。这两者能汇聚到一个个体身上。
---
对于`DelegatingFilterProxy`，职责和行为都是什么？
Tomcat Web容器和Spring Web Application Context是两个不同的容器系统，委托就是将一个容器中的委托给另一方的容器，这就是所谓职责。通俗说，Tomcat想要这个Filter要从Spring容器中获取。行为就是过滤。所以得出几个结论：
1. `DelegatingFilterProxy`必定是`Filter`，因为是代理
2. `DelegatingFilterProxy`必定在Spring容器中，所谓的委托
3. `Filter`的`doFilter`行为是`delegate`完成的
下面就是说`DelegatingFilterProxy.delegate`是什么？换句话说，就是`WebApplicationContext`中放了一个什么Bean来真正进行过滤器行为的呢？此时可能需要的就是调试了，从代码层面不太容易看得出来了。
经过版本的迭代，Spring Security在此过程中做了非常多的补偿设计，即可以看到很多CompositXxx的内部类。通过调试，我们最终要知道Spring Security的核心是过滤器链，而不是过滤器，因此有这样的一个类`FilterChainProxy`，其中有一个核心的方法就是`doFilterInternal`，可以得到最终有哪些Filter在工作。

---
首先`FilterChainProxy`是`FilterChain`的代理，里面必然有一个真正的`FilterChain`：
```java
public class FilterChainProxy extends GenericFilterBean {  
	// ...
	
	// 这就是最核心的过滤器链的数组（Spring Security允许有多个过滤器链）
    private List<SecurityFilterChain> filterChains;
    
    // ...
```
这个过滤器链上有（注意顺序）：
1. `DisableEncodeUrlFilter`
2. `WebAsyncManagerIntegrationFilter`
3. `SecurityContextHolderFilter`
4. `HeaderWriterFilter`
5. `CsrfFilter`
6. `LogoutFilter`
7. `UsernamePasswordAuthenticationFilter`
8. `DefaultResourcesFilter`
9. `DefaultLoginPageGeneratingFilter`
10. `DefaultLogoutPageGeneratingFilter`
11. `BasicAuthenticationFilter`
12. `RequestCacheAwareFilter`
13. `SecurityContextHolderAwareRequestFilter`
14. `AnonymousAuthenticationAware`
15. `ExceptionTranslationFilter`
16. `AuthorizationFilter`

其中最后两个是特殊的。以上就大概搞清楚了什么是过滤器链。

### 过滤器链怎么起作用的
过滤器链（`SecurityFilterChain`）这是Spring的东西，过滤器（`Filter`）是Java Web Servlet标准的东西，Spring的组件怎么放进到Spring容器内后，Java Web也就是Tomcat就能起作用了呢？
这个核心是`WebApplicationInitializer`（Spring的）组件做的事情。
回到自动配置：
```java
@AutoConfiguration(after = SecurityAutoConfiguration.class)  
@ConditionalOnWebApplication(type = Type.SERVLET)  
@EnableConfigurationProperties(SecurityProperties.class)  
@ConditionalOnClass({ AbstractSecurityWebApplicationInitializer.class, SessionCreationPolicy.class })  
public class SecurityFilterAutoConfiguration { ... }
```
自动配置的最后一个`@ConditionalOnClass`条件要求我们的应用里必须有一个`AbstractSecurityWebApplicationInitializer.class`的类文件，它是一个`WebApplicationInitializer`，核心方法是`onStartup`：
```java
@Override  
public final void onStartup(ServletContext servletContext) {  
    beforeSpringSecurityFilterChain(servletContext);  
    //...
    // 就是将SecurityFilterChain放到ServletContext里的 
    insertSpringSecurityFilterChain(servletContext);  
    afterSpringSecurityFilterChain(servletContext);  
}
```
注意`ServletContext`是`jakarta.servlet`下的，是Java的，不是Spring的。核心逻辑就是对这个`ServletContext`操作即可。
```java
private void registerFilter(ServletContext servletContext, boolean insertBeforeOtherFilters, String filterName,  
       Filter filter) {  
    // Dynamic就是Java规范接口用来注册Filter的
    Dynamic registration = servletContext.addFilter(filterName, filter);  
    // ...
    registration.setAsyncSupported(isAsyncSecuritySupported());  
    EnumSet<DispatcherType> dispatcherTypes = getSecurityDispatcherTypes();
    // 既然是Filter，你要告诉Web容器（Tomcat），你要过滤哪些URL，Spring默认就是/*所有的路径，因此只要你引入Spring Security，你的所有的URL都会被保护。  
    registration.addMappingForUrlPatterns(dispatcherTypes, !insertBeforeOtherFilters, "/*");  
}
```


## 三、流程解释
当我们发送`/hello`的请求时，会跳转到一个登录页面，这个流程是如何实现的？
1. 发送请求`GET /hello`：这是一个访问资源的操作，注意安全框架解决的是两个问题，认证和授权，认证就是通常口语说的登录，授权就是我经常说的用户有没有权限来做这个事情（访问对应的资源），安全框架保护的是各种Web资源，就是我们通常意义下的URL。所以`GET /hello`是对资源的访问。
2. 既然是对资源的访问，16个过滤器中自然最后一个开始起作用了，即`AuthorizationFilter`，因此我们要求研究的是下面的代码：
	```java
	@Override  
	public void doFilter(ServletRequest servletRequest, ServletResponse servletResponse, FilterChain chain)  
       throws ServletException, IOException {  
    
    HttpServletRequest request = (HttpServletRequest) servletRequest;  
    HttpServletResponse response = (HttpServletResponse) servletResponse;  
    
    if (this.observeOncePerRequest && isApplied(request)) {  
       chain.doFilter(request, response);  
       return;  
    }  
    
    if (skipDispatch(request)) {  
       chain.doFilter(request, response);  
       return;  
    }  
    
    String alreadyFilteredAttributeName = getAlreadyFilteredAttributeName();  
    request.setAttribute(alreadyFilteredAttributeName, Boolean.TRUE);  
    try {  
       AuthorizationResult result = this.authorizationManager.authorize(this::getAuthentication, request);  
       this.eventPublisher.publishAuthorizationEvent(this::getAuthentication, request, result);  
       if (result != null && !result.isGranted()) {  
          throw new AuthorizationDeniedException("Access Denied", result);  
       }  
       chain.doFilter(request, response);  
    }  
    finally {  
       request.removeAttribute(alreadyFilteredAttributeName);  
    }  
	}
	```
	粗略看来，核心就是
	```java
	AuthorizationResult result = this.authorizationManager.authorize(this::getAuthentication, request);
	```
	这里有个新的概念就是`authorizationManager`，即授权管理器。那么核心就是研究这个工作原理。
	在研究授权管理器之前，我们还有一个逻辑要说清楚。如果此时没有权限访问资源，是必要抛出异常，异常被上一个（编号15）`ExceptionTranslationFilter`捕获了，然后进行`handleSpringSecurityException(request, response, chain, securityException)`。
	这个异常过滤器（`ExceptionTranslationFilter`）要处理两种异常，看代码：
```java
private void handleSpringSecurityException(HttpServletRequest request, HttpServletResponse response,  
       FilterChain chain, RuntimeException exception) throws IOException, ServletException {  
    if (exception instanceof AuthenticationException) {  
       handleAuthenticationException(request, response, chain, (AuthenticationException) exception);  
    }  
    else if (exception instanceof AccessDeniedException) {  
       handleAccessDeniedException(request, response, chain, (AccessDeniedException) exception);  
    }  
}
```
分别是：
- `AuthenticationException`
- `AccessDeniedException`
认证和授权两种异常。这里我们显然触发了第二种异常。接下来看看怎么处理的，即`handleAccessDeniedException`方法。
你没有登录，就属于匿名登录（Anonymous Login），但是这个资源不允许你匿名登录下访问。因此要进入认证流程，我们平常接触到的认证流程有：
1. 重定向登录页
2. 返回401，直接返回
所以进入到认证流程的**认证端点（Authentication Entrypoint）**，同样这里有一个`DelegatingAuthenticationEntryPoint`，里面放了非常多的认证端点。通过`for`循环依次拿到各个认证端点，第一个满足条件后执行认证逻辑然后结束。这里默认的是`LoginUrlAuthenticationEntryPoint`认证端点，因此我们看到了跳转到了登录页。
这其实是Spring Security配置的结果，具体在`SpringSecurityAutoConfiguration`中有：
```java
@Import({ SpringBootWebSecurityConfiguration.class, SecurityDataConfiguration.class })
```
其中`SpringBootWebSecurityConfiguration`预定义了一些行为：
```java
@Configuration(proxyBeanMethods = false)  
@ConditionalOnWebApplication(type = Type.SERVLET)  
class SpringBootWebSecurityConfiguration {  
  
    @Configuration(proxyBeanMethods = false)  
    @ConditionalOnDefaultWebSecurity  
    static class SecurityFilterChainConfiguration {  
  
       @Bean  
       @Order(SecurityProperties.BASIC_AUTH_ORDER)  
       SecurityFilterChain defaultSecurityFilterChain(HttpSecurity http) throws Exception {  
          http.authorizeHttpRequests((requests) -> requests.anyRequest().authenticated());  
          http.formLogin(withDefaults());  
          http.httpBasic(withDefaults());  
          return http.build();  
       }  
  
    }  
  
    @Configuration(proxyBeanMethods = false)  
    @ConditionalOnMissingBean(name = BeanIds.SPRING_SECURITY_FILTER_CHAIN)  
    @ConditionalOnClass(EnableWebSecurity.class)  
    @EnableWebSecurity  
    static class WebSecurityEnablerConfiguration {  
  
    }  
  
}
```
这个说了以下几件事：
1. 要在`Servlet`环境下运行
2. 放了一个配置类`SecurityFilterChainConfiguration`，里面干的事情就是刚才跳转到登录页面的事情，比如保护所有的URL资源，支持Basic Login和表单登录
3. `@ConditionalOnDefaultWebSecurity`又来了个条件，这是个什么条件呢？根据代码，他的意思是，你自己如果没有放`SecurityFilterChain`，就使用这个配置，如果你自己放了一个`SecurityFilterChain`那么这个配置就失效了，也就是不会自动跳转到登录页了。换句话说，我们想要接管Spring Security，就是自己在容器里放置一个`SecurityFilterChain`
4. 还有一个注解`@EnableWebSecurity`：写了就是手动挡，完全接管Spring Security，没写就是自动挡，Spring Security给出了一些自动的配置。类似于`@EnableWebMvc`之类的注解。
最佳实践就是你在容器里放一个`SecurityFilterChain`，然后通过`HttpSecurity`来构建。

到此整个Spring Security的Hello World中做的事情已经讲解清楚了。进一步地事情有：
1. 如何配置
2. 认证管理器、授权管理器如何工作和扩展