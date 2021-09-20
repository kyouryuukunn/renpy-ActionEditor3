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
 * the concept of depth of field
 * spline
 * expression
 * loading last action

 To install, copy all files in the camera directory to your game directory.
 Then enable it like below.
	camera:
        perspective True
        gl_depth True

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

 Image Viewer
================
 Showing defined images and filtering that by tag and atrribute.
 
 Press Shift+U to open Image Viewer and view all currently generated displayables.


 Ren'Py v7.4.5から追加された3Dステージ機能により、旧版にあった自作の3Dカメラ再現関数は不要になりました。
 3Dステージ対応のGUI上で設定できる演出エディター、画像ビューワー、さらに便利なワーパー関数を追加します。
 v7.4.5以前のバージョンでは旧版のActionEditorを使用してください。
 <https://github.com/kyouryuukunn/renpy-ActionEditor>

 3Dカメラの再現を自作スクリプトから3Dステージに切り替えたことにより、旧版にあった最後のアクションを読み込む機能、スプライン、エクスプレッション、被写界深度の概念はなくなりました。
 使用したい場合はそれぞれ以下で代用してください。
 * スプライン ActionEditorで座標を確認後、手動でknotを使用してスプラインを指定してください <https://ja.renpy.org/doc/html/atl.html#interpolation-statement>
 * エクスプレッション function transform プロパティで代用してください。 <https://ja.renpy.org/doc/html/atl.html#function-statement>
 * 被写界深度 各画像に対し、個別にブラーをかけて代用してください。

 使用にはフォルダ内のファイルをgameフォルダにコピーし、ゲーム開始時に以下のようにしてカメラを有効化してください
	camera:
        perspective True
        gl_depth True


 演出エディター
================

 演出エディターでは変換プロパティーやカメラ、レイヤーの座標設定をGUI上で変更し、
 結果を確認できます。さらにそれらの値を時間軸に沿って変更可能なので、スクリプト
 を変更するたびに、リロードで結果を確認する従来の方法より遥かに短時間で動的演出
 を作成可能です。設定した値はクリップボードに送られ、スクリプトに貼り付けられま
 す。

 config.developer が True なら、Shift+Pで演出エディターが起動します。
 
 演出エディターでは以下の機能が利用可能です。:
 
 * 各画像の変換プロパティーやカメラ、レイヤー座標を直接入力またはバーの操作により変更
 * 数値を右クリックでリセット
 * カメラアイコンのドラッグまたはマウスホイール、キーボード(hjkl,HJKL)によるカメラ移動
 * 動画編集ソフトの様にキーフレームを設定して時間軸にそった演出を作成
 * 作成した演出のコードをクリップボードに送る(v6.99以上, Windows限定)

   camera_config.rpyで細かい挙動を調整できます。
   

 画像ビューワー
================
 定義された画像を画像タグ、属性から縛り込んで表示します。

 config.developer が True なら、Shift+Uで起動します。

