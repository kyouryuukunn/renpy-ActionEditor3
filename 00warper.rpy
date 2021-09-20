python early hide:

    @renpy.atl_warper
    def power_in2(x):
        if x >= 1.0:
            return 1.0
        return 1.0 - (1.0 - x)**2

    @renpy.atl_warper
    def power_out2(x):
        if x >= 1.0:
            return 1.0
        return x**2

    @renpy.atl_warper
    def power_in3(x):
        if x >= 1.0:
            return 1.0
        return 1.0 - (1.0 - x)**3

    @renpy.atl_warper
    def power_out3(x):
        if x >= 1.0:
            return 1.0
        return x**3

    @renpy.atl_warper
    def power_in4(x):
        if x >= 1.0:
            return 1.0
        return 1.0 - (1.0 - x)**4

    @renpy.atl_warper
    def power_out4(x):
        if x >= 1.0:
            return 1.0
        return x**4

    @renpy.atl_warper
    def power_in5(x):
        if x >= 1.0:
            return 1.0
        return 1.0 - (1.0 - x)**5

    @renpy.atl_warper
    def power_out5(x):
        if x >= 1.0:
            return 1.0
        return x**5

    @renpy.atl_warper
    def power_in6(x):
        if x >= 1.0:
            return 1.0
        return 1.0 - (1.0 - x)**6

    @renpy.atl_warper
    def power_out6(x):
        if x >= 1.0:
            return 1.0
        return x**6

    @renpy.atl_warper
    def spring1(x):
        from math import exp, cos
        rho = 5 # 減衰率
        mu  = 30# 角振動数
        return (1.0 - exp(-rho * x) * cos(mu * x)) / (1.0 - exp(-rho) * cos(mu))

    @renpy.atl_warper
    def spring2(x):
        from math import exp, cos
        rho = 5 # 減衰率
        mu  = 20# 角振動数
        return (1.0 - exp(-rho * x) * cos(mu * x)) / (1.0 - exp(-rho) * cos(mu))

    @renpy.atl_warper
    def spring3(x):
        from math import exp, cos
        rho = 5 # 減衰率
        mu  = 10# 角振動数
        return (1.0 - exp(-rho * x) * cos(mu * x)) / (1.0 - exp(-rho) * cos(mu))

    @renpy.atl_warper
    def bop_time_warp(x):
      return -23.0 * x**5 + 57.5 * x**4 - 55 * x**3 + 25 * x**2 - 3.5 * x

    @renpy.atl_warper
    def bop_in_time_warp(x):
      return -2.15 * x**2 + 3.15 * x

    @renpy.atl_warper
    def bop_out_time_warp(x):
      return 2.15 * x**2 - 1.15 * x

    @renpy.atl_warper
    def bop_to_time_warp(x):
      return -5 * x**5 + 5 * x**4 + x**2

    @renpy.atl_warper
    def to_bop_time_warp(x):
      return -5 * x**5 + 20 * x**4 - 30 * x**3 + 19 * x**2 - 3 * x

    @renpy.atl_warper
    def easeout2(x):
        if x >= 1.0:
            return 1.0
        import math
        return 1.0 - math.cos(x * math.pi / 2.0)

    @renpy.atl_warper
    def easein2(x):
        if x >= 1.0:
            return 1.0
        import math
        return math.cos((1.0 - x) * math.pi / 2.0)

    @renpy.atl_warper
    def ease2(x):
        if x >= 1.0:
            return 1.0
        import math
        return .5 - math.cos(math.pi * x) / 2.0
    @renpy.atl_warper
    def power_in_time_warp_real(x):
        if x >= 1.0:
            return 1.0
        return 1.0 - (1.0 - x)**6

    #互換性のために残しておく
    @renpy.atl_warper
    def power_out_time_warp_real(x):
        if x >= 1.0:
            return 1.0
        return 1.0 - (1.0 - x)**6

    @renpy.atl_warper
    def power_in_time_warp_real5(x):
        if x >= 1.0:
            return 1.0
        return 1.0 - (1.0 - x)**5

    @renpy.atl_warper
    def power_out_time_warp_real5(x):
        if x >= 1.0:
            return 1.0
        return x**5

    @renpy.atl_warper
    def loop_cos(x):
        from math import cos, pi
        if x >= 1.0:
            return 1.0
        return (-1*cos(x*2*pi)+1)/2
