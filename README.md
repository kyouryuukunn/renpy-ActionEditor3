 youtube sample
<https://www.youtube.com/watch?v=VMMBj4-7k_Q>
<https://www.youtube.com/watch?v=lhA8Ib3iKE8>

lemma forum
<https://lemmasoft.renai.us/forums/viewtopic.php?f=8&t=29778>

 日本語マニュアルはドキュメント後半にあります。

 This script adds the ability to adjust and view transform properties of images
 and camera by in-game Action Editor and Image Viewer GUI.

 Ren'Py <http://www.renpy.org/>

 This is available in v7.4.5 later.
 To use in older version, use old version ActionEditor.
 <https://github.com/kyouryuukunn/renpy-ActionEditor>

 In current version ActionEditor, below functions are removed.
 * expression
 * loading last action

 To install, copy all files in the camera directory into your game directory.

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
 * Skipping animations may not work when those include the tags which are already shown and have loop animations.

 Image Viewer
================
 Showing defined images and filtering that by tag and atrribute.
 The completion feature is availabe by tab
 
 Press Shift+U to open Image Viewer and view all currently generated displayables.








 本ライブラリでは3Dステージ対応のGUI上で設定できる演出エディター、画像ビューワー、さらに便利なワーパー関数を追加します。
 Ren'Py v7.4.5から追加された3Dステージ機能により、旧版にあった自作の3Dカメラ再現関数は不要になりました。
 v7.4.5以前のバージョンでは旧版のActionEditorを使用してください。
 <https://github.com/kyouryuukunn/renpy-ActionEditor>

 3Dカメラの再現を自作スクリプトから3Dステージに切り替えたことにより、旧版にあった最後のアクションを読み込む機能、エクスプレッション機能はなくなりました。
 使用したい場合はそれぞれ以下で代用してください。
 * エクスプレッション function transform プロパティで代用してください。 <https://ja.renpy.org/doc/html/atl.html#function-statement>

 使用にはフォルダ内のファイルをgameフォルダにコピーしてください。

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
 *funtion transform propertyにcamera_blurを使用して表示している画像にはblurをかけられません。既に表示している画像の
 focusingを無効にしたい場合はfunctionプロパティーをいったんNoneにしてください
 *matrixtransformプロパティーの値をエディターで読み込むことは困難なため現在以下の順番、組み合わせのみに対応しています。
    OffsetMatrix * RotateMatrix
    OffsetMatrix
    RotateMatrix
 *colormatrixプロパティーは現在の値をエディターでは読み込めません。
 *アニメーションのスキップはアニメーション終了後と同じ画像を表示してスキップを可能にしています。アニメーション開始前から同じタグの画像がすでに表示されており、かつそのタグのアニメーションにループが含まれている場合は正常に動作しません。
 参考リンク
 http://akakyouryuu.com/renpy/renpy%e3%81%aeatl%e3%82%a2%e3%83%8b%e3%83%a1%e3%83%bc%e3%82%b7%e3%83%a7%e3%83%b3%e3%82%92%e3%82%af%e3%83%aa%e3%83%83%e3%82%af%e3%81%a7%e3%82%b9%e3%82%ad%e3%83%83%e3%83%97%e3%81%a7%e3%81%8d%e3%82%8b/
   

 画像ビューワー
================
 定義された画像を画像タグ、属性から縛り込んで表示します。
 タブでの補間も可能です。

 config.developer が True なら、Shift+Uで起動します。

