# 도구 조사와 선정 — 2026-10-30
기준은 설치 수가 아니라 시간 제한 안에서의 추가 효용입니다.
검증 단계: source(원문 확인), static(선택 파일 검토), executed(실행), compared(효과 비교).
상위 단계는 하위 단계를 포함합니다. 한 저장소 전체를 감사했다고 해석하면 안 됩니다.
고정 커밋·읽은 파일은 ../sources.lock.json에 기록했습니다.

| 후보 | 판정 | 확인한 근거 / 한계 |
|---|---|---|
| 자체 4 Skill + Python 하네스 | 기본 사용 | 실행 검증은 VALIDATION.md. Skill 효과 A/B는 미측정 |
| obra/superpowers 디버깅·검증 | 절차 참고 | 두 SKILL.md 검토. 다른 Skill 참조·긴 절차가 있어 그대로 반입하지 않음 |
| Superpowers 전체 | 기본 제외 | 전체 설치 없이 필요한 원리만 독립 작성 |
| openai/skills | 신규 설치 경로 제외 | 고정 커밋 README에 deprecated 및 openai/plugins 이전 안내 |
| openai/plugins | 필요 시 탐색 | 최신 공식 예시. 전체 설치·최신 CLI 호환 가정 금지 |
| Vercel React Best Practices | React일 때 선택 | SKILL.md의 성능 우선순위 참고. 하위 규칙 전체 실행 검증은 아님 |
| Vercel 디자인 지침 | 선택 후보 | UI 과제일 때만 세부 원문 검토 후 사용, 이번 패키지에 포함 안 함 |
| Anthropic frontend-design | 참고 후보 | SKILL.md 읽음. 자체 환경·이미지·브라우저 관련 절차는 그대로 적용하지 않음 |
| Anthropic PDF/XLSX | 기본 제외 | Proprietary 표기, XLSX는 LibreOffice 재계산·사전 설치 가정. 원문 복제 안 함 |
| OpenAI Docs MCP | 선택 | 공식 문서 조회만. 현재 셸 DNS 실패로 프로토콜 실행 미검증 |
| Context7 | 선택 | README는 원격 URL·인증 안내. 개인 인증/외부 질의가 필요할 수 있음 |
| GitHub MCP | 제외 | 인증·다수 API 대신 공개 저장소 읽기/clone으로 충분 |
| Filesystem MCP | 제외 | 기본 파일 도구와 중복 |
| Memory MCP | 제외 | 로컬 STATE/ADR로 충분, 최신 원문은 Node 24+ 요구 |
| Sequential Thinking MCP | 제외 | 추가 서버의 시간/품질 효과 입증 안 됨, Node 24+ 요구 |
| Playwright MCP / CLI | 자동 조작 제한 시 제외 | 원문이 브라우저 자동화를 명시; CLI로 바꿔도 성격 동일 |
| Chrome DevTools MCP | 자동 조작 제한 시 제외 | 별도 실측 없음, 제한된 평가용 기본 스택에 넣지 않음 |
| 원격 크롤링·검색·벡터 DB | 제외 | task 데이터 전송과 설정 비용, 제공 자료·로컬 검색 우선 |
| 원격 추적·자동 배포·PR 도구 | 제외 | 결과물 외부 전송이 없는 로컬 근거 기록으로 대체 |

## 꼭 필요한 경우에만 MCP 연결
1. 허용 범위와 제공 클라이언트 버전의 도움말 확인.
2. 설정이 이미 있는지 확인하고 중복 등록·기존 설정 덮어쓰기 금지.
3. 아래 OpenAI 공식 예시를 제공 환경이 허용할 때 사용.
4. 등록 성공, 도구 노출, 공개 일반 문서 질의 성공을 구분하여 기록.
5. 3분 이상 걸리거나 차단되면 중단. 연결 성공을 다른 환경까지 일반화하지 않음.

```bash
codex mcp --help
codex mcp list
codex mcp add openaiDeveloperDocs --url https://developers.openai.com/mcp
```

공식 출처: https://developers.openai.com/learn/docs-mcp
일반 질의 예: “Python csv 모듈 DictReader의 빈 행 처리”.
금지할 질의 예: 실제 문제 원문, 업무 파일 행, 구현 코드, 로그를 붙인 외부 질의.
읽기 전용 MCP도 쿼리는 외부로 나갑니다.
플랫폼의 JSON MCP 탭과 Codex 설정이 연동되는지는 각각 확인해야 합니다.
Context7 원격 주소는 https://mcp.context7.com/mcp 이지만 인증·정책·쿼리 범위를 확인하기 전 자동 등록하지 않습니다.
