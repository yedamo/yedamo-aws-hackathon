import express from 'express';
import cors from 'cors';
import { Client } from '@modelcontextprotocol/sdk/client/index.js';
import { StdioClientTransport } from '@modelcontextprotocol/sdk/client/stdio.js';
import { translateSajuResult, analyzeWuxing } from './utils/sajuTranslator.js';

const app = express();
const PORT = 3001;

app.use(cors());
app.use(express.json());

// MCP 클라이언트 초기화
let mcpClient = null;

async function initMCPClient() {
  try {
    const transport = new StdioClientTransport({
      command: 'npx',
      args: ['-y', '@mymcp-fun/bazi']
    });
    
    mcpClient = new Client({
      name: 'yedamo-client',
      version: '1.0.0'
    }, {
      capabilities: {}
    });

    await mcpClient.connect(transport);
    console.log('MCP 클라이언트 연결 성공');
  } catch (error) {
    console.error('MCP 클라이언트 연결 실패:', error);
  }
}

// MCP 도구 목록 조회 API (디버깅용)
app.get('/api/tools', async (req, res) => {
  try {
    if (!mcpClient) {
      return res.status(500).json({ error: 'MCP 클라이언트가 연결되지 않았습니다.' });
    }

    const tools = await mcpClient.listTools();
    res.json({ tools: tools.tools || [] });
  } catch (error) {
    console.error('도구 목록 조회 오류:', error);
    res.status(500).json({ error: error.message });
  }
});

// 사주 분석 API
app.post('/api/saju', async (req, res) => {
  try {
    const { birthDate, birthTime, isLunar, gender, name } = req.body;
    
    if (!mcpClient) {
      return res.status(500).json({ error: 'MCP 클라이언트가 연결되지 않았습니다.' });
    }

    // MCP 도구 목록 가져오기
    const tools = await mcpClient.listTools();
    console.log('사용 가능한 도구:', tools.tools?.map(t => t.name) || []);

    // 사주 계산 도구 호출
    let result;
    try {
      // 날짜 파싱
      const date = new Date(birthDate);
      const [hours, minutes] = birthTime.split(':').map(Number);
      
      result = await mcpClient.callTool({
        name: 'get_bazi_details',
        arguments: {
          year: date.getFullYear(),
          month: date.getMonth() + 1,
          day: date.getDate(),
          hour: hours,
          gender: gender || 'male',
          timezone: 'Asia/Seoul'
        }
      });
    } catch (toolError) {
      console.log('도구 호출 실패, 사용 가능한 도구들:', tools.tools);
      throw toolError;
    }

    // 결과 번역 및 파싱
    const translatedResult = translateSajuResult(result);
    
    if (!translatedResult) {
      throw new Error('사주 결과 번역에 실패했습니다.');
    }
    
    const wuxingAnalysis = analyzeWuxing(translatedResult.오행);
    
    res.json({
      success: true,
      data: {
        name: name,
        translatedData: translatedResult,
        wuxingAnalysis: wuxingAnalysis,
        rawData: result
      }
    });

  } catch (error) {
    console.error('사주 분석 오류:', error);
    res.status(500).json({ 
      error: '사주 분석 중 오류가 발생했습니다.',
      details: error.message 
    });
  }
});

// 서버 시작
app.listen(PORT, async () => {
  console.log(`서버가 포트 ${PORT}에서 실행 중입니다.`);
  console.log(`- API 엔드포인트: http://localhost:${PORT}/api/saju`);
  console.log(`- 도구 목록 확인: http://localhost:${PORT}/api/tools`);
  await initMCPClient();
});

// 프로세스 종료 시 MCP 클라이언트 정리
process.on('SIGINT', async () => {
  if (mcpClient) {
    await mcpClient.close();
  }
  process.exit(0);
});