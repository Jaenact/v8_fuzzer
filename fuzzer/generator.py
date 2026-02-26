from __future__ import annotations

import random

TEMPLATES = [
    """
function hot(o) {
  let s = 0;
  for (let i = 0; i < __loop_n__; i++) {
    o.x = (i + __const_a__) | 0;
    s += (o.x ^ i) & 0xff;
  }
  return s;
}
let o = {x: 1, y: 2};
for (let i = 0; i < __warmup_n__; i++) hot(o);
%OptimizeFunctionOnNextCall(hot);
hot(o);
""",
    """
function midtier(a) {
  let v = a;
  for (let i = 0; i < __loop_n__; i++) {
    if ((i & 1) === 0) {
      v = (v + i) | 0;
    } else {
      v = {x: v, y: i};
      v = v.x | 0;
    }
  }
  return v;
}
for (let i = 0; i < __warmup_n__; i++) midtier(i | 0);
midtier(__call_n__);
""",
    """
const buf = new ArrayBuffer(__arr_size__);
const dv = new DataView(buf);
for (let i = 0; i < __arr_size__; i += 4) {
  dv.setInt32(i, (i * __mul__) | 0, true);
}
function ready(i) {
  return dv.getInt32((i * 4) % __arr_size__, true);
}
for (let i = 0; i < __warmup_n__; i++) ready(i);
ready(__call_n__);
""",
    """
let target = {a: 1, b: 2};
let p = new Proxy(target, {
  get(obj, key) {
    if (key === 'a') return __p_val__;
    return Reflect.get(obj, key);
  }
});
function g(x) {
  target.c = x;
  delete target.c;
  return p.a + (target.b | 0);
}
for (let i = 0; i < __warmup_n__; i++) g(i);
g(__q_val__);
""",
    """
let mem = new WebAssembly.Memory({initial:1});
let u8 = new Uint8Array(mem.buffer);
for (let i = 0; i < __arr_len__; i++) u8[i] = i & 255;
function h() {
  gc();
  return u8[__idx__ % u8.length];
}
for (let i = 0; i < __warmup_n__; i++) h();
h();
""",
]


def generate_program(rng: random.Random) -> str:
    template = rng.choice(TEMPLATES)
    values = {
        "__loop_n__": rng.randint(20, 180),
        "__const_a__": rng.randint(0, 2**16),
        "__warmup_n__": rng.randint(50, 800),
        "__call_n__": rng.randint(0, 2**10),
        "__arr_size__": rng.choice([64, 128, 256, 512, 1024, 2048]),
        "__mul__": rng.randint(1, 31),
        "__p_val__": rng.randint(-(2**20), 2**20),
        "__q_val__": rng.randint(-(2**20), 2**20),
        "__idx__": rng.randint(0, 63),
        "__arr_len__": rng.randint(8, 128),
    }
    for token, val in values.items():
        template = template.replace(token, str(val))
    return template
