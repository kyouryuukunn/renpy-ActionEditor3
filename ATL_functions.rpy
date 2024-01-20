# ATL functions
# This File adds some utility function for ATL function.
# このファイルはATLのfunctionステートメントで使用できるユーソリティー関数を追加します。
#
#class mfn(func1, func2, func3, ...)
#   This class takes functions which are called with arguments tran, st, at.
#   This is intended to be used to use multiple functions for function statement in ATL.
#   このクラスは複数の関数を引数に取り、それらは tran, st, atを引数に呼び出されます。
#   これはATLのfunctionステートメントで複数の関数を使用するために使用できます。
#    example:
#        show test:
#            function mfn(func1, func2)
#
#class atl_sin(property, peak, hz, start=None, end=None, damped=False, damped_warper='ease')
#    This change the property value with a sine wave.
#    プロパティーの値を正弦波で変更します。
#    property:      property name string
#                   プロパティーの名前の文字列です。
#    peak:          peak value
#                   振幅
#    hz:            hz of the wave
#                   振動数
#    start:         This function starts after `start` seconds
#                   この関数は `start` 秒後に開始します。
#    end:           This function ends after `end` seconds
#                   この関数は `end` 秒後に終了します。
#    damped:        If True and `end` is not None, this wave
#                   is damped wave. Wave stops in `end` seconds
#                   True かつ `end` が設定されていれば減衰波になり、
#                   `end` 秒後に振動が止まります。
#    damped_warper: This is warper which is used for damp.
#                   減衰に使用されるワーパーです。
#
#class atl_cos(property, peak, hz, start=None, end=None, damped=False, damped_warper='ease')
#    This is cos version of atl_sin.
#    atl_sinの余弦波バージョンです。

#class atl_wiggle(property, max, deviation, cycle, fast_forward=1, knot_num_per_sec=1, start=None, end=None, damped=False, damped_warper='ease'):
#    Random knots are created according to a Gaussian distribution, and sprite interpolation is performed between knots to reproduce random vibration.
#    ガウス分布に従ったランダムな中間点を作成し、中間点間をスプライト補間してランダム振動を再現します。
#    property:         property name string
#                      プロパティーの名前の文字列です。
#    max:              The valu is limited in this value.
#                      設定される値はこの値を越えません。
#    deviation:        the standard deviation
#                      標準偏差です。
#    cycle:            The number of seconds of the vibration cycle. The value set for each of these seconds is 0.
#                      It is important for this vibration looks random to set sufficiently big value 
#                      振動周期の秒数です。この秒数ごとに設定される値は0となります。振動をランダムに見せるには十分長い必要があります。
#    fast_forward:     The vibration will be `fast_forward` times faster.
#                      振動が `fast_forward` 倍早まわしになります。
#    knot_num_per_sec: The number of knot per second. The more knot, the finer the amplitude.
#                      1秒あたりの中間点の数です。中間点が増えるほど振幅が細かくなります。
#    start:            This function starts after `start` seconds
#                      この関数は `start` 秒後に開始します。
#    end:              This function ends after `end` seconds
#                      この関数は `end` 秒後に終了します。
#    damped:           If True and `end` is not None, this wave
#                      is damped wave. Wave stops in `end` seconds
#                      True かつ `end` が設定されていれば減衰波になり、
#                      `end` 秒後に振動が止まります。
#    damped_warper:    This is warper which is used for damp.
#                      減衰に使用されるワーパーです。
#
#    For example, This reproduces camera shake.
#    例: 手ぶれを再現します。
#    camera:   
#        function mfn(atl_wiggle("yoffset", max=20, deviation=40, cycle=10), atl_wiggle("xoffset", max=20, deviation=40, cycle=10))
#
#    For example, This reproduces the 10 seconds earthquake
#    例: 10秒間の地震を再現します。
#    camera:   
#        function mfn(atl_wiggle("yoffset", max=20, deviation=40, cycle=100, fast_forward=10, end=10, damped=True, damped_warper="ease"), atl_wiggle("xoffset", max=20, deviation=40, cycle=100, fast_forward=10, end=10, damped=True, damped_warper="ease"))
#
#
#def atl_swiggle(deviation, fast_forward=1, start=None, end=None, damped=False, damped_warper='ease', property=("xoffset", "yoffset")):
#    This is the wrapper for atl_wiggle.
#    これはatl_wiggleのラッパーです。
#    Below two code is mostly equivalent.
#    次の2つのコードはほぼ同じ動作をします。
#
#    camera:   
#        function mfn(atl_wiggle("yoffset", max=20, deviation=40, cycle=10), atl_wiggle("xoffset", max=20, deviation=40, cycle=10))
#    camera:   
#        function atl_swiggle(deviation=40)

init python in _viewers:
    in_editor = False

init python:
    class mfn(object):
        def __init__(self, *args):
            self.fns = list(args)

        def __call__(self, tran, st, at):
            min_fr = None
            for i in reversed(range(len(self.fns))):
                fr = self.fns[i](tran, st, at)
                if fr is not None and (min_fr is None or fr < min_fr):
                    min_fr = fr
                elif fr is None and not _viewers.in_editor:
                    del self.fns[i]
            return min_fr


    class generate_atl_func(object):
        def __init__(self, property, start=None, end=None, check_type=True):
            self.property = property
            self.start = start
            self.end = end
            self.check_type = check_type

        def __call__(self, tran, st, at):
            if self.end is not None:
                if st > self.end:
                    return None
            if self.start is not None:
                st -= self.start
                if st < 0:
                    return 0
            cur_prop = self.get_cur_prop(tran)
            fr = self.function(tran, st, at)
            if self.check_type and isinstance(cur_prop, int):
                setattr(tran, self.property, int(getattr(tran, self.property)))
            return fr

        def get_cur_prop(self, tran):
            cur_prop = getattr(tran, self.property)
            if cur_prop is None:
                cur_prop = getattr(tran, "inherited_"+self.property)
            return cur_prop


    class atl_sin(generate_atl_func):
        def __init__(self, property, peak, hz, start=None, end=None, damped=False, damped_warper='ease'):
            super(atl_sin, self).__init__(property, start, end)
            self.peak = peak
            self.hz = hz
            self.damped = damped
            self.damped_warper = damped_warper

        def function(self, tran, st, at):
            from math import sin, pi
            damp = 1
            if self.damped and self.end is not None:
                damp = renpy.atl.warpers[self.damped_warper]((self.end - st) / self.end)
            offset = damp * self.peak * sin(st*2*pi*self.hz)
            setattr(tran, self.property, offset)
            return 0


    class atl_cos(generate_atl_func):
        def __init__(self, property, peak, hz, start=None, end=None, damped=False, damped_warper='ease'):
            super(atl_cos, self).__init__(property, start, end)
            self.peak = peak
            self.hz = hz
            self.damped = damped
            self.damped_warper = damped_warper

        def function(self, tran, st, at):
            from math import cos, pi
            damp = 1
            if self.damped and self.end is not None:
                damp = renpy.atl.warpers[self.damped_warper]((self.end - st) / self.end)
            offset = damp * self.peak * cos(st*2*pi*self.hz)
            setattr(tran, self.property, offset)
            return 0


    class atl_wiggle(generate_atl_func):
        def __init__(self, property, max, deviation, cycle, fast_forward=1, knot_num_per_sec=1, start=None, end=None, damped=False, damped_warper='ease'):
            super(atl_wiggle, self).__init__(property, start, end)
            from random import gauss

            start_point = 0
            goal_point = 0
            #予めランダムな値を生成しておく
            self.random_knot = [start_point]
            for i in range(0, int(cycle/knot_num_per_sec)):
                while True:
                    v = gauss(0, deviation)
                    if abs(v) <= max:
                        break
                self.random_knot.append(v)
            self.random_knot.append(goal_point)
            self.cycle = cycle
            self.fast_forward = fast_forward
            self.damped = damped
            self.damped_warper = damped_warper

        def function(self, tran, st, at):
            st *= self.fast_forward
            g = round((st % self.cycle), 3) / self.cycle
            damp = 1
            if self.damped and self.end is not None:
                damp = renpy.atl.warpers[self.damped_warper]((self.end - st / self.fast_forward) / self.end)

            if renpy.version_tuple[3] >= 24011600:
                interpolate_spline = renpy.atl.interpolate_spline(g, self.random_knot, renpy.atl.PROPERTIES[self.property])
            else:
                interpolate_spline = renpy.atl.interpolate_spline(g, self.random_knot)

            offset = damp * interpolate_spline
            setattr(tran, self.property, offset)
            return 0


    def atl_swiggle(deviation, fast_forward=1, start=None, end=None, damped=False, damped_warper='ease', property=("xoffset", "yoffset")):
        cycle = 20
        if not isinstance(property, tuple):
            property = tuple([property])
        args = []
        for p in property:
            args.append(atl_wiggle(p, max=deviation/2, deviation=deviation, cycle=cycle*fast_forward, fast_forward=fast_forward, start=start, end=end, damped=damped, damped_warper=damped_warper))
        return mfn(*args)
    
    
    # class atl_wiggle(generate_atl_func):
    #     def __init__(self, property, peak, hz, start=None, end=None):
    #         super(atl_wiggle, self).__init__(property, start, end)
    #         from random import random
    #         #予めランダムな値を生成しておく
    #         self.randoms = [(1+random(), 1+random()) for i in range(0, 100)]
    #         self.hz = hz
    #         self.peak = peak
    #
    #         self.octaves = 1
    #         self.ampMulti = .5
    #         self.time = 0
    #
    #     def function(self, tran, st, at):
    #         from math import sin, pi, ceil
    #         rx1, rx2 = self.randoms[int(ceil(st*self.hz)%100)]
    #         offset = rx1*self.peak*sin(2*pi*self.hz*st) + rx2*self.peak*self.ampMulti*sin(2*pi*self.hz*2*self.octaves*(st+self.time))
    #         setattr(tran, self.property, offset)
    #         return 0
