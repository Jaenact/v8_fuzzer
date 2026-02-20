# V8 파이프라인 타겟팅 가이드 (Ignition/Sparkplug/Maglev/TurboFan)

Gemini에서 정리한 V8 내부 구조 포인트를 실제 퍼저 옵션으로 연결한 운영 노트입니다.

## 1) Tier별 실행 프로파일

현재 퍼저는 `--primary-profile`, `--secondary-profile`로 tier 성향을 빠르게 바꿀 수 있습니다.

- `ignition`: `--jitless`
- `sparkplug`: `--sparkplug --no-maglev --no-turbofan`
- `maglev`: `--maglev --no-turbofan`
- `turbofan`: `--turbofan`
- `stress`: `--stress-opt --always-turbofan`

## 2) Differential 전략 예시

```bash
python3 main.py \
  --d8-path /path/to/d8 \
  --primary-profile sparkplug \
  --secondary-d8-path /path/to/d8 \
  --secondary-profile maglev \
  --iterations 5000
```

또는,

```bash
python3 main.py \
  --d8-path /path/to/d8_stable \
  --primary-profile turbofan \
  --secondary-d8-path /path/to/d8_head \
  --secondary-profile stress \
  --iterations 5000
```

## 3) Turbolizer 연계 분석

crash 시 TurboFan trace를 남기려면:

```bash
python3 main.py \
  --d8-path /path/to/d8 \
  --primary-profile turbofan \
  --trace-turbo-on-crash \
  --iterations 5000
```

산출물은 `.fuzz-work/traces/trace_xxxxxx/` 아래에 저장됩니다.
해당 trace는 Turbolizer에서 단계별 IR 변환 분석에 사용 가능합니다.

## 4) 왜 중요한가

- Speculative optimization + deopt 경계는 대표적인 type confusion/OOB 발생 지점
- Tier별 동작 차이는 differential oracle 품질을 높임
- trace 확보는 root-cause 분석 시간을 크게 줄임
