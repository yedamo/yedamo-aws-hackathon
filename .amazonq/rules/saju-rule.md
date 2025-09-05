# Bazi MCP 서버 규칙 및 사용법

## 패키지 정보
- **패키지명**: `@mymcp-fun/bazi`
- **설명**: 중국 전통 사주팔자(八字) 계산 MCP 서버
- **버전**: 2.0.2+
- **라이센스**: MIT

## 설치 및 실행
```bash
# 직접 실행 (권장)
npx @mymcp-fun/bazi

# 전역 설치
npm install -g @mymcp-fun/bazi
bazi
```

## MCP 클라이언트 설정
```json
{
  "mcpServers": {
    "bazi": {
      "command": "npx",
      "args": ["-y", "@mymcp-fun/bazi"]
    }
  }
}
```

## 도구 API 스펙

### get_bazi_details
**목적**: 생년월일시를 기반으로 사주팔자 계산

**입력 매개변수**:
- `year` (number, 필수): 출생년도 (1900-2100)
- `month` (number, 필수): 출생월 (1-12)
- `day` (number, 필수): 출생일 (1-31)
- `hour` (number, 필수): 출생시간 (0-23)
- `gender` (string, 선택): "male" 또는 "female" (기본값: "male")
- `timezone` (string, 선택): 시간대 (기본값: "Asia/Shanghai")

**출력 형식**:
```json
{
  "四柱": {
    "年柱": "천간지지",
    "月柱": "천간지지",
    "日柱": "천간지지",
    "時柱": "천간지지"
  },
  "五行": {
    "木": 숫자,
    "火": 숫자,
    "土": 숫자,
    "金": 숫자,
    "水": 숫자
  },
  "生肖": "띠",
  "星座": "별자리",
  "農曆": {
    "農曆年": 음력년,
    "農曆月": 음력월,
    "農曆日": 음력일,
    "是否閏月": boolean,
    "農曆月名": "월이름"
  },
  "日主": "일간천간"
}
```

## 백엔드 연동 예시

### Node.js Express 서버
```javascript
import { Client } from '@modelcontextprotocol/sdk/client/index.js';
import { StdioClientTransport } from '@modelcontextprotocol/sdk/client/stdio.js';

// MCP 클라이언트 초기화
const transport = new StdioClientTransport({
  command: 'npx',
  args: ['-y', '@mymcp-fun/bazi']
});

const mcpClient = new Client({
  name: 'your-client',
  version: '1.0.0'
}, { capabilities: {} });

await mcpClient.connect(transport);

// 사주 계산 호출
const result = await mcpClient.callTool({
  name: 'get_bazi_details',
  arguments: {
    year: 2006,
    month: 1,
    day: 28,
    hour: 23,
    gender: 'male',
    timezone: 'Asia/Seoul'
  }
});
```

## 일반적인 오류 및 해결책

### 1. 패키지 이름 오류
- ❌ `@mymcp/bazi`
- ✅ `@mymcp-fun/bazi`

### 2. 도구 이름 오류
- ❌ `calculate_bazi`
- ✅ `get_bazi_details`

### 3. 매개변수 형식 오류
- ❌ `birth_date`, `birth_time`
- ✅ `year`, `month`, `day`, `hour`

### 4. 연결 실패 시 확인사항
- Node.js 18+ 버전 확인
- npx 명령어 사용 가능 여부
- 네트워크 연결 상태
- MCP SDK 버전 호환성

## 기술 스택
- **MCP SDK**: @modelcontextprotocol/sdk
- **계산 엔진**: lunar-javascript
- **언어**: TypeScript/JavaScript
- **런타임**: Node.js 18+

## 사용 예시

### 입력
```json
{
  "year": 2006,
  "month": 1,
  "day": 28,
  "hour": 23,
  "gender": "male",
  "timezone": "Asia/Seoul"
}
```

### 출력
```json
{
  "四柱": {
    "年柱": "乙酉",
    "月柱": "己丑",
    "日柱": "丁巳",
    "時柱": "壬子"
  },
  "五行": {
    "木": 1,
    "火": 2,
    "土": 2,
    "金": 1,
    "水": 2
  },
  "生肖": "鸡",
  "星座": "水瓶",
  "農曆": {
    "農曆年": 2005,
    "農曆月": 12,
    "農曆日": 29,
    "是否閏月": false,
    "農曆月名": "腊月"
  },
  "日主": "丁"
}
```

## 주의사항
- 시간대 설정이 중요 (한국: "Asia/Seoul")
- 시간은 24시간 형식 (0-23)
- 성별은 "male" 또는 "female"만 허용
- 년도 범위: 1900-2100
