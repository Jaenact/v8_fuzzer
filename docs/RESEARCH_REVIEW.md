# V8/JS Fuzzing 선행연구 분석과 개선 포인트

이 문서는 기존 퍼저/논문에서 반복적으로 검증된 전략을 현재 코드베이스에 매핑하고,
아직 비어있는 고가치 영역을 정리합니다.

## 1) 선행 접근 요약

- **Fuzzilli 계열**: IR 기반 생성 + coverage feedback + semantic mutation + crash minimization.
- **coverage-guided JS fuzzers**: 엔진 내부 edge/pc-guard를 사용해 입력 품질을 정량화.
- **differential fuzzing 연구**: 버전/플래그/엔진 간 의미 차이를 oracle로 사용.
- **JIT/GC 표적 연구**: warmup, shape transition, deopt 유도, GC interleaving으로 deep state 도달.

## 2) 현재 구현과 매핑

- 구현됨:
  - 엔진 특화 템플릿 생성
  - adaptive mutator weighting
  - energy-based corpus scheduling
  - differential execution artifact 저장
- 아직 부족:
  - 실제 edge coverage 연동
  - IR/AST 기반 semantic-preserving mutation
  - 재현 crash 자동 최소화(reducer)
  - phase-specific forcing(ignition/sparkplug/turbofan) 강도 제어

## 3) 이번 개선 반영

이번 커밋에서는 선행연구의 공통 필수 요소 중 하나인 **자동 최소화(reducer)** 를 추가했습니다.

- 크래시 발생 시 line-based delta debugging으로 빠르게 입력 축소
- 최소화된 재현 파일을 별도 저장하여 triage 부담 감소

## 4) 다음 우선순위 제안

1. d8 coverage/sancov adapter 추가 (가장 큰 효율 개선)
2. JS 파서 기반 AST mutation 도입 (유효 문법 보존)
3. reducer를 line+token 하이브리드로 확장
4. crash dedup를 signal+stack hash 기반으로 강화
