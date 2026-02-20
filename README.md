# V8 Fuzzer (Research-Driven)

이 저장소는 **V8 엔진 취약점 제보**를 목표로 하는 차세대 퍼저의 초기 구현체입니다.
기존 오픈소스/논문의 핵심 아이디어(coverage feedback, grammar 기반 생성, mutation, crash triage)를 조합하고,
V8 특화 영역(최적화 파이프라인, GC 경계, TypedArray/WebAssembly/JIT 상호작용)을 공략하도록 설계했습니다.

## 현재 상태

현재는 빠르게 반복 가능한 **MVP 퍼징 루프**를 구현했습니다.

- JavaScript 샘플 생성 (grammar-like 템플릿)
- corpus 관리 및 mutation
- `d8` 프로세스 실행/타임아웃 처리
- crash 입력 자동 저장
- 간단한 novelty(새로운 출력/실행결과 해시) 기반 corpus 확장

## 목표 아키텍처 (단계별)

1. **Stage 1 (현재)**: 단일 프로세스 퍼징 루프 + crash 수집
2. **Stage 2**: 커버리지(가능하면 sancov/edge profile) 기반 시드 선택
3. **Stage 3**: 타입 상태 추적 + JIT phase-aware 변이
4. **Stage 4**: differential fuzzing (d8 플래그/버전 간 비교)
5. **Stage 5**: 자동 최소화(minimization), dedup, 제보 패키지 자동화

세부 내용은 `docs/ARCHITECTURE.md` 참고.

## 빠른 시작

### 요구사항

- Python 3.11+
- V8 `d8` 바이너리 (직접 빌드하거나 배포 바이너리 사용)

### 실행

```bash
python3 main.py \
  --d8-path /path/to/d8 \
  --iterations 1000 \
  --timeout 1.0 \
  --workdir ./.fuzz-work
```

## 디렉터리

- `fuzzer/` : 퍼징 코어 로직
- `docs/` : 연구/설계 문서
- `tests/` : 단위 테스트

## 주의

- 이 코드는 보안 연구/책임있는 제보 목적입니다.
- 발견된 취약점은 공개 전에 벤더의 disclosure 정책을 준수하세요.
