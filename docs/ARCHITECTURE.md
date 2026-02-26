# Architecture Notes for a Next-Gen V8 Fuzzer

## 1) Why this is beyond a toy fuzzer

기존 단순 랜덤 생성은 deep optimization state에 도달하기 어렵습니다.
이 구현은 아래 4축을 결합합니다.

1. **Engine-aware generation**: JIT/GC/Proxy/DataView/Wasm 경계 노림
2. **Adaptive mutation**: mutator별 reward를 누적해 좋은 전략을 더 자주 선택
3. **Energy-based corpus scheduling**: novelty/crash 기여 seed에 더 많은 실행 기회 부여
4. **Differential oracle**: 서로 다른 빌드/플래그의 의미적 불일치 포착

## 2) Execution Pipeline

1. seed 선택 (metadata energy 기반)
2. 생성/변이/스플라이스
3. primary 실행
4. crash 분류 + novelty 판정
5. optional secondary 실행 (diff 판정)
6. mutator reward 업데이트
7. artifacts + stats 저장

## 3) Target Surfaces

- Hidden class transition / IC invalidation
- DataView/TypedArray index + endian corner cases
- Proxy trap과 Reflect의 관찰 차이
- Wasm Memory + JS object interaction
- GC 타이밍과 optimized function 재호출 경계

## 4) Dedup and triage

- Crash: returncode + stderr prefix hash로 1차 dedup
- Differential: 양측 stdout/stderr/returncode/timed_out 비교
- 모든 interesting 입력은 재현 가능한 원본 JS로 보존

## 5) Upgrade hooks

- Coverage bitmap adapter (`result.coverage`) 슬롯 추가 예정
- Phase-aware forcing (Ignition/Sparkplug/TurboFan) mutator 확장 가능
- Reducer 연결 포인트: crash/diff artifact 후처리
