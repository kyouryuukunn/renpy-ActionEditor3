 本ライブラリでは、GUI上で設定できる演出エディターおよび画像ビューワーとサウンドビューワー、さらにATLのfunctionステートメントでの使用を意図した便利な関数群と多数のワーパー関数を追加します。
 日本語マニュアルはドキュメント後半にあります。

 This script adds Ren'py the ability to adjust and view transform properties of images
 and camera by in-game Action Editor, Image Viewer and Sound Viewer.
 Many warpers and useful functions intended to be used in function statements in ATL are
 also added.

 Ren'Py <http://www.renpy.org/>

lemma forum
<https://lemmasoft.renai.us/forums/viewtopic.php?f=8&t=29778>

![Demo](https://dl.dropboxusercontent.com/s/cyfizgl2pvk8w9x/ActionEditor.png)

 youtube samples:
 * Tutorials チュートリアル <https://www.youtube.com/playlist?list=PLVAQBcrPbK5J33EbslA6sRSsNAeUZ92EG>

 * Introduce ATL_functions <https://www.youtube.com/watch?v=AXf4JQVq3v8>
 * Introduce generate warper <https://www.youtube.com/watch?v=7Mosa88gY-c>
 * Introduce ActionEditor Update 20220212 <https://www.youtube.com/watch?v=h2Zdhugiho8>



 English Document
================

 This script adds Ren'py the ability to adjust and view transform properties of images
 and camera by in-game Action Editor, Image Viewer and Sound Viewer.
 Many warpers and useful functions intended to be used in function statements in ATL are
 also added.

 About old version
================
 This is available in v7.4.5 later.
 To use an older version, use the old version of ActionEditor.
 <https://github.com/kyouryuukunn/renpy-ActionEditor>
 
 In the current version of ActionEditor, the below functions are removed.
 * expression
 * loading last action

 To install
================
 To install, copy all files in the camera directory into your game directory.
 ActionEditor.rpy is required for release version if you use camera blur or warper_generator.
 00warper.rpy is also required if you use added warpers.
 ATL_funcctions.rpy is also required if you use added functions for ATL statement.
 Other files are not required.

 Action Editor
================

 This allows you to adjust transform properties of camera and images in
 real-time with a GUI. It can then generate a script based on these changes and
 place it on the clipboard for later pasting into Ren'Py scripts.

 When `config.developer` is True, pressing action_editor (by default,
 "shift+P") will open the Action editor.
 
 The Action Editor has the following features:
 
  * View and adjust the transform properties of images and camera by adjusting a bar or typing a value.
  * View and adjust the x and y coordinates of the camera with a draggable camera icon.
  * Adjust the z coordinate of the camera with the mouse wheel.
  * Adjust the x,y coordinate of the camera with the keyboard(hjkl, HJKL, wasd, WASD).
  * Reset the value by right-clicking on the value button.
  * Add, delete, and edit keyframes on a timeline like video editing software.
  * The spline motion and loop is available
  * After setting up a scene with the desired look and animations, the Action
    Editor will generate a script and place it on your clipboard for pasting
    into your Ren'Py scripts. (v6.99 and later only)
  * Introducing the concept of depth of field and allow to adjust focus position and dof.
    Blur each image according to dof, focus position and the distance between the camera and the image.
  * Show, replace and hide a image with transition(use None for a image name to hide image)
  * Change a scene with scene statement.
  * There is the option for hiding window during the ATL animation in clipboard data.
  * There is the option for allowing to skip ATL animation in clipboard data.

 Note
 * blur transform property of each images are used for simulating camera blur in function transform property,
   so blur transform properties of each images aren't available when focusing is enabled.
   Set function property to None when you want to disable camera blur for already shown images.
 * Unfortunately, The behavior of functions for function property isn't the same as ATL.
   There are some different points.
   1. inherited_<property> have no value.
   2. Setting properties have no effect when it is called next time.
   3. The return value from it has no effect.
   4. It isn't always called in time.
  ActionEditor can't get current function when opened.

 * Skipping animations may not work when those include the tags which are already shown and have loop animations.
   When using functions other than camera_blur, these may cause malfunction after skip.
 * ActionEditor supports ScaleMatrix, OffsetMatrix, RotateMatrix and ignores other matrixtransforms.
 * ActionEditor supports InvertMatrix, ContrastMatrix, SaturationMatrix, BrightnessMatrix, HueMatrix and ignores other matrixcolors.


 How to add desired properties to the editor.
================

 variable is edited in ActionEditor_config.rpy.

 Commonly, add the following variables the property name you want to add to be added.:

 * `props_set`: control where that is shown in ActionEditor.
 * `sort_order_list`: control where that is shown in the clipboard.
 * `transform_props` or `camera_props`: Add the the property name.
 Adding `transform_props` shows it in each images and Adding `camera_props` shows it in camera.
 * `property_default_value`: Add the default value of the property.

 Further add the following variables according to the type of property.

 If it is integer or float and required. :

 * `force_wide_range`: it has the same scale as integer even when it is float type.
 * `force_narrow_range`: it has the same scale as float even when it is int type.
 * `force_plus`: it is always plus.
 * `force_float`: it is always float.

 If it is boolean type. :

 * `boolean_props`

 Others:

 * `any_props`: this accepts all types. I recommend also using `check_any_props` or `menu_props`.

 * `check_any_props`: This maps a property name to the function. This is called
   with the value of the property and set the property the value if result is
   True. Otherwise, the error message is shown.

    any_props = {"blend"}
    check_any_props = {"blend":lambda v: v in (None, "normal", "add", "multiply", "min", "max")}

 * `menu_props` : use selectable buttons to change `anpy_props` instead of input screen.

    any_props = {"blend"}
    menu_props = {"blend":[None] + [key for key in config.gl_blend_func]}

 Exclusive properties like tile and pan should be set in `exclusive`. example:

    exclusive = (
            ({"xpos", "ypos"}, {"xalignaround", "yalignaround", "radius", "angle"}), 
            ({"xtile", "ytile"}, {"xpan", "ypan"}), 
        )


 Property Group
================

 For tuples, you can use `props_groups` where that key is the property name and that value
 is the tuple of each element name, so that they can be edited individually. example:

    props_groups = {
        "alignaround":["xalignaround", "yalignaround"], 
        "matrixanchor":["matrixanchorX", "matrixanchorY"], 
        "crop":["cropX", "cropY", "cropW", "cropH"], 
        "focusing":["focusing", "dof"], 
    }


 Image Viewer
================
 If `config.developer` is True, pressing Shift+U or +(add image) textbutton on ActionEditor
 to open Image Viewer.

 Defined image tags and attribute textbuttons are shown in this viewer.
 You can filter them by the text entered in the top-most text entry field.
 The completion feature is also available by tab.

 When these textbuttons get focus and the same image name exists as these text, the image is
 shown.
 Pressing the textbutton add that text to the filter if the same image name doesn't exist
 as that text. the image is added to ActionEditor if that exist and viewer is opened by
 ActionEditor.  the image name is outputted to the clipboard if that exist and viewer isn't
 opened by ActionEditor. 

 Pressing clipboard button at the bottom also outputs the filter string to clipboard 
 

 Sound Viewer
================
 If `config.developer` is True, pressing Shift+S or sounds textbutton on ActionEditor
 to open Sound Viewer.

 Variable names in audio store are shown in this viewer.
 The music files should be automatically defined as these name.
 You can filter them by the text entered in the top-most text entry field.
 The completion feature is also available by tab.

 When these textbuttons get focus and the music file is played.
 Pressing the textbutton adds that to ActionEditor if the viewer is opened by ActionEditor.
 Otherwise, that name is outputted to the clipboard.

 Pressing clipboard button at the bottom also outputs the filter string to clipboard 

 ATL functions
================
 ATL_funcctions.rpy adds useful functions which are intended to be used for
 function statement in ATL block. For more information, see that file.


 Matrix
================

 The default matrix and order for each is as follows.

    matrixtransform: ScaleMatrix*OffsetMatrix*RotateMatrix*OffsetMatrix*OffsetMatrix
    matrixcolors: InvertMatrix*ContrastMatrix*SaturationMatrix*BrightnessMatrix*HueMatrix

 You can change default matrix, that order and default value by editing default_matrixtransform or default_matrixcolor in ActionEditor_config.rpy.

    default_matrixtransform = [
        ("matrixtransform_1_1_scaleX", 1.),  ("matrixtransform_1_2_scaleY", 1.),  ("matrixtransform_1_3_scaleZ", 1.),
        ("matrixtransform_2_1_offsetX", 0.), ("matrixtransform_2_2_offsetY", 0.), ("matrixtransform_2_3_offsetZ", 0.),
        ("matrixtransform_3_1_rotateX", 0.), ("matrixtransform_3_2_rotateY", 0.), ("matrixtransform_3_3_rotateZ", 0.),
        ("matrixtransform_4_1_offsetX", 0.), ("matrixtransform_4_2_offsetY", 0.), ("matrixtransform_4_3_offsetZ", 0.),
        ("matrixtransform_5_1_offsetX", 0.), ("matrixtransform_5_2_offsetY", 0.), ("matrixtransform_5_3_offsetZ", 0.),
    ]
    default_matrixcolor = [
        ("matrixcolor_1_1_invert", 0.), 
        ("matrixcolor_2_1_contrast", 1.), 
        ("matrixcolor_3_1_saturate", 1.),
        ("matrixcolor_4_1_bright", 0.),
        ("matrixcolor_5_1_hue", 0.), 
    ]


 Text Size
================
 
 All text style is changeable by new_action_editor_text style.

    init:
        style new_action_editor_text:
            size 10

 Troubleshooting
================

 Layout is corrupted

 Too long tag names and big font sizes corrupt the layout of ActionEditor.
 In that case, try to adjust the size of font by the above manner.


 Known issue
================

 ActionEditor can't show camera and displayable with "at clause" including animation correctly.

 ActionEditor can't show movie and animation displayable correctly.


 Note
================

 The clipboard from ActionEditor includes the difference from the state when ActionEditor is opened on. Therefore that is intended to be pasted on next that line. Images aren't shown correctly if the existing lines are overwritten.


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
 リリース時には追加したファイルは不要になりますが、次の場合は配布ファイルに追加ファイルを残してください。
 * カメラブラー、ワーパージェネレータを使用している場合にはActionEditor.rpが必要です。
 * 追加ワーパーを使用している場合は00warper.rpyが必要です。
 * function ステートメント向け追加関数を使用している場合はATL_functions.rpyが必要です。

 演出エディター(Action Editor)
================

 演出エディターではcameraや画像の transform プロパティーをGUI上で変更し、結果を
 確認できます。さらにそれらの値を時間軸に沿って変更可能なので、スクリプトを変更
 するたびに、リロードで結果を確認する従来の方法より遥かに短時間でアニメーション
 を作成可能です。設定したアニメーションはクリップボード経由でスクリプトに貼り付
 けられます。
 さらにfocusingを有効にすると被写界深度の概念をRen'Pyに導入して、カメラと画像と
 の距離に応じてブラーがかかるようにもできます。

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
 * function ステートメントに関数を指定できますが、ActionEditorとATL中で関数が同じ動作をしないことに注意してください。
  以下の制限があります。
   1. inherited_(property) では値を取得できません
   2. プロパティーを変更しても次のその関数呼び出し時の値には反映されません
   3. 返り値は機能しません
   4. 時間どおりの順に呼び出されるとは限りません。
  これらの制限のため、プロパティーの値に対するオフセットとして動作させるには癖があり、もっぱらx,yoffsetへの値の代入が主な用途となるでしょう。
  加えて、ActionEditor起動時に現在のfuncitonは読み込めません
 参考リンク
 https://akakyouryuu.com/renpy/atl-%e3%81%aefunction%e3%82%b9%e3%83%86%e3%83%bc%e3%83%88%e3%83%a1%e3%83%b3%e3%83%88%e3%81%a7%e3%83%97%e3%83%ad%e3%83%91%e3%83%86%e3%82%a3%e3%83%bc%e3%81%ae%e5%80%a4%e3%82%92%e3%82%aa%e3%83%95/
 * camera_blur 以外を function プロパティーに使用しているとスキップ後に誤作動する可能性があります。
 * アニメーション開始前から同じタグの画像がすでに表示されており、かつそのタグのアニメーションにループが含まれている場合は正常に動作しません。
 参考リンク
 http://akakyouryuu.com/renpy/renpy%e3%81%aeatl%e3%82%a2%e3%83%8b%e3%83%a1%e3%83%bc%e3%82%b7%e3%83%a7%e3%83%b3%e3%82%92%e3%82%af%e3%83%aa%e3%83%83%e3%82%af%e3%81%a7%e3%82%b9%e3%82%ad%e3%83%83%e3%83%97%e3%81%a7%e3%81%8d%e3%82%8b/
 * matrixtransformはScaleMatrix, OffsetMatrix, RotateMatrixのみサポートしています。それ以外は無視されます。
 * matrixcolorはInvertMatrix, ContrastMatrix, SaturationMatrix, BrightnessMatrix, HueMatrixのみサポートしています。それ以外は無視されます。


 任意のプロパティーをエディターに追加する方法
================

 ActionEditor_config.rpy を編集します。

 共通の設定項目として以下に追加したいプロパティー名を加えます。:

 * `props_set`: ActionEditor上でプロパティーが表示される位置を指定します。
 * `sort_order_list`: クリップボードに出力されるプロパティーの順番を指定します。
 * `transform_props` または `camera_props`: プロパティー名を追加してください。前者は画像に、後者はカメラにプロパティーを追加します。
 * `transform_props` または `camera_props`: プロパティー名を追加してください。前者は画像に、後者はカメラにプロパティーを追加します。
 * `property_default_value`: プロパティーのデフォルト値を設定してください。
 
 さらに追加したいプロパティーの型に応じて設定します。

 整数または浮動小数の場合、必要なら以下に追加したいプロパティー名を加えます。:

 * `force_wide_range`: 値が浮動小数でも整数と同じ幅で値を調整できます。
 * `force_narrow_range`: 値が整数でも浮動小数と同じ幅で値を調整できます。
 * `force_plus`: 常に値が正の数となります。
 * `force_float`: 常に値が浮動小数となります。

 真偽値の場合、以下に追加したいプロパティー名を加えます。:

 * `boolean_props`

 他の型の場合、以下に追加したいプロパティー名を加えます。:

 * `any_props` 

 `any_props` はすべての型を受け入れます。使用するなら `check_any_props` か `menu_props`と併用すると安全です。

 * `check_any_props`

 エラーチェックを設定します。プロパティー名とチェック関数を対応させる辞書です。
 関数はプロパティーの値を引数に実行され、結果がTrueならその値を入力し、Falseならエラーメッセージを表示します。 例:

    any_props = {"blend"}
    #"blend"プロパティーの入力を(None, "normal", "add", "multiply", "min", "max")に限定する
    check_any_props = {"blend":lambda v: v in (None, "normal", "add", "multiply", "min", "max")}

 * `menu_props`

 `any_props` の変更を直接入力ではなく選択制にします。 例:

    any_props = {"blend"}
    #"blend"プロパティー(None, "normal", "add", "multiply", "min", "max")からの選択制にする
    menu_props = {"blend":[None] + [key for key in config.gl_blend_func]}

 tileとpanのような排他的なプロパティーは `exclusive` にも登録してください。例:

    exclusive = (
            ({"xpos", "ypos"}, {"xalignaround", "yalignaround", "radius", "angle"}), 
            ({"xtile", "ytile"}, {"xpan", "ypan"}), 
        )


 プロパティーグループ
================

 値がタプルであるプロパティーは props_groups でプロパティー名をキーに、
 各要素名を値にして登録すれば個別に編集できます。例:

    props_groups = {
        "alignaround":["xalignaround", "yalignaround"], 
        "matrixanchor":["matrixanchorX", "matrixanchorY"], 
        "crop":["cropX", "cropY", "cropW", "cropH"], 
        "focusing":["focusing", "dof"], 
    }


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


 Matrix
================

 デフォルトのマトリックスと順番はそれぞれ以下のようになっています。

    matrixtransform: ScaleMatrix*OffsetMatrix*RotateMatrix*OffsetMatrix*OffsetMatrix
    matrixcolors: InvertMatrix*ContrastMatrix*SaturationMatrix*BrightnessMatrix*HueMatrix

 マトリックスの組み合わと順番、デフォルト値はActionEditor_config.rpyの以下の変数で変更できます。

    default_matrixtransform = [
        ("matrixtransform_1_1_scaleX", 1.),  ("matrixtransform_1_2_scaleY", 1.),  ("matrixtransform_1_3_scaleZ", 1.),
        ("matrixtransform_2_1_offsetX", 0.), ("matrixtransform_2_2_offsetY", 0.), ("matrixtransform_2_3_offsetZ", 0.),
        ("matrixtransform_3_1_rotateX", 0.), ("matrixtransform_3_2_rotateY", 0.), ("matrixtransform_3_3_rotateZ", 0.),
        ("matrixtransform_4_1_offsetX", 0.), ("matrixtransform_4_2_offsetY", 0.), ("matrixtransform_4_3_offsetZ", 0.),
        ("matrixtransform_5_1_offsetX", 0.), ("matrixtransform_5_2_offsetY", 0.), ("matrixtransform_5_3_offsetZ", 0.),
    ]
    default_matrixcolor = [
        ("matrixcolor_1_1_invert", 0.), 
        ("matrixcolor_2_1_contrast", 1.), 
        ("matrixcolor_3_1_saturate", 1.),
        ("matrixcolor_4_1_bright", 0.),
        ("matrixcolor_5_1_hue", 0.), 
    ]


 文字サイズ
================
 
 new_action_editor_text スタイルから全てのテキストのスタイルを変更できます。

    init:
        style new_action_editor_text:
            size 10


 よくあるトラブル
================
 レイアウトが崩れる

 ActionEditorではタグ名が長過ぎる、フォントサイズが大きすぎる場合はレイアウトが崩れます。
 それらしい症状が発生した場合は上記の方法でフォントサイズを調整してください。

 次のエラーが発生する

 NameError: name '_open_image_viewer' is not defined

 旧版ActionEditorのファイルがあるゲームに本ActionEditor3のスクリプトファイルをコピーした場合に発生します。旧版とは互換性がないため、以前のActionEditorにあったファイルとスクリプト中で追加関数を使用していればそちらも削除してから、本ActionEditor3のファイルをコピーしてください。

 既知の問題
================

 アニメーションするat 節を使用したcamera, displayableは正常に表示できない

 Movie Displayable, アニメーションするDisplayableは正常に表示できない

 注意
================

 ActionEditorから出力されるクリップボードデータはActionEditorが開かれた状態からの差分として出力され、その次の行への貼り付けを意図しています。このため既存のshowステートメントを上書きするように貼り付けると正常に表示されない場合があります。
