# V8 Fuzzer (Research-Driven)

이 프로젝트는 **실제 취약점 제보 가능한 수준**을 목표로 V8 특화 퍼징을 구현합니다.
MVP 수준 랜덤 퍼저를 넘어서, corpus energy scheduling / mutator 학습 / differential 실행까지 포함합니다.

## 핵심 기능 (현재)

- V8 표면 특화 템플릿 생성기
  - 최적화(%OptimizeFunctionOnNextCall), Proxy, DataView, WebAssembly.Memory, GC 경계
- 고급 mutation 전략
  - 문장 삽입 / 블록 복제 / 숫자 리터럴 교란 / seed splice
- Corpus metadata + energy 기반 seed 선택
  - novelty/crash 히스토리로 seed 우선순위 동적 조정
- Differential fuzzing 모드
  - primary vs secondary d8 (혹은 서로 다른 flag 셋) 결과 비교
- Crash/Diff artifact 저장
  - `.js` 재현 입력 + 로그/JSON 메타 저장

## 빠른 시작

```bash
python3 main.py \
  --d8-path /path/to/d8 \
  --iterations 10000 \
  --timeout 1.0 \
  --workdir ./.fuzz-work
```

### Differential 모드

```bash
python3 main.py \
  --d8-path /path/to/d8_stable \
  --secondary-d8-path /path/to/d8_head \
  --primary-flags "--no-lazy" \
  --secondary-flags "--stress-opt --no-lazy" \
  --iterations 10000
```

## 출력 디렉터리

- `.fuzz-work/corpus/` : seed + metadata
- `.fuzz-work/crashes/` : crash 재현 입력/로그
- `.fuzz-work/differentials/` : 실행 결과 불일치 샘플
- `.fuzz-work/stats.json` : 누적 통계

## 다음 단계 (권장)

1. sancov/edge bitmap 연동으로 진짜 coverage-guided selection
2. AST-level mutation + reducer 통합
3. crash dedup 고도화(stack hash/signal 기반)
4. distributed worker 모델로 병렬화
