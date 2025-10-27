---
banner: 数学/凸优化/resources/banner.png
banner-height: 330
---
[[2025]] [[9月]] [[数学]] [[凸优化]] [[凸集]]
# Chapter 2: Convex Set
## 2.1 Line & Line Segment

首先要解决的一个问题就是明确险段和直线的表示。
```tikz
\begin{document}
	\begin{tikzpicture}[domain=-5:5]
		\draw[->] (0,0) -- (0,4) node[above] {$y$};
		\draw[->] (0,0) -- (5,0) node[right] {$x$};
		\draw[dashed] (0,0) -- (5,5);
		\filldraw (1,1) circle (2pt);
		\filldraw (3,3) circle (2pt);
		\node[below=5pt] (A) at (1,1) {$x_1$};
		\node[below=5pt] (B) at (3,3) {$x_2$};
		\node[right=5pt] at (2,2) {Segemnt $S$};
		\draw[color=yellow] (1,1) -- (3,3);
		\node[above] at (5,5) {Line $L$};
	\end{tikzpicture}
\end{document}

```
在上图中，我们考虑这样的一个组合，给定一个变量$\theta$，然后作
$$
\theta x_1 + (1-\theta) x_2
$$
那么如果$\theta\in[0,1]$，则这个组合得到的一系列的点就是$x_1$到$x_2$的线段，如果$\theta\in\mathbb R$，那么这就是一条直线。以上就是在一个二维空间里的展示，那么在高维空间中，同样可以类似定义直线和线段。
## 2.2 Affine Set
*Def.* $\forall x_1,x_2\in C, \theta\in\mathbb R$，
$$
\{x|\theta x_1 +(1-\theta)x_2\}\subset C
$$
也就是说一个集合里，任意两个点连线，这条直线还在这个集合里。
1. $\mathbb R^n$是Affine Set：毋庸置疑，任意一条直线都在集合里
2. $\{\boldsymbol{0}\}$是Affine Set：首先任意取出亮点，肯定是$\boldsymbol{0}$和$\boldsymbol{0}$，那么他们两个的任意组合还在这个集合中
3. $\mathbb R^n$中的任意的“直线”和“平面”都是Affine Set
