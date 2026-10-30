# Codex Sprint Kit
시간 제한이 있는 개발 작업에서 **요구사항 → 구현 → 실험 → 검증 → 설명**을 연결하는 작은 로컬 하네스입니다.
Python 3.10+ / Linux·macOS. Python 표준 라이브러리만 사용합니다.
필수 MCP·API 키·외부 모델·자동 브라우저 조작·설치 후크가 없습니다.

## 시험 때는 여기만 보고 시작하세요
**실제 과제 README가 있는 응시 환경의 폴더**에서 아래 두 줄을 실행하세요.
공개 저장소 다운로드가 허용된 환경에서만 사용합니다. 로컬 준비 PC에서 실제 과제를 풀지 않습니다.

```bash
git clone https://github.com/DonghaeSuh/codex-sprint-kit.git codex-sprint-kit
codex 'codex-sprint-kit/SESSION.md를 읽고 세션 시작 절차를 수행해줘. 실제 과제 README와 기존 지침을 우선하고, 실제 구현과 실험 및 기록은 이 응시 작업 공간 안에서만 진행해줘.'
```

**`cd codex-sprint-kit`를 하지 마세요.** Codex는 실제 과제 폴더에서 시작합니다.
이미 clone했다면 첫 줄을 반복하지 않고 두 번째 줄만 실행합니다.
제공 CLI가 첫 요청 인자를 받지 않으면 `codex`만 실행한 뒤 위 따옴표 안 문장을 첫 메시지로 입력하세요.
Codex가 안내에 따라 환경 확인, 템플릿 초기화, 요구 파악, 검증 설정을 진행합니다.
업무 질문에 답하고, 화면을 직접 확인하고, 최종 제출하는 일은 사용자 역할입니다.

**이후 모든 단계는 [SESSION.md — clone 이후 끝까지](SESSION.md)에 있습니다.**
문맥이 끊기면 새 Codex에 다음을 입력하세요.

> codex-sprint-kit/SESSION.md의 세션 복구 절차에 따라 .sprint/STATE.md와 관련 근거를 읽고 이어서 진행해줘.

### 기억할 경계
- 공개 키트에는 범용 지침·빈 양식·합성 연습만 있습니다.
- 실제 문제·코드·데이터·실험 결과는 **응시 작업 공간에만** 남깁니다.
- 응시 중 push, PR, 원격 배포, 외부 로그/파일 전송을 하지 않습니다.
- 이 지침은 기술적 네트워크 차단 장치가 아닙니다. 제공 환경의 규정을 따라야 합니다.
- Skill이 자동 발견되지 않으면 SESSION.md가 해당 SKILL.md를 직접 읽도록 안내합니다.
- 사용자 전역 설정, 인증, 제공 Codex 버전은 변경하지 않습니다.

## 검증 설정
초기 .sprint/verify.json은 수동 검사를 담고 있으므로 실행하면 not_run, exit 1이 정상입니다.
실제 과제의 실행 명령으로 편집하세요. 예시:

```json
{
  "checks": [
    {"id": "unit", "argv": ["python3", "-m", "unittest", "discover", "-s", "tests"], "timeout_seconds": 60},
    {"id": "core-ui", "manual": "내장 Browser에서 등록→조회→상태 변경을 직접 확인"}
  ]
}
```

```bash
python3 codex-sprint-kit/scripts/verify.py --root . --config .sprint/verify.json
```

- 명령 인자는 배열입니다. 파이프·리다이렉트·셸 치환을 자동 해석하지 않습니다.
- cwd는 --root 기준입니다. 설정 파일 경로는 호출한 셸 기준입니다.
- exit 0: 모든 검사 pass. exit 1: fail/timeout/not_run 존재. exit 2: 설정·경로 오류.
- 각 실행은 새로운 .sprint/runs/시간-ID 폴더를 만듭니다. 이전 근거를 덮어쓰지 않습니다.
- 검사당 기본 30초, 최대 600초. 로그 기본 128KiB, 초과 출력은 잘립니다.
- 수동 검사는 항상 not_run으로 남습니다. 사람의 관측은 MANUAL-CHECKS.md에 별도 기록합니다.
- 명령의 exit 0은 그 명령이 보장한 것만 증명합니다. 빈 테스트 모음이나 외부 도구의 JSON 오류 필드도 확인하세요.
- 신뢰하는 명령만 넣으세요. 실행기는 샌드박스가 아니며 명령의 파일 변경·네트워크를 차단하지 않습니다.
- 서버 시작 명령을 검증기에 넣지 마세요. 검사 종료 시 해당 프로세스 그룹을 정리합니다. 서버는 별도 터미널에서 유지합니다.
- 로그와 명령 인자에 비밀값을 넣지 마세요. 자동 비밀 마스킹은 제공하지 않습니다.

## 세션 복구
사용자는 위의 복구 요청만 입력하면 됩니다. Codex가 STATE의 실제 보고서 경로를 읽고,
필요하면 snapshot.py에 그 경로와 새 출력 파일 이름을 넣어 요약을 만듭니다.
보고서가 아직 없으면 STATE와 ACCEPTANCE로 복구하고 첫 기준 검사를 수행합니다.
과거 검증은 변경된 코드의 보증이 아닙니다. 필요한 검사만 다시 실행합니다.

## 문서
- **[clone 직후부터 제출까지의 세션 안내](SESSION.md)**
- [작업 루프와 요청 예시](guides/WORKFLOW.md)
- [도구 선정과 실제 검증 수준](guides/TOOLS.md)
- [공개·고정 버전·반입](guides/PUBLISH.md)
- [합성 리허설](practice/README.md)
- [AI 없이 설명 연습](practice/EXPLAIN.md)
- [외부 출처·라이선스](THIRD_PARTY_NOTICES.md)
- [검증 결과](VALIDATION.md)

개별 시험·평가의 안내가 우선합니다. 이 도구가 사용 허가를 대신하지 않습니다.
