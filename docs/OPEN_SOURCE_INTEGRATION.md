# 오픈소스 퍼저 아이디어 반영 현황

이 문서는 공개 퍼저들의 실무 패턴을 현재 구현에 어떻게 반영했는지 설명합니다.

## 참고한 공개 퍼저 패턴

- AFL 계열: corpus seed import, deterministic+random mutation, crash dedup/triage
- Fuzzilli 계열: 엔진 특화 생성 + feedback 기반 스케줄링 + reducer
- jsfunfuzz 계열: JIT/GC 경계를 자극하는 warmup + shape 변화

## 이번 코드 반영

1. **Seed corpus import 지원**
   - `--import-seeds-dir`, `--import-seeds-limit`
   - 공개 JS corpus를 초기 시드로 투입 가능
2. **Corpus dedup 강화**
   - seed content SHA-256 기반 중복 삽입 방지
3. **Crash dedup 안정화**
   - Python process-randomized `hash()` 대신 stable SHA-256 사용
4. **Mutator 관측성 강화**
   - `stats.json`에 mutator별 tries/rewards/score 기록

## 바로 쓸 수 있는 시드 소스 예시

- V8 mjsunit 테스트 중 JS 샘플
- Web platform tests의 JS 케이스
- 기존 fuzz artifact 중 non-crashing interesting sample

주의: 라이선스/정책에 맞는 데이터만 사용하세요.
