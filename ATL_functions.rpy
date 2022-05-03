#class mfn(func1, func2, func3, ...)
#   This class takes functions which are called with arguments tran, st, at.
#   This is intended to be used to use multiple functions for function statement in ATL.
#   このクラスは複数の関数を引数に取り、それらは tran, st, atを引数に呼び出されます。
#   これはATLのfunctionステートメントで複数の関数を使用するために使用できます。
#    example:
#        show test:
#            function mfn(func1, func2)

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
                elif fr is None:
                    del self.fns[i]
            return min_fr


    class sin_offset(object):
        def __init__(self, property, peak, hz, start=None, end=None):
            self.property = property
            self.peak = peak
            self.hz = hz
            self.start = start
            self.end = end

            self.last_offset = None

        def __call__(self, tran, st, at):
            from math import sin, pi
            if end is not None:
                if st > end:
                    return None
            if start is not None:
                st -= start
                if st < 0:
                    return 0
            cur_prop = getattr(tran, self.property)
            if cur_prop is None:
                cur_prop = getattr(tran, "inherited_" + self.property)
            if self.last_offset is not None and not _viewers.in_editor:
                cur_prop -= self.last_offset
            offset = self.peak * sin(st*2*pi*self.hz)
            if isinstance(cur_prop, int):
                offset = int(offset)
            setattr(tran, self.property, cur_prop + offset)
            self.last_offset = offset
            return 0


    class cos_offset(object):
        def __init__(self, property, peak, hz, start=None, end=None):
            self.property = property
            self.peak = peak
            self.hz = hz
            self.start = start
            self.end = end

            self.last_offset = None

        def __call__(self, tran, st, at):
            from math import cos, pi
            if end is not None:
                if st > end:
                    return None
            if start is not None:
                st -= start
                if st < 0:
                    return 0
            cur_prop = getattr(tran, self.property)
            if cur_prop is None:
                cur_prop = getattr(tran, "inherited_" + self.property)
            if self.last_offset is not None and not _viewers.in_editor:
                cur_prop -= self.last_offset
            offset = self.peak * cos(st*2*pi*self.hz)
            if isinstance(cur_prop, int):
                offset = int(offset)
            setattr(tran, self.property, cur_prop + offset)
            self.last_offset = offset
            return 0
