# DragonFeast
> 小鲤鱼成龙记，大鱼吃小鱼游戏模式，使用与龙相关的元素进行设计。主角小鲤鱼（龙）在海洋、天空成长。关卡随机生成海洋生物、宝物（龙鳞、龙珠、龙角、龙吉祥物、金币）、障碍物（落石、旋涡、落雨）, 
> 小鲤鱼躲避障碍物、吃小鱼成长。当鲤鱼达到一定分数进入奖励关卡（快速成长）、成龙关卡（小鲤鱼跃龙门）。

小鲤鱼上下左右、（w、a、s、d）控制方向、跟随鼠标点击位置游进，其他随机生成。

鱼、宝物、障碍物什么时候随机生成？
- 鱼每隔10秒、少于3只时左右两边随机生成10只
- 宝物每隔26秒、分数整除66，上方掉落宝物
- 每隔15秒、随机障碍物

游戏结束：空格重玩、esc退出
详细设计请看：https://juejin.cn/post/7336887570977308711

# 游戏启动
## 安装依赖
```python
pip install -r requirements.txt
```

## 运行游戏
```python
python main.py
```

## todo list
- 血量、幸运、奖励值，数值转进度条样子
- 游戏特效优化
- Boss 模式

## 效果展示
![](https://p3-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/8f3594b3011a4961b54b15dcf1d125ac~tplv-k3u1fbpfcp-jj-mark:0:0:0:0:q75.image#?w=3024&h=1880&s=2030317&e=png&a=1&b=011421)

![](https://p3-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/f5fbccb25d8f414886d658468e9413dd~tplv-k3u1fbpfcp-jj-mark:0:0:0:0:q75.image#?w=3024&h=1880&s=5521183&e=png&a=1&b=175680)

![](https://p3-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/92f2b950b7b5493fb1f572cc5ff09cbe~tplv-k3u1fbpfcp-jj-mark:0:0:0:0:q75.image#?w=3024&h=1880&s=2210491&e=png&a=1&b=011421)

![](https://p3-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/8f52011d67914abd90521f1ac986b822~tplv-k3u1fbpfcp-jj-mark:0:0:0:0:q75.image#?w=3024&h=1880&s=2102012&e=png&a=1&b=011421)

![](https://p3-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/d910849fc9af45c7ba39a26fd9e792d2~tplv-k3u1fbpfcp-jj-mark:0:0:0:0:q75.image#?w=3024&h=1880&s=2002957&e=png&a=1&b=00131e)