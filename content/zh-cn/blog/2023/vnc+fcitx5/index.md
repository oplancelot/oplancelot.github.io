---
title: The VNC remote login cannot enter Chinese characters
weight: 3
date: 2023-08-02
description:  主要解决了VNC连接时中文输入的问题
# draft: true
categories: [ Linux]
tags: [fcitx5,tigervnc,xfce,vnc,debian11]
---

前段时间我将工作机从win10迁移到了debian11,刚安装的是server版，后面加上了xfce桌面环境。经过一段时间的优化美化，用起来非常的顺手。

好景不长，这台debian11要放到其他地方，我又只能使用之前的win10了。想了想干脆使用VNC远程桌面吧，用起来才发现中文输入是个问题，调试了快两天才解决。记录下过程，或许有人也有一样的情况。

# 环境配置

+ OS: `Linux lance-workstation 5.10.0-23-rt-amd64 #1 SMP PREEMPT_RT Debian 5.10.179-3 (2023-07-27) x86_64 GNU/Linux`
+ xfce:`4.16`
+ vnc :`Xvnc TigerVNC 1.11.0 - built 2022-01-26 17:59`
+  Fcitx 版本: `5.0.5`


{{< imgproc workstation Fill "600x300" >}}
workstation{{< /imgproc >}}



<details><summary>详细配置信息</summary>

```

$  fcitx5-diagnose
# 系统信息:
1.  `uname -a`:

        Linux lance-workstation 5.10.0-23-rt-amd64 #1 SMP PREEMPT_RT Debian 5.10.179-3 (2023-07-27) x86_64 GNU/Linux

2.  `lsb_release -a`:

        No LSB modules are available.
        Distributor ID:	Debian
        Description:	Debian GNU/Linux 11 (bullseye)
        Release:	11
        Codename:	bullseye

3.  `lsb_release -d`:

        Description:	Debian GNU/Linux 11 (bullseye)

4.  `/etc/lsb-release`:

        DISTRIB_ID=Kylin
        DISTRIB_RELEASE=V10
        DISTRIB_CODENAME=kylin
        DISTRIB_DESCRIPTION="Kylin V10 SP1"
        DISTRIB_KYLIN_RELEASE=V10
        DISTRIB_VERSION_TYPE=enterprise
        DISTRIB_VERSION_MODE=normal

5.  `/etc/os-release`:

        PRETTY_NAME="Debian GNU/Linux 11 (bullseye)"
        NAME="Debian GNU/Linux"
        VERSION_ID="11"
        VERSION="11 (bullseye)"
        VERSION_CODENAME=bullseye
        ID=debian
        HOME_URL="https://www.debian.org/"
        SUPPORT_URL="https://www.debian.org/support"
        BUG_REPORT_URL="https://bugs.debian.org/"

6.  桌面环境：

    桌面环境为 `xfce`。

7.  Bash 版本：

        BASH_VERSION='5.1.4(1)-release'

# 环境：
1.  DISPLAY:

        DISPLAY=':1.0'

2.  键盘布局：

    1.  `setxkbmap`:

            xkb_keymap {
            	xkb_keycodes  { include "evdev+aliases(qwerty)"	};
            	xkb_types     { include "complete"	};
            	xkb_compat    { include "complete"	};
            	xkb_symbols   { include "pc+cn+us:2+inet(evdev)"	};
            	xkb_geometry  { include "pc(pc105)"	};
            };

    2.  `xprop`:

            _XKB_RULES_NAMES(STRING) = "evdev", "pc105", "cn,us", ",", ""

3.  Locale：

    1.  全部可用 locale：

            C
            C.UTF-8
            en_US.utf8
            ja_JP.utf8
            POSIX
            zh_CN.gb18030
            zh_CN.utf8
            zh_HK.utf8

    2.  当前 locale：

            LANG=zh_CN.UTF-8
            LANGUAGE=zh_CN:zh
            LC_CTYPE="zh_CN.UTF-8"
            LC_NUMERIC="zh_CN.UTF-8"
            LC_TIME="zh_CN.UTF-8"
            LC_COLLATE="zh_CN.UTF-8"
            LC_MONETARY="zh_CN.UTF-8"
            LC_MESSAGES="zh_CN.UTF-8"
            LC_PAPER="zh_CN.UTF-8"
            LC_NAME="zh_CN.UTF-8"
            LC_ADDRESS="zh_CN.UTF-8"
            LC_TELEPHONE="zh_CN.UTF-8"
            LC_MEASUREMENT="zh_CN.UTF-8"
            LC_IDENTIFICATION="zh_CN.UTF-8"
            LC_ALL=

4.  目录：

    1.  主目录：

            /home/lance

    2.  `${XDG_CONFIG_HOME}`:

        环境变量 `XDG_CONFIG_HOME` 没有设定。

        `XDG_CONFIG_HOME` 的当前值是 `~/.config` (`/home/lance/.config`)。

    3.  Fcitx5 设置目录：

        当前 fcitx5 设置目录是 `~/.config/fcitx5` (`/home/lance/.config/fcitx5`)。

5.  当前用户：

    脚本作为 lance (1000) 运行。

# Fcitx 状态:
1.  可执行文件：

    在 `/usr/bin/fcitx5` 找到了 fcitx5。

2.  版本：

    Fcitx 版本: `5.0.5`

3.  进程：

    找到了 2 个 fcitx5 进程：

          10553 fcitx5
          42578 fcitx5

4.  `fcitx5-remote`:

    `fcitx5-remote` 工作正常。

5.  DBus 界面：

    使用 `dbus-send` 来检查 dbus。

    DBus 名称 `org.fcitx.Fcitx5` 的所有者是 `:1.488`。

    DBus 名称 `org.fcitx.Fcitx5` 的 PID 所有者是 `42578`。

# Fcitx 配置界面：
1.  配置工具封装：

    在 `/usr/bin/fcitx5-configtool` 找到了 fcitx5-configtool。

2.  Qt 的配置界面：

    在 `/usr/bin/fcitx5-config-qt` 找到了 `fcitx5-config-qt`。

3.  KDE 的配置界面：

    **`kcmshell5` 未找到.**

# 前端设置：
## Xim:
1.  `${XMODIFIERS}`:

    **环境变量 XMODIFIERS 的值被设为了“@im=fcitx5”而不是“@im=fcitx”。请检查您是否在某个初始化文件中错误的设置了它的值。**

    **请使用您发行版提供的工具将环境变量 XMODIFIERS 设为 "@im=fcitx" 或者将 `export XMODIFIERS=@im=fcitx` 添加到您的 `~/.xprofile` 中。参见 [输入法相关的环境变量：XMODIFIERS](http://fcitx-im.org/wiki/Input_method_related_environment_variables/zh-cn#XMODIFIERS)。**

    从环境变量中获取的 Xim 服务名称为 fcitx5.

2.  根窗口上的 XIM_SERVERS：

    Xim 服务的名称与环境变量中设置的相同。

## Qt:
1.  qt4 - `${QT4_IM_MODULE}`:

    **环境变量 QT_IM_MODULE 的值被设为了“fcitx5”而不是“fcitx”。请检查您是否在某个初始化文件中错误的设置了它的值。**
    **您可能会在 qt4 程序中使用 fcitx 时遇到问题.**

    **请使用您发行版提供的工具将环境变量 QT_IM_MODULE 设为 "fcitx" 或者将 `export QT_IM_MODULE=fcitx` 添加到您的 `~/.xprofile` 中。参见 [输入法相关的环境变量：QT_IM_MODULE](http://fcitx-im.org/wiki/Input_method_related_environment_variables/zh-cn#QT_IM_MODULE)。**

2.  qt5 - `${QT_IM_MODULE}`:

    **环境变量 QT_IM_MODULE 的值被设为了“fcitx5”而不是“fcitx”。请检查您是否在某个初始化文件中错误的设置了它的值。**
    **您可能会在 qt5 程序中使用 fcitx 时遇到问题.**

    **请使用您发行版提供的工具将环境变量 QT_IM_MODULE 设为 "fcitx" 或者将 `export QT_IM_MODULE=fcitx` 添加到您的 `~/.xprofile` 中。参见 [输入法相关的环境变量：QT_IM_MODULE](http://fcitx-im.org/wiki/Input_method_related_environment_variables/zh-cn#QT_IM_MODULE)。**



3.  Qt 输入法模块文件：

    找到了 fcitx5 的 qt5 输入法模块：`/lib/x86_64-linux-gnu/qt5/plugins/platforminputcontexts/libfcitx5platforminputcontextplugin.so`。
    找到了 fcitx5 qt5 模块：`/lib/x86_64-linux-gnu/fcitx5/qt5/libfcitx-quickphrase-editor5.so`。
    **无法找到 Qt4 的 fcitx5 输入法模块。**

## Gtk:
1.  gtk - `${GTK_IM_MODULE}`:

    **环境变量 GTK_IM_MODULE 的值被设为了“fcitx5”而不是“fcitx”。请检查您是否在某个初始化文件中错误的设置了它的值。**
    **您可能会在 gtk 程序中使用 fcitx 时遇到问题.**

    **请使用您发行版提供的工具将环境变量 GTK_IM_MODULE 设为 "fcitx" 或者将 `export GTK_IM_MODULE=fcitx` 添加到您的 `~/.xprofile` 中。参见 [输入法相关的环境变量：GTK_IM_MODULE](http://fcitx-im.org/wiki/Input_method_related_environment_variables/zh-cn#GTK_IM_MODULE)。**

2.  `gtk-query-immodules`:

    1.  gtk 2:

        **无法找到 gtk 2 的 `gtk-query-immodules`。**

        **无法找到 gtk 2 的 fcitx5 输入法模块。**

    2.  gtk 3:

        **无法找到 gtk 3 的 `gtk-query-immodules`。**

        **无法找到 gtk 3 的 fcitx5 输入法模块。**

3.  Gtk 输入法模块缓存：

    1.  gtk 2:

        在 `/lib/x86_64-linux-gnu/gtk-2.0/2.10.0/immodules.cache` 找到了 gtk `2.24.33` 的输入法模块缓存。
        版本行：

            # Created by /usr/lib/x86_64-linux-gnu/libgtk2.0-0/gtk-query-immodules-2.0 from gtk+-2.24.33

        已找到 gtk `2.24.33` 的 fcitx5 输入法模块。

            "/usr/lib/x86_64-linux-gnu/gtk-2.0/2.10.0/immodules/im-fcitx5.so" 
            "fcitx" "Fcitx5 (Flexible Input Method Framework5)" "fcitx5" "/usr/locale" "ja:ko:zh:*" 
            "fcitx5" "Fcitx5 (Flexible Input Method Framework5)" "fcitx5" "/usr/locale" "ja:ko:zh:*" 

    2.  gtk 3:

        在 `/lib/x86_64-linux-gnu/gtk-3.0/3.0.0/immodules.cache` 找到了 gtk `3.24.24` 的输入法模块缓存。
        版本行：

            # Created by /usr/lib/x86_64-linux-gnu/libgtk-3-0/gtk-query-immodules-3.0 from gtk+-3.24.24

        已找到 gtk `3.24.24` 的 fcitx5 输入法模块。

            "/usr/lib/x86_64-linux-gnu/gtk-3.0/3.0.0/immodules/im-fcitx5.so" 
            "fcitx" "Fcitx5 (Flexible Input Method Framework5)" "fcitx5" "/usr/locale" "ja:ko:zh:*" 
            "fcitx5" "Fcitx5 (Flexible Input Method Framework5)" "fcitx5" "/usr/locale" "ja:ko:zh:*" 

    3.  gtk 4:

        **无法找到 gtk 4 的输入法模块缓存**

        **无法在缓存中找到 gtk 4 的 fcitx5 输入法模块。**

4.  Gtk 输入法模块文件：

    1.  gtk 2:

        找到的全部 Gtk 2 输入法模块文件均存在。

    2.  gtk 3:

        找到的全部 Gtk 3 输入法模块文件均存在。

    3.  gtk 4:

        找到的全部 Gtk 4 输入法模块文件均存在。

# 配置:
## Fcitx 插件：
1.  插件配置文件目录：

    找到了 fcitx5 的插件配置目录：`/usr/share/fcitx5/addon`。

2.  插件列表：

    1.  找到了 26 个已启用的插件：

            Simplified and Traditional Chinese Translation
            Classic User Inteface
            Clipboard
            Cloud Pinyin
            DBus
            DBus Frontend
            Emoji
            Fcitx4 Frontend
            Full width character
            IBus Frontend
            Input method selector
            Keyboard
            KDE Input Method Panel
            Status Notifier
            Notification
            Pinyin
            Extra Pinyin functionality
            Punctuation
            Quick Phrase
            Spell
            Table
            Unicode
            Wayland
            Wayland Input method frontend
            XCB
            X Input Method Frontend

    2.  找到了 0 个被禁用的插件：

3.  插件库: 

    所有插件所需的库都被找到。

4.  用户界面：

    找到了 2 个已启用的用户界面插件：

        Classic User Inteface
        KDE Input Method Panel

# 日志：
1.  `date`:

        2023年 08月 02日 星期三 16:12:29 CST

2.  `/home/lance/.config/fcitx5/crash.log`:

    `/crash.log` 未找到.


```
</details>

# 安装tigervnc

为什么不使用`tightvnc`呢？简单点说是`tightvnc`和`fcitx5`兼容性有问题。

输入`fcitx5 -r` ，可以看到关键报错

```bash
W2023-07-31 23:25:39.538681 xcbeventreader.cpp:39] XCB connection ":1.0" got error: 2
I2023-07-31 23:25:39.538988 inputcontextmanager.cpp:318] All display connections are gone, exit now.
I2023-07-31 23:25:39.539315 xcbmodule.cpp:58] Disconnected from X11 Display :1.0
```

现象可参考[esxi+vnc+xfce环境下fcitx5不自动启动，而手动启动报错无法启动](https://github.com/fcitx/fcitx5/issues/559)



`tigervnc`才是解决问题的关键
/ TigerVNC was originally based on the (never-released) VNC 4 branch of TightVNC.TigerVNC was originally based on the (never-released) VNC 4 branch of TightVNC.


## install 

```
sudo apt install tigervnc-standalone-server tigervnc-common 
```

## config

使用当前用户`lance`设置个远程登录需要的密码

```bash
$ tigervncpasswd
Password:
Verify:
Would you like to enter a view-only password (y/n)? n


```


`tigervnc`的配置文件放在`/etc/tigervnc`
``````
├── openssl.cnf
├── openssl-ecparams.pem
├── vncserver-config-defaults
├── vncserver-config-mandatory
└── vncserver.users
``````
这里只贴出配置选项，其他的请参考原始文件。

vncserver.users
```text
#lance 是 用户名
:1=lance
```

vncserver-config-mandatory
```text
#共享剪贴板方便远程复制
 Default: $AlwaysShared = "yes";
```

vncserver-config-defaults
```text
 Default: $vncUserDir = "$ENV{HOME}/.vnc";
 Default: $vncPasswdFile = "$vncUserDir/passwd";
 Default: $vncStartup = "/etc/X11/Xtigervnc-session";
 Default: $session = xfce;
 Default: $geometry = "1920x1080";
 Default: $depth = "24";

```

还有个关键配置
`/home/lance/.vnc/xstartup`

```text
#!/bin/bash
export INPUT_METHOD=fcitx5
export GTK_IM_MODULE=fcitx5
export QT_IM_MODULE=fcitx5
export XMODIFIERS=@im=fcitx5
xrdb $HOME/.Xresources
startxfce4
```
注意两点
+ `startxfce4` 后面没有 `&`
+ 变量一定要写在这个文件。解释如下
```text
# $vncStartup points to a script that will be started at the very beginning
# when neither $vncUserDir/Xtigervnc-session nor $vncUserDir/xstartup is present.
# If $vncUserDir/Xtigervnc-session is present, it will be used. Otherwise, we try
# $vncUserDir/xstartup. If this is also absent, then we use the script given by
# $vncStartup. If $vncStartup is specified in $vncUserDir/tigervnc.conf, then this
# script is used unconditionally. That is without checking for the presence of
# $vncUserDir/Xtigervnc-session or $vncUserDir/xstartup.

```
写在`～/.profile`，`～/.xprofile`,`~/.pam_environment`,这些地方我估计是给本地登陆桌面用的，`VNC`取不到这些变量，这也是测试出来的结果。


最后使用`systemctl`管理服务，注意这个版本已经不再使用`vncserver`了，一些旧的文档还是用这个，启动会报错。

```bash
cp /lib/systemd/system/tigervncserver@.service  /etc/systemd/system/

 systemctl daemon-reload
 systemctl enable tigervncserver@:1.service
 systemctl start tigervncserver@:1.service

```


  #  注意

  使用`tigervnc`注意这个情况[同一个用户，无法同时远程登录和本地登录]( https://github.com/TigerVNC/tigervnc/issues/1179)

  如果本地登录，需要停用这个`tigervncserver@1.service`
 
  如果远程登陆，`pkill`掉这个用户`lance`的所有进程也不行，一定要在本地注销掉这个用户。



然后就可以使用`vncviewer`愉快的继续使用Debian11了。