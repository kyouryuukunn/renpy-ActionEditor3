 本ライブラリでは、GUI上で設定できる3Dステージ対応の演出エディター、および画像ビューワーとサウンドビューワーさらに多数のワーパー関数とATLのfunctionステートメントでの使用を意図した便利な関数群を追加します。
 日本語マニュアルはドキュメント後半にあります。

 This script adds Ren'py the ability to adjust and view transform properties of images
 and camera by in-game Action Editor and Image Viewer and Sound Viewer.
 Many warpers and usefull functions intended to be used in function statement in ATL are
 also added.

 Ren'Py <http://www.renpy.org/>

![Demo](https://dl.dropboxusercontent.com/s/cyfizgl2pvk8w9x/ActionEditor.png)

 youtube samples:

 * Ren'Py ActionEditor Update 220505 <https://www.youtube.com/watch?v=AXf4JQVq3v8>
 * Ren'Py ActionEditor Update 220305 <https://www.youtube.com/watch?v=7Mosa88gY-c>
 * Introduce ActionEditor Update 20220212 <https://www.youtube.com/watch?v=h2Zdhugiho8>
 * Ren'Py Action Editor Introduction <https://www.youtube.com/watch?v=VMMBj4-7k_Q>
 * How to use spline in Action Editor with graphic editor <https://www.youtube.com/watch?v=qmGSsJbTYx4>
 * Quick Overview of the 3D Camera for Ren'Py <https://www.youtube.com/watch?v=lhA8Ib3iKE8>

lemma forum
<https://lemmasoft.renai.us/forums/viewtopic.php?f=8&t=29778>





 Endglish Document
================

 This script adds Ren'py the ability to adjust and view transform properties of images
 and camera by in-game Action Editor and Image Viewer and Sound Viewer.
 Many warpers and usefull functions intended to be used in function statement in ATL are
 also added.

 About old version
================
 This is available in v7.4.5 later.
 To use in older version, use old version ActionEditor.
 <https://github.com/kyouryuukunn/renpy-ActionEditor>

 In current version ActionEditor, below functions are removed.
 * expression
 * loading last action

 To instal
================
 To install, copy all files in the camera directory into your game directory.
 ActionEditor.rpy is required for release version if you use camera blur or warper_generator.
 00warper.rpy is also required if you use added warpers.
 ATL_funcctions.rpy is also required if you use added functions for ATL statement.
 Ohter files arenot required.

 Action Editor
================

 This allows you to adjusts transform properties of camera and images in
 real-time with a GUI. It can then generate a script based on these changes and
 place it on the clipboard for later pasting into Ren'Py scripts.

 When `config.developer` is True, pressing action_editor (by default,
 "shift+P") will open the Action editor.
 
 The Action Editor has the following features:
 
  * View and adjust the transform properties of images and camera with adjusting a bar or typing value.
  * View and adjust the x and y coordinates of the camera with a draggable camera icon.
  * Adjust the z coordinate of the camera with the mouse wheel.
  * Adjust the x,y coordinate of the camera with the keyboard(hjkl, HJKL, wasd, WASD).
  * Reset the value with right-click on the value button.
  * Add, delete, and edit keyframes on a timeline like video editing software.
  * the spline motion and loop is availabe
  * After setting up a scene with the desired look and animations, the Action
    Editor will generate a script and place it on your clipboard for pasting
    into your Ren'Py scripts. (v6.99 and later only)
  * Introducing the concept of depth of field and allow to adjust focus position and dof.
    Blur each image according to dof, focus postion and the distance between the camera and the image.
  * Show, replace and hide a image with transition(use None for a image name to hide image)
  * Change a scene with scene statement.
  * There is the option for hiding window during the ATL animation in clipboard data.
  * There is the option for allowing to skip ATL animation in clipboard data.

 Note
 * blur transform property of each images are used for simulating camera blur in function transform prperty,
   so blur transform properties of each images aren't availabe when focusing is enabled.
   Set function property to None when you want to disable camera blur for already shownd images.
 * ActionEditor Can't get correct value If any other transform_matrix than below Matrixes are used.:
   1. OffsetMatrix * RotateMatrix
   2. OffsetMatrix
   3. RotateMatrix

 * ActionEditor Can't get colormatrix property.
 * Unfortunately, The behavior of functions for function property isn't same as ATL.
   There are some different points.
  1. inherited_<property> have no value.
  2. Setting properties have no affect when it is called next time.
  3. The return value from it have no affect.
  4. It isn't always called in time.

 * Skipping animations may not work when those include the tags which are already shown and have loop animations.
   When using functions other than camera_blur, these may cause malfunction after skip.


 How to add desired properties to the editor.
================

 variable is edited in ActionEditor_config.rpy.

 Commonly, add the following variables the property name you want to add to be added.:

 * `props_set`: control where that is shwon in ActionEditor.
 * `sort_order_list`: control where that is shwon in clipboard.
 * `transform_props` or `camera_props`: Add the tuple which include that property name and default value.
 Adding `transform_props` shows it in each images and Adding `camera_props` shows it in camera.

 Further add the following variables according to the type of property.

 If it is integer or float and required. :

 * `force_float`: it is always float.
 * `force_wide_range`: it has the same scale as integer even when it is float type.
 * `force_plus`: it is always plus.

 If it is boolean type. :

 * `boolean_props`

 Others:

 * `any_props` : This type isn't checked error. so you should pay attention to the input order.


 Property Group
================

 For tuple, You can use `props_groups` where that key is the property name and that value
 is the tuple of each element name, so that they can be edited individually. Also
 set `generate_groups_clipboard` and `generate_groups_value` to combine individual
 values into one. example:

    props_groups = {
        "alignaround":["xalignaround", "yalignaround"], 
        "matrixtransform":["rotateX", "rotateY", "rotateZ", "offsetX", "offsetY", "offsetZ"], 
        "matrixanchor":["matrixanchorX", "matrixanchorY"], 
        "matrixcolor":["invert", "contrast", "saturate", "bright", "hue"], 
        "crop":["cropX", "cropY", "cropW", "cropH"], 
        "focusing":["focusing", "dof"], 
    }

    def generate_matrixtransform_value(rotateX, rotateY, rotateZ, offsetX, offsetY, offsetZ):
        return Matrix.offset(offsetX, offsetY, offsetZ)*Matrix.rotate(rotateX, rotateY, rotateZ)
    generate_groups_value["matrixtransform"] = generate_matrixtransform_value

    def generate_matrixtransform_clipboard(rotateX, rotateY, rotateZ, offsetX, offsetY, offsetZ):
        v = "OffsetMatrix(%s, %s, %s)*RotateMatrix(%s, %s, %s)"
        return v % (offsetX, offsetY, offsetZ, rotateX, rotateY, rotateZ)
    generate_groups_clipboard["matrixtransform"] = generate_matrixtransform_clipboard

 Exclusive proparties like tile and pan should be set in exclusive. example:

    exclusive = (
            ({"xpos", "ypos"}, {"xalignaround", "yalignaround", "radius", "angle"}), 
            ({"xtile", "ytile"}, {"xpan", "ypan"}), 
        )


 Image Viewer
================
 If `config.developer` is True, pressing Shift+U or +(add image) textbutton on ActionEditor
 to open Image Viewer.

 Defined image tag and attribute textbuttons are shown in this viewer.
 You can filter them by the text entered in the top-most text entry field.
 The completion feature is also availabe by tab.

 When these textbuttons get focus and the same image name exist as these text, the image is
 shown.
 Pressing the textbutton add that text to the filter if the same image name doesn't exist
 as that text. the image is added to ActionEditor if that exist and viewer is opened by
 ActionEditor.  the image name is outputted to the clipboard if that exist and viewer isn't
 opened by ActionEditor. 

 Pressing clipboard buton at the bottom also outputs the filter string to clipboard 
 

 Sound Viewer
================
 If `config.developer` is True, pressing Shift+S or sounds textbutton on ActionEditor
 to open Sound Viewer.

 Variable names in audio store are shown in this viewer.
 The music files should be automatically defined as these name.
 You can filter them by the text entered in the top-most text entry field.
 The completion feature is also availabe by tab.

 When these textbuttons get focus and the music file is played.
 Pressing the textbutton add that to ActionEditor if the viewer is opened by ActionEditor.
 Otherwise, that name is outputted to the clipboard.

 Pressing clipboard buton at the bottom also outputs the filter string to clipboard 

 ATL functions
================
 ATL_funcctions.rpy adds usefull functions which are intended to be used for
 function statement in ATL block. For more information, see that file.








 日本語ドキュメント
================
 本ライブラリでは、GUI上で設定できる3Dステージ対応の演出エディター、および画像ビューワーとサウンドビューワーさらに多数のワーパー関数とATLのfunctionステートメントでの使用を意図した便利な関数群を追加します。

 旧バージョンについて
================

 Ren'Py v7.4.5から追加された3Dステージ機能により、旧版にあった自作の3Dカメラ再現関数は不要になりました。
 v7.4.5以前のバージョンでは旧版のActionEditorを使用してください。
 <https://github.com/kyouryuukunn/renpy-ActionEditor>

 3Dカメラの再現を自作スクリプトから3Dステージに切り替えたことにより、旧版にあった最後のアクションを読み込む機能とエクスプレッション機能はなくなりました。
 使用したい場合はそれぞれ以下で代用してください。
 * エクスプレッション function ステートメントで代用してください。 <https://ja.renpy.org/doc/html/atl.html#function-statement>

 インストール方法
================

 使用にはフォルダ内のファイルをgameフォルダにコピーしてください。
 カメラブラー、ワーパージェネレータを使用している場合にはActionEditor.rpyを、追加ワーパーを使用している場合は00warper.rpyを、追加function ステートメント向け関数を使用している場合はATL_functions.rpyもリリース版に含めてください。
 他のファイルは必要ありません。

 演出エディター(Action Editor)
================

 演出エディターではcameraや画像の transform プロパティーをGUI上で変更し、結果を
 確認できます。さらにそれらの値を時間軸に沿って変更可能なので、スクリプトを変更
 するたびに、リロードで結果を確認する従来の方法より遥かに短時間でアニメーション
 を作成可能です。設定したアニメーションをクリップボードに送って、スクリプトに貼
 り付けられます。
 さらにfocusingを有効にすると被写界深度の概念をRen'Pyに導入して、カメラと画像と
 の距離に応じてブラーがかかるようにもできます。。

 config.developer が True なら、Shift+Pで演出エディターが起動します。
 
 演出エディターでは以下の機能が利用可能です。:
 
 * カメラや各画像の transform プロパティーを直接数値入力またはバーの操作により変更
 * カメラアイコンのドラッグでカメラのx,y座標を移動
 * マウスホイールでカメラのz座標を移動
 * キーボード(hjkl,HJKL,wasd,WASD)によりカメラのxy座標を移動
 * 数値を右クリックでリセット
 * 動画編集ソフトの様にキーフレームを設定して時間軸にそった演出を作成
 * transform プロパティーへのスプライン補間やループ設定
 * 作成した演出のコードをクリップボードに送る(v6.99以上, Windows限定)
 * 被写界深度の概念を導入し、フォーカス位置と被写界深度を操作可能にする。これらの
   値とカメラと各画像のz座標から各画像にブラーがかけられる(通常のブラーと排他)
 * トランジションを伴う画像の表示、置き換え、非表示
   (画像を非表示するには画像名にNoneを入力してください)
 * sceneステートメントによるシーンの切り替え
 * オプションから、アニメーション中はウィンドウを非表示にするフォーマットでクリップボードに出力するか選択可
   (複数シーンを使用する場合は強制的にウィンドウ非表示となります)
 * オプションから、アニメーションスキップ可能にするフォーマットでクリップボードに出力するか選択可
   (複数シーンを使用する場合は強制的にスキップ可となります)

 注意

 * focusingを有効化している間、function transform プロパティーで利用しているため各画像のblurは利用できなくなります。
 * matrixtransformプロパティーの値をエディターで読み込むことは困難なため現在以下の順番、組み合わせのみに対応しています。
  1. OffsetMatrix * RotateMatrix
  2. OffsetMatrix
  3. RotateMatrix

 * colormatrixプロパティーは現在の値をエディターでは読み込めません。
 * function ステートメントに関数を指定できますが、ActionEditorとATL中で関数が同じ動作をしないことに注意してください。
  以下の制限があります。
  1. inherited_(property) では値を取得できません
  2. プロパティーを変更しても次のその関数呼び出し時の値には反映されません
  3. 返り値は機能しません
  4. 時間どおりの順に呼び出されるとは限りません。
  これらの制限のため、プロパティーの値に対するオフセットとして動作させるには癖があり、もっぱらx,yoffsetへの値の代入が主な用途となるでしょう。
 参考リンク
 https://akakyouryuu.com/renpy/atl-%e3%81%aefunction%e3%82%b9%e3%83%86%e3%83%bc%e3%83%88%e3%83%a1%e3%83%b3%e3%83%88%e3%81%a7%e3%83%97%e3%83%ad%e3%83%91%e3%83%86%e3%82%a3%e3%83%bc%e3%81%ae%e5%80%a4%e3%82%92%e3%82%aa%e3%83%95/
 * camera_blur 以外を function プロパティーに使用しているとスキップ後に誤作動する可能性があります。
 * アニメーション開始前から同じタグの画像がすでに表示されており、かつそのタグのアニメーションにループが含まれている場合は正常に動作しません。
 参考リンク
 http://akakyouryuu.com/renpy/renpy%e3%81%aeatl%e3%82%a2%e3%83%8b%e3%83%a1%e3%83%bc%e3%82%b7%e3%83%a7%e3%83%b3%e3%82%92%e3%82%af%e3%83%aa%e3%83%83%e3%82%af%e3%81%a7%e3%82%b9%e3%82%ad%e3%83%83%e3%83%97%e3%81%a7%e3%81%8d%e3%82%8b/


 任意のプロパティーをエディターに追加する方法
================

 ActionEditor_config.rpy を編集します。

 共通の設定項目として以下に追加したいプロパティー名を加えます。:

 * `props_set`: ActionEditor上でプロパティーが表示される位置を指定します。
 * `sort_order_list`: クリップボードに出力されるプロパティーの順番を指定します。
 * `transform_props` または `camera_props`: プロパティー名とデフォルト値のタプルを追加してください。前者は画像の、後者はカメラの追加プロパティーを操作できるようにします。
 
 さらに追加したいプロパティーの型に応じて設定します。

 整数または浮動小数の場合、必要なら以下に追加したいプロパティー名を加えます。:

 * `force_float`: 常に値が浮動小数になります。
 * `force_wide_range`: 値が浮動小数でも整数と同じ幅で値を調整できます。
 * `force_plus`: 常に値が正の数となります。

 真偽値の場合、以下に追加したいプロパティー名を加えます。:

 * `boolean_props`

 他の型の場合、以下に追加したいプロパティー名を加えます。:

 * `any_props` : 使用時はエラーチェックを行なえないので入力順番等に注意してください。


 プロパティーグループ
================

 タプルなど複数の値で1つのプロパティーを設定するものは props_groups でプロパティー名をキーに、
 各要素名を値にして登録すれば個別に編集できます。個別の値を1つにまとめるために 
 `generate_groups_clipboard`, `generate_groups_value` も設定してください。例:

    props_groups = {
        "alignaround":["xalignaround", "yalignaround"], 
        "matrixtransform":["rotateX", "rotateY", "rotateZ", "offsetX", "offsetY", "offsetZ"], 
        "matrixanchor":["matrixanchorX", "matrixanchorY"], 
        "matrixcolor":["invert", "contrast", "saturate", "bright", "hue"], 
        "crop":["cropX", "cropY", "cropW", "cropH"], 
        "focusing":["focusing", "dof"], 
    }

    def generate_matrixtransform_value(rotateX, rotateY, rotateZ, offsetX, offsetY, offsetZ):
        return Matrix.offset(offsetX, offsetY, offsetZ)*Matrix.rotate(rotateX, rotateY, rotateZ)
    generate_groups_value["matrixtransform"] = generate_matrixtransform_value

    def generate_matrixtransform_clipboard(rotateX, rotateY, rotateZ, offsetX, offsetY, offsetZ):
        v = "OffsetMatrix(%s, %s, %s)*RotateMatrix(%s, %s, %s)"
        return v % (offsetX, offsetY, offsetZ, rotateX, rotateY, rotateZ)
    generate_groups_clipboard["matrixtransform"] = generate_matrixtransform_clipboard

 tileとpanのような排他的なプロパティーはexclusiveにも登録してください。例:

    exclusive = (
            ({"xpos", "ypos"}, {"xalignaround", "yalignaround", "radius", "angle"}), 
            ({"xtile", "ytile"}, {"xpan", "ypan"}), 
        )


 画像ビューワー
================

 `config.developer` が True なら、ゲーム画面でShift+UまたはActionEditor上の+(add image)のボタンから開けます。

 定義済の画像のタグ、属性のテキストボタンとして一覧表示します。
 最上段のテキスト入力欄に入力されたテキストで表示結果をフィルターします。
 フィルターではタブキーでの補完も可能です。

 テキストボタンにフォーカスするとそのテキストに対応する画像名があればその画像を表示します。
 ボタンを押すと、対応する画像名がなければ、そのテキストをフィルターに追加します。
 ある場合、ActionEditor上から開いてれば、それをActionEditorに追加します。そうでなければ、
 その画像名をクリップボードに出力します。
 

 最底段のclipboardボタンでフィルターテキストをクリップボードに出力できます。


 サウンドビューワー
================

 `config.developer` が True なら、ゲーム画面でShift+SまたはActionEditor上のSoundsの項目から開けます。

 audio store にある変数名をテキストボタンとして一覧表示します。
 音声ファイルがgame/audioディレクトリーにあれば変数は自動定義されるはずです。
 最上段のテキスト入力欄に入力されたテキストで表示結果をフィルターします。
 フィルターではタブキーでの補完も可能です。

 ボタンにフォーカスするとその音声が再生されます。
 ボタンをクリックするとActionEditor上から開いていれば、それがActionEditorに追加されます。
 そうでなければ、そのボタンテキストをクリップボードに出力します。

 最低段のclipboardボタンでフィルターテキストをクリップボードに出力できます。


 ATL functions
================

 ATL_funcctions.rpy に ATL function ステートメントでの使用を意図した関数群を用意しました。
 使用方法は該当ファイルを参照してください。
