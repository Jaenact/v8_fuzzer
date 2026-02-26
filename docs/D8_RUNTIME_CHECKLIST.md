# d8 설치 환경 기준 실제 운영 체크리스트

이 문서는 **d8가 이미 설치된 환경**에서 현재 퍼저를 실제로 돌릴 때 필요한 최소/권장 점검 순서를 제공합니다.

## 0) 사전 조건

- Python 3.11+
- `d8` 실행 가능 바이너리 (stable/head 2개면 differential 권장)
- 충분한 디스크 공간 (crash/diff artifact 누적)

---

## 1) 바이너리/환경 확인

```bash
which d8
python3 --version
```

### 합격 기준
- `which d8`가 절대경로를 출력
- Python 버전이 3.11 이상

---

## 2) 프로젝트 무결성 체크

```bash
python3 -m pytest -q
python3 -m compileall -q .
```

### 합격 기준
- 테스트 전부 통과
- compileall 오류 없음

---

## 3) 1차 스모크 런 (단일 d8)

```bash
python3 main.py \
  --d8-path "$(which d8)" \
  --iterations 300 \
  --timeout 1.0 \
  --workdir ./.fuzz-work-smoke \
  --seed 1337
```

### 합격 기준
- 프로세스 비정상 종료 없이 완료
- `.fuzz-work-smoke/stats.json` 생성
- `.fuzz-work-smoke/corpus/`에 seed 누적

확인:

```bash
cat ./.fuzz-work-smoke/stats.json
```

---

## 4) 크래시 최소화 경로 검증

```bash
python3 main.py \
  --d8-path "$(which d8)" \
  --iterations 500 \
  --timeout 1.0 \
  --workdir ./.fuzz-work-reducer \
  --minimize-crashes
```

### 합격 기준
- crash 발생 시 `crash_*.js`, `crash_*.log`, `crash_*.min.js`가 함께 생성
- min 파일이 원본보다 작거나 동일하며 재현성 유지

---

## 5) Differential 런 (권장)

`d8_stable`, `d8_head`가 모두 있을 때:

```bash
python3 main.py \
  --d8-path /path/to/d8_stable \
  --secondary-d8-path /path/to/d8_head \
  --primary-flags "--no-lazy" \
  --secondary-flags "--stress-opt --no-lazy" \
  --iterations 1000 \
  --timeout 1.0 \
  --workdir ./.fuzz-work-diff
```

### 합격 기준
- `.fuzz-work-diff/differentials/`에 `.js`, `.json` 쌍 저장
- stats의 `differentials` 카운터 증가

---

## 6) 장시간 런 운영 기준 (실전)

권장 시작점:

- Iterations: 50k ~ 200k
- Timeout: 0.5~2.0 (환경에 맞춰)
- Workdir: 날짜/실험ID 분리 (`.fuzz-runs/2026-02-20-exp01`)

모니터링 포인트:

- `stats.json`의 `corpus_add`, `crashes`, `differentials` 증가율
- crash dedup 품질(유사 stderr 과다 여부)
- 디스크 사용량 증가율

---

## 7) 실패 시 빠른 진단

1. `d8 binary not found`
   - `--d8-path`를 절대경로로 지정
2. timeout 과다
   - `--timeout` 상향, 혹은 workload 축소
3. corpus 증가 정체
   - `--generate-ratio` 조정, mutator 확장 필요
4. differential 과다/과소
   - flags 조합 재설계 (`--stress-*`, `--jitless` 대비 등)

---

## 8) 리포팅 직전 체크

- crash 최소 재현 스크립트 확보 (`.min.js`)
- 재현 시점의 d8 버전/커밋/플래그 기록
- 원본/최소화 입력과 stderr 로그를 쌍으로 보관

