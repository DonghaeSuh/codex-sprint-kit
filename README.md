# Codex Sprint Kit
시간 제한이 있는 개발 작업에서 **요구사항 → 구현 → 실험 → 검증 → 설명**을 연결하는 작은 로컬 하네스입니다.
Python 3.10+ / Linux·macOS. Python 표준 라이브러리만 사용합니다.
필수 MCP·API 키·외부 모델·자동 브라우저 조작·설치 후크가 없습니다.

## 5분 빠른 시작
이 저장소를 과제의 하위 폴더 또는 별도 허용 경로에 둡니다. 과제 README/AGENTS.md를 덮어쓰지 않습니다.
공개 전에는 clone 주소를 쓸 수 없습니다. 먼저 [공개 절차](guides/PUBLISH.md)를 완료하세요.

```bash
# kit 폴더에서: .은 현재 폴더, ../my-task는 이미 존재하는 실제 작업 폴더로 바꾸세요.
python3 scripts/doctor.py --root ../my-task
python3 scripts/init_workspace.py --root ../my-task
python3 -m unittest discover -s tests -v
```

Codex에 다음과 같이 요청합니다.
> 실제 과제 README와 기존 지침을 먼저 읽고, codex-sprint-kit/AGENTS.md를 작업 보조 지침으로 참고해라.
> task-intake/SKILL.md를 읽어 .sprint/BRIEF.md와 ACCEPTANCE.md를 채워라.
> 필수 조건·추정·질문을 구분하고 첫 핵심 흐름부터 구현해라.

경로는 배치 위치에 맞게 바꿉니다. 네이티브 Skill 목록에 안 나타나면 **SKILL.md를 직접 읽히면 됩니다.**
4개 Skill의 자동 발견을 위해 사용자 전역 설정을 바꾸거나 플랫폼 업로드 제한을 우회하지 않습니다.

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
python3 scripts/verify.py --root ../my-task --config ../my-task/.sprint/verify.json
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
STATE.md와 ACCEPTANCE.md를 갱신하고 위 출력의 REPORT 경로를 사용합니다.

```bash
python3 scripts/snapshot.py --root ../my-task --report .sprint/runs/RUN-ID/report.json --output .sprint/handoff-01.md
```

report/output 경로는 --root 기준입니다. 출력 파일이 이미 있으면 새 이름을 사용합니다.
새 세션에서 handoff, 관련 ADR 최대 3개, 해당 코드만 읽힙니다. 과거 검증은 변경된 코드의 보증이 아닙니다.

## 문서
- [작업 루프와 요청 예시](guides/WORKFLOW.md)
- [도구 선정과 실제 검증 수준](guides/TOOLS.md)
- [공개·고정 버전·반입](guides/PUBLISH.md)
- [합성 리허설](practice/README.md)
- [AI 없이 설명 연습](practice/EXPLAIN.md)
- [외부 출처·라이선스](THIRD_PARTY_NOTICES.md)
- [검증 결과](VALIDATION.md)

개별 시험·평가의 안내가 우선합니다. 이 도구가 사용 허가를 대신하지 않습니다.
