 youtube sample
<https://www.youtube.com/watch?v=VMMBj4-7k_Q>
<https://www.youtube.com/watch?v=lhA8Ib3iKE8>

lemma forum
<https://lemmasoft.renai.us/forums/viewtopic.php?f=8&t=29778>

 日本語マニュアルはドキュメント後半にあります。

 This script adds the ability to simulate a 3D camera within Ren'Py, along with an
 in-game Action Editor and Image Viewer GUI to assist in animating the camera.
 To install, copy all files in the camera directory to your game directory.

 Ren'Py <http://www.renpy.org/>

 This is available in v7.4.5 later.
 To use in older version, use old version ActionEditor.
 <https://github.com/kyouryuukunn/renpy-ActionEditor>

 In current version ActionEditor, below functions are removed.
 * spline
 * expression
 * loading last action

 To install, copy all files in the camera directory to your game directory.
 Then enable it like below.
	camera:
        perspective True

 Action Editor
================

 This allows you to adjusts coordinates of the  camera and transform properties
 of images in real-time with a GUI. It can then generate a script based on these changes and
 place it on the clipboard for later pasting into Ren'Py scripts.

 When `config.developer` is True, pressing action_editor (by default,
 "shift+P") will open the Action editor.
 
 The Action Editor has the following features:
 
  * View and adjust the transform properties of images, camera coordinates, and 3D layer depth with bars
  * View and adjust the x and y coordinates of the camera with a mouse-positionable camera
  * Adjust the z coordinate of the camera with the mouse wheel.
  * Adjust the x,y coordinate of the camera with the keyboard(hjkl, HJKL).
  * Alternatively, each value can be adjusted with the keyboard without going back to the original script.
  * Add, delete, and edit keyframes on a timeline.
  * After setting up a scene with the desired look and animations, the Action
    Editor will generate a script and place it on your clipboard for pasting
    into your Ren'Py scripts. (v6.99 and later only)
  * Introducing the concept of depth of field and allow to adjust focus position and dof.
  * Showing and replacing, hiding image with transition(use None for image name to hide image)
  * There is the option for hiding window during the ATL animation in clipboard data.

 some config variables is availabe in ActionEditor_config.rpy

 Note
 * blur transform property of each images are used for simulating camera blur in function transform prperty,
 so blur transform properties of each images aren't availabe when focusing is enabled.
 Set function property to None when you want to disable camera blur for already shownd images.
 * Can't get correct value If any other transform_matrix than below Matrixes are used.
    OffsetMatrix * RotateMatrix
    OffsetMatrix
    RotateMatrix
 * Can't get colormatrix property.

 Image Viewer
================
 Showing defined images and filtering that by tag and atrribute.
 The completion feature is availabe by tab
 
 Press Shift+U to open Image Viewer and view all currently generated displayables.








 本ライブラリでは3Dステージ対応のGUI上で設定できる演出エディター、画像ビューワー、さらに便利なワーパー関数を追加します。
 Ren'Py v7.4.5から追加された3Dステージ機能により、旧版にあった自作の3Dカメラ再現関数は不要になりました。
 v7.4.5以前のバージョンでは旧版のActionEditorを使用してください。
 <https://github.com/kyouryuukunn/renpy-ActionEditor>

 3Dカメラの再現を自作スクリプトから3Dステージに切り替えたことにより、旧版にあった最後のアクションを読み込む機能、スプライン、エクスプレッション機能はなくなりました。
 使用したい場合はそれぞれ以下で代用してください。
 * スプライン ActionEditorで座標を確認後、手動でknotを使用してスプラインを指定してください <https://ja.renpy.org/doc/html/atl.html#interpolation-statement>
 * エクスプレッション function transform プロパティで代用してください。 <https://ja.renpy.org/doc/html/atl.html#function-statement>

 使用にはフォルダ内のファイルをgameフォルダにコピーし、ゲーム開始時に以下のようにしてカメラを有効化してください
	camera:
        perspective True

 演出エディター(Action Editor)
================

 演出エディターでは変換プロパティーやカメラ、レイヤーの座標設定をGUI上で変更し、
 結果を確認できます。さらにそれらの値を時間軸に沿って変更可能なので、スクリプト
 を変更するたびに、リロードで結果を確認する従来の方法より遥かに短時間で動的演出
 を作成可能です。設定した値はクリップボードに送られ、スクリプトに貼り付けられま
 す。
 さらにfocusingを有効にすると被写界深度の概念を導入し、カメラと画像との距離で
 ブラーをかけられます。

 config.developer が True なら、Shift+Pで演出エディターが起動します。
 
 演出エディターでは以下の機能が利用可能です。:
 
 * 各画像の変換プロパティーやカメラ、レイヤー座標を直接入力またはバーの操作により変更
 * 数値を右クリックでリセット
 * カメラアイコンのドラッグまたはマウスホイール、キーボード(hjkl,HJKL)によるカメラ移動
 * 動画編集ソフトの様にキーフレームを設定して時間軸にそった演出を作成
 * 作成した演出のコードをクリップボードに送る(v6.99以上, Windows限定)
 * 被写界深度の概念を導入し、フォーカス位置と被写界深度を操作可能
 * トランジションを伴う画像の表示、置き換え、非表示(画像を非表示するには画像名にNoneを入力してください)
 * クリップボードへの出力データでアニメーション中はウィンドウを非表示するようにするオプション

   ActionEditor_config.rpyで細かい挙動を調整できます。

 注意
 focusingを有効化している間、function transform プロパティーで利用しているため各画像のblurは利用できなくなります
 funtion transform propertyにcamera_blurを使用して表示している画像にはblurをかけられません。既に表示している画像の
 focusingを無効にしたい場合はfunctionプロパティーをNoneにしてください
 matrixtransformプロパティーの値をエディターで読み込むことは困難なため現在以下の順番、組み合わのみに対応しています。
    OffsetMatrix * RotateMatrix
    OffsetMatrix
    RotateMatrix
 colormatrixプロパティーは現在の値をエディターでは読み込めません。
   

 画像ビューワー
================
 定義された画像を画像タグ、属性から縛り込んで表示します。
 タブでの補間も可能です。

 config.developer が True なら、Shift+Uで起動します。

