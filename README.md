# NLA Strip Stepper

# 概要

BlenderのNLAストリップに対して〝コマ落とし〟を適用するために開発しました。

# インストール方法

ZIPファイルでDLするか、プロジェクトフォルダごとZIPに変換してもいいと思います。

そしてBlenderのプリファレンスより、インストールでZIPを指定してください。

# 使い方について

NLAエディタでストリップを選択して、ドープシートのUIパネルで操作します。

キーフレームを挿入できるのは、あくまでNLAストリップの長さに収まる範囲です。

NLAストリップを移動しても自動では追従しないので、そのためにアジャスト機能を用意しました。

ドープシートでストリップ時間のキーフレームを手動で前後に動かすと、タメやツメの表現もできると思います。

# 現状の問題点

BlenderのSystemメニューから〝Reload Scripts〟を実行するとBlenderが〝不安定〟になり、時間が経つと落ちてしまうようです。

# Lisence

This project is licensed under the MIT License, see the LICENSE.txt file for details

![サンプル画像](https://github.com/yakage-yu/NLA_StripStepper/blob/master/NLA_StripStepper_ss000.png?raw=true "サンプル")
