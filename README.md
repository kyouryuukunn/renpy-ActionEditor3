 youtube sample

Ren'Py ActionEditor Update 220305 <https://www.youtube.com/watch?v=7Mosa88gY-c>

Introduce ActionEditor Update 20220212 <https://www.youtube.com/watch?v=h2Zdhugiho8>

Ren'Py Action Editor Introduction <https://www.youtube.com/watch?v=VMMBj4-7k_Q>

How to use spline in Action Editor with graphic editor <https://www.youtube.com/watch?v=qmGSsJbTYx4>

Quick Overview of the 3D Camera for Ren'Py <https://www.youtube.com/watch?v=lhA8Ib3iKE8>

lemma forum
<https://lemmasoft.renai.us/forums/viewtopic.php?f=8&t=29778>

 日本語マニュアルはドキュメント後半にあります。

 This script adds Ren'py the ability to adjust and view transform properties of images
 and camera by in-game Action Editor and Image Viewer and Sound Viewer.

 Ren'Py <http://www.renpy.org/>

![Demo](https://dl.dropboxusercontent.com/s/cyfizgl2pvk8w9x/ActionEditor.png)

 This is available in v7.4.5 later.
 To use in older version, use old version ActionEditor.
 <https://github.com/kyouryuukunn/renpy-ActionEditor>

 In current version ActionEditor, below functions are removed.
 * expression
 * loading last action

 To install, copy all files in the camera directory into your game directory.
 ActionEditor.rpy is required for release version if you use camera blur or warper_generator.
 00warper.rpy is also required if you use added warpers. Ohter files arenot required.

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
 * ActionEditor Can't get correct value If any other transform_matrix than below Matrixes are used.
    OffsetMatrix * RotateMatrix
    OffsetMatrix
    RotateMatrix
 * ActionEditor Can't get colormatrix property.
 * The behavior of functions for function property isn't same as ATL.
   There are some different points.
  1. inherited_<property> have no value.
  2. Setting properties have no affect when it is called next time.
  3. The return value from it have no affect.
   You should note it isn't always called in time.
 * Skipping animations may not work when those include the tags which are already shown and have loop animations.
   When using functions other than camera_blur, these may cause malfunction after skip.

 How to add desired properties to the editor.
 Add the names of the properties you want to add to props_set, sort_order_list
 and transform_props or camera_props in ActionEditor_config.rpy. If the type of
 the property you want to add is int or float, also add it to force_float,
 force_wide_range, or force_plus as needed. if it is a boolean value, add it to
 boolean_props. If it is not one of those, add it to any_props where any type
 can be entered. Please note that error checking is not available when using
 this function, so please be careful about the order of input.

 For tuples, you can use props_groups where key is the property name and value
 is tuple of each element name, so that they can be edited individually. Also
 set generate_groups_clipboard and generate_groups_value to combine individual
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
 Showing defined images and filtering that by tag and atrribute.
 The completion feature is availabe by tab
 
 Press Shift+U to open Image Viewer and view all currently generated displayables.

 Sound Viewer
================
 Showing auto defined sounds in game/audio and filtering.
 The completion feature is availabe by tab
 
 Press Shift+S to open Sound Viewer and view all currently generated displayables.








 本ライブラリでは3Dステージ対応のGUI上で設定できる演出エディター、画像ビューワー、サウンドビューワーさらに便利なワーパー関数を追加します。
 Ren'Py v7.4.5から追加された3Dステージ機能により、旧版にあった自作の3Dカメラ再現関数は不要になりました。
 v7.4.5以前のバージョンでは旧版のActionEditorを使用してください。
 <https://github.com/kyouryuukunn/renpy-ActionEditor>

 3Dカメラの再現を自作スクリプトから3Dステージに切り替えたことにより、旧版にあった最後のアクションを読み込む機能、エクスプレッション機能はなくなりました。
 使用したい場合はそれぞれ以下で代用してください。
 * エクスプレッション function transform プロパティで代用してください。 <https://ja.renpy.org/doc/html/atl.html#function-statement>

 使用にはフォルダ内のファイルをgameフォルダにコピーしてください。
 カメラブラー、ワーパージェネレータを使用している場合にはActionEditor.rpyを、追加ワーパーを使用している場合は00warper.rpyをリリース版にも含めてください。
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
 *focusingを有効化している間、function transform プロパティーで利用しているため各画像のblurは利用できなくなります。
 *matrixtransformプロパティーの値をエディターで読み込むことは困難なため現在以下の順番、組み合わせのみに対応しています。
    OffsetMatrix * RotateMatrix
    OffsetMatrix
    RotateMatrix
 *colormatrixプロパティーは現在の値をエディターでは読み込めません。
 *function プロパティーに関数を指定してもActionEditorとATL中では同じ動作をしないことに注意してください。
  以下の制限があります。
  1. inherited_<property>では値を取得できません。
  2. プロパティーを変更しても次のその関数呼び出し時には反映されない。
  3. 返り値は機能しない。
  また時間どおりの順に呼び出されるとは限りません。
 *アニメーションのスキップはアニメーション終了後と同じ画像を表示してスキップを可能にしています。
  アニメーション開始前から同じタグの画像がすでに表示されており、かつそのタグのアニメーションにループが含まれている場合は正常に動作しません。
  また、camera_blur 以外を function プロパティーに使用しているとスキップ後に誤作動する可能性があります。
 参考リンク
 http://akakyouryuu.com/renpy/renpy%e3%81%aeatl%e3%82%a2%e3%83%8b%e3%83%a1%e3%83%bc%e3%82%b7%e3%83%a7%e3%83%b3%e3%82%92%e3%82%af%e3%83%aa%e3%83%83%e3%82%af%e3%81%a7%e3%82%b9%e3%82%ad%e3%83%83%e3%83%97%e3%81%a7%e3%81%8d%e3%82%8b/

 任意のプロパティーをエディターに追加する方法
 ActionEditor_config.rpyのprops_set, sort_order_listとtransform_propsまたはcamera_propsに追加したいプロパティー名を加えます。
 さらに追加したいプロパティーの型が整数または浮動小数ならば必要に応じてforce_float, force_wide_range, force_plusに、
 真偽値ならばboolean_propsにプロパティー名を追加します。プロパティーの型がそれら以外ならばどのような型も入力できるany_propsに追加してください。 
 使用時はエラーチェックを行なえないので入力順番等に注意してください。

 タプルなど複数の値で1つのプロパティーを設定するものはprops_groupsでプロパティー名をキーに、各要素名を値にして登録すれば個別に編集できるようになります。
 個別の値を1つにまとめるためにgenerate_groups_clipboard, generate_groups_valueも設定してください。例:
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
 定義された画像を画像タグ、属性から縛り込んで表示します。
 タブでの補間も可能です。

 config.developer が True なら、Shift+Uで起動します。


 サウンドビューワー
================
 game/audioディレクトリーで自動定義された変数一覧を縛り込んで表示します。
 タブでの補間も可能です。

 config.developer が True なら、Shift+Sで起動します。

