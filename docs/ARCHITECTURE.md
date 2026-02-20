# Architecture Notes for a Next-Gen V8 Fuzzer

## 1) Design Principles

- **Engine-aware fuzzing**: 단순 JS 랜덤 생성이 아니라 V8의 최적화/JIT/GC 경계를 노린다.
- **Feedback first**: 입력 품질은 관측 가능한 피드백(커버리지/행동 차이/크래시 신호)로 평가한다.
- **Hybrid strategy**: grammar 생성 + mutation + differential 비교를 결합한다.
- **Triage automation**: crash 재현성, 최소화, 중복 제거를 자동화한다.

## 2) Core Loop (MVP)

1. Seed 선택
2. 입력 생성/변이
3. `d8` 실행 (timeout/return code/출력 수집)
4. crash 여부 분류
5. novelty 판단 후 corpus 업데이트

## 3) V8-Focused Target Surfaces

- Hidden class transition / inline cache stability
- TypedArray + DataView boundary patterns
- Proxy / Reflect / dynamic property reconfiguration
- WebAssembly ↔ JS bridge (type confusion edge)
- Promise/microtask ordering with GC pressure
- Optimization directives (`%OptimizeFunctionOnNextCall` 등)

## 4) Near-Term Upgrades

- Coverage bitmap 연동(sancov/edge log)
- Multi-armed bandit 기반 mutator 선택
- AST-level mutation + semantic-preserving transforms
- Differential mode: stable vs experimental flags 비교
- Auto reducer: crash input 최소화

## 5) Long-Term Novel Ideas

- **Phase-targeted fuzzing**: Ignition → Sparkplug → TurboFan 전환 시점 유도
- **Constraint-guided generation**: 특정 최적화 패턴을 만족하는 코드 합성
- **State stitching**: 여러 실행 상태를 재조합해 rare state 도달
- **Heap-shape orchestration**: 객체 레이아웃을 의도적으로 조형

## 6) Operational Security / Disclosure

- 취약점 저장소 암호화/접근 통제
- 재현 스크립트 자동 생성
- 벤더 정책에 맞춘 타임라인 관리
