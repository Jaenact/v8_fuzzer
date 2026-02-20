from __future__ import annotations

import random

TEMPLATES = [
    """
function f(a) {
  let x = a | 0;
  for (let i = 0; i < __loop_n__; i++) {
    x = (x + i) ^ __const_a__;
  }
  return x;
}
for (let i = 0; i < __warmup_n__; i++) f(i);
f(__call_n__);
""",
    """
let arr = new Uint8Array(__arr_size__);
for (let i = 0; i < arr.length; i++) arr[i] = (i * __mul__) & 0xff;
function g(o) {
  o.p = __p_val__;
  delete o.p;
  o.q = __q_val__;
  return arr[__idx__] + (o.q | 0);
}
let obj = {};
for (let i = 0; i < __warmup_n__; i++) g(obj);
g(obj);
""",
    """
function h(v) {
  let a = [1.1, 2.2, 3.3, v];
  a.length = __arr_len__;
  return a[__idx__] ?? 0;
}
for (let i = 0; i < __warmup_n__; i++) h(i + 0.5);
h(__call_n__);
""",
]


def generate_program(rng: random.Random) -> str:
    template = rng.choice(TEMPLATES)
    values = {
        "__loop_n__": rng.randint(5, 80),
        "__const_a__": rng.randint(0, 2**16),
        "__warmup_n__": rng.randint(10, 200),
        "__call_n__": rng.randint(0, 2**10),
        "__arr_size__": rng.randint(8, 1024),
        "__mul__": rng.randint(1, 31),
        "__p_val__": rng.randint(-(2**16), 2**16),
        "__q_val__": rng.randint(-(2**16), 2**16),
        "__idx__": rng.randint(0, 7),
        "__arr_len__": rng.randint(0, 8),
    }
    for token, val in values.items():
        template = template.replace(token, str(val))
    return template
