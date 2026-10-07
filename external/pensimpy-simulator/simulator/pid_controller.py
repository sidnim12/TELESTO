"""PID controller in incremental form.

Equivalent to PIDSimple3.m.
"""


def pid_simple3(uk1, ek, ek1, yk, yk1, yk2, u_min, u_max, Kp, Ti, Td, h):
    """Simple PID controller in incremental form.

    The derivative component is applied only to the output.
    Controller checks for control signal saturation.

    u_k = u_{k-1} + Kp * [e_k - e_{k-1} + e_k*h/Ti + Td/h*(y_k - 2*y_{k-1} + y_{k-2})]

    Parameters:
        uk1: Previous control input.
        ek: Current error.
        ek1: Previous error.
        yk: Current process variable.
        yk1: Previous process variable.
        yk2: Previous-previous process variable.
        u_min: Minimum control signal.
        u_max: Maximum control signal.
        Kp: Proportional gain.
        Ti: Integral time constant.
        Td: Derivative time constant.
        h: Sampling time.

    Returns:
        Saturated control signal.
    """
    # Proportional component
    P = ek - ek1

    # Integral component
    if Ti > 1e-7:
        I = ek * h / Ti
    else:
        I = 0.0

    # Derivative component
    if Td > 0.001:
        D = -Td / h * (yk - 2.0 * yk1 + yk2)
    else:
        D = 0.0

    # Compute and saturate the control signal
    u = uk1 + Kp * (P + I + D)
    u = max(u_min, min(u_max, u))

    return u