import express from "express";
import cors from "cors";
import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";
import { spawn } from "child_process";
import crypto from "crypto";
import redis from "redis";
import { BedrockRuntimeClient, InvokeModelCommand } from "@aws-sdk/client-bedrock-runtime";
import { translateSajuResult, analyzeWuxing } from "./utils/sajuTranslator.js";

const app = express();
const PORT = process.env.PORT || 3001;

// Bedrock 클라이언트 설정
const bedrockClient = new BedrockRuntimeClient({ 
  region: process.env.AWS_REGION || "us-east-1" 
});

// Redis 클라이언트 설정
let redisClient = null;
let redisConnected = false;

async function initializeRedis() {
  try {
    redisClient = redis.createClient({
      socket: {
        host: process.env.REDIS_HOST || "localhost",
        port: process.env.REDIS_PORT || 6379,
        connectTimeout: 5000,
        lazyConnect: true,
      },
    });

    redisClient.on("error", (err) => {
      console.error("Redis 연결 오류:", err.message);
      redisConnected = false;
    });

    redisClient.on("connect", () => {
      console.log("Redis 연결 성공");
      redisConnected = true;
    });

    await redisClient.connect();
  } catch (error) {
    console.error("Redis 초기화 실패:", error.message);
    redisConnected = false;
  }
}

app.use(cors());
app.use(express.json());

let mcpClient = null;

// MCP 클라이언트 초기화
async function initializeMCP() {
  try {
    const transport = new StdioClientTransport({
      command: "npx",
      args: ["@mymcp-fun/bazi"],
    });

    mcpClient = new Client(
      {
        name: "yedamo-client",
        version: "1.0.0",
      },
      {
        capabilities: {},
      }
    );

    await mcpClient.connect(transport);
    console.log("MCP 클라이언트 연결 성공");
  } catch (error) {
    console.error("MCP 클라이언트 연결 실패:", error);
  }
}

// 캐시 키 생성 (cache_manager와 동일한 방식)
function generateCacheKey(name) {
  const timestamp = Math.floor(Date.now() / 1000);
  return `${timestamp}_${name}`;
}

// 사주 기본 분석 API (캐시 지원)
app.post("/saju/basic", async (req, res) => {
  try {
    // 두 가지 형식 지원: birthDate/birthTime 또는 birth_info 객체
    let birthDate, birthTime, isLunar, gender, name, requestCacheKey;
    
    if (req.body.birth_info) {
      // birth_info 객체 형식
      const { birth_info } = req.body;
      name = req.body.name;
      requestCacheKey = req.body.cacheKey;
      
      birthDate = `${birth_info.year}-${birth_info.month.toString().padStart(2, '0')}-${birth_info.day.toString().padStart(2, '0')}`;
      birthTime = `${birth_info.hour.toString().padStart(2, '0')}:00`;
      isLunar = birth_info.isLunar || false;
      gender = birth_info.gender || "male";
    } else {
      // 기존 birthDate/birthTime 형식
      ({ birthDate, birthTime, isLunar, gender, name, cacheKey: requestCacheKey } = req.body);
    }

    if (!birthDate || !birthTime) {
      return res
        .status(400)
        .json({ error: "생년월일과 시간 정보가 필요합니다." });
    }

    // 캐시 키 처리 - 요청에 있으면 사용, 없으면 생성
    const cacheKey = requestCacheKey || generateCacheKey(name || "anonymous");

    // 캐시에서 데이터 확인 (Redis 연결된 경우만)
    let needsRefresh = false;
    if (redisConnected && redisClient) {
      try {
        const cachedJson = await redisClient.get(cacheKey);
        if (cachedJson) {
          const cachedItem = JSON.parse(cachedJson);
          const currentTime = Math.floor(Date.now() / 1000);
          const age = currentTime - (cachedItem.timestamp || 0);

          // 갱신 필요 확인 (만료 5분 미만)
          needsRefresh = age > 1800 - 300; // TTL 30분 - 갱신임계값 5분

          if (!needsRefresh) {
            console.log("캐시에서 데이터 반환:", cacheKey);
            return res.json({
              cache_key: cacheKey,
              cached: true,
              needsRefresh: false,
              ...cachedItem,
            });
          }
        }
      } catch (cacheError) {
        console.error("캐시 조회 오류:", cacheError.message);
      }
    }

    if (!mcpClient) {
      return res
        .status(500)
        .json({ error: "MCP 클라이언트가 연결되지 않았습니다." });
    }

    // 날짜 파싱
    const date = new Date(birthDate);
    const [hours, minutes] = birthTime.split(":").map(Number);

    // 사주 계산
    const result = await mcpClient.callTool({
      name: "get_bazi_details",
      arguments: {
        year: date.getFullYear(),
        month: date.getMonth() + 1,
        day: date.getDate(),
        hour: hours,
        gender: gender || "male",
        timezone: "Asia/Seoul",
      },
    });

    // 결과 번역 및 파싱
    const translatedResult = translateSajuResult(result);

    if (!translatedResult) {
      throw new Error("사주 결과 번역에 실패했습니다.");
    }

    const wuxingAnalysis = analyzeWuxing(translatedResult.오행);

    const sajuAnalysis = {
      success: true,
      data: {
        name: name || "익명",
        translatedData: translatedResult,
        wuxingAnalysis: wuxingAnalysis,
        rawData: {
          content: [
            {
              type: "text",
              text: JSON.stringify(translatedResult.원본데이터, null, 2),
            },
          ],
          isError: false,
        },
      },
      timestamp: Math.floor(Date.now() / 1000),
    };

    // 캐시에 저장 (Redis 연결된 경우만)
    if (redisConnected && redisClient) {
      try {
        await redisClient.setEx(cacheKey, 1800, JSON.stringify(sajuAnalysis));
        console.log("캐시에 데이터 저장:", cacheKey);
      } catch (cacheError) {
        console.error("캐시 저장 오류:", cacheError.message);
      }
    }

    res.json({
      cache_key: cacheKey,
      cached: false,
      needsRefresh: needsRefresh,
      redis_connected: redisConnected,
      ...sajuAnalysis,
    });
  } catch (error) {
    console.error("사주 분석 오류:", error);
    res.status(500).json({
      error: "사주 분석 중 오류가 발생했습니다.",
      details: error.message,
    });
  }
});

// 캐시된 사주 데이터 조회 API
app.get("/api/saju/:cacheKey", async (req, res) => {
  try {
    const { cacheKey } = req.params;

    if (!redisConnected || !redisClient) {
      return res.status(503).json({ error: "Redis 연결이 없습니다." });
    }

    const cachedJson = await redisClient.get(cacheKey);
    if (!cachedJson) {
      return res
        .status(404)
        .json({ error: "캐시된 데이터를 찾을 수 없습니다." });
    }

    const cachedItem = JSON.parse(cachedJson);
    const currentTime = Math.floor(Date.now() / 1000);
    const age = currentTime - (cachedItem.timestamp || 0);
    const needsRefresh = age > 1800 - 300;

    res.json({
      cache_key: cacheKey,
      cached: true,
      needsRefresh: needsRefresh,
      ...cachedItem,
    });
  } catch (error) {
    console.error("캐시 조회 오류:", error);
    res.status(500).json({
      error: "캐시 조회 중 오류가 발생했습니다.",
      details: error.message,
    });
  }
});

// 사주 상담 API (Lambda에서 이전)
app.post("/saju/consultation", async (req, res) => {
  try {
    const { cache_key, question } = req.body;

    if (!cache_key) {
      return res.status(400).json({ error: "cache_key가 필요합니다" });
    }
    if (!question) {
      return res.status(400).json({ error: "질문이 필요합니다" });
    }

    // Redis에서 캐시된 사주 데이터 조회
    if (!redisConnected || !redisClient) {
      return res.status(503).json({ error: "Redis 연결이 없습니다" });
    }

    const cachedJson = await redisClient.get(cache_key);
    if (!cachedJson) {
      return res.status(404).json({ 
        error: "캐시에서 사주 데이터를 찾을 수 없습니다",
        cache_key: cache_key
      });
    }

    const cachedData = JSON.parse(cachedJson);
    
    // Bedrock을 사용한 AI 상담 응답 생성
    const consultation = await generateConsultation(question, cachedData);

    res.json({
      agent_type: "ec2_bedrock_consultation",
      consultation: consultation,
      cache_key: cache_key,
      question: question,
      timestamp: new Date().toISOString()
    });

  } catch (error) {
    console.error("상담 처리 오류:", error);
    res.status(500).json({
      error: "상담 중 오류가 발생했습니다. 다시 시도해주세요.",
      details: error.message
    });
  }
});

// Bedrock을 사용한 상담 응답 생성 함수

// 헬스 체크
app.get("/health", (req, res) => {
  res.json({
    status: "OK",
    timestamp: new Date().toISOString(),
    redis_connected: redisConnected,
  });
});

// 서버 시작
app.listen(PORT, () => {
  console.log(`서버가 포트 ${PORT}에서 실행 중입니다.`);
  console.log(`- API 엔드포인트: http://localhost:${PORT}/api/saju`);
  console.log(`- 캐시 조회: http://localhost:${PORT}/api/saju/:cacheKey`);
  console.log(`- 헬스 체크: http://localhost:${PORT}/health`);

  // 비동기 초기화
  initializeRedis();
  initializeMCP();
});
// Bedrock을 사용한 상담 응답 생성 함수 (타임아웃 추가)
async function generateConsultation(question, sajuData) {
  try {
    const name = sajuData.data?.name || '고객';
    const translatedData = sajuData.data?.translatedData;
    const wuxingAnalysis = sajuData.data?.wuxingAnalysis;
    
    const prompt = `당신은 전문 사주명리학 상담사입니다. 다음 사주 정보를 바탕으로 질문에 답변해주세요.

고객명: ${name}
질문: ${question}

사주 정보:
- 사주팔자: ${JSON.stringify(translatedData?.사주팔자 || {})}
- 오행 분석: ${JSON.stringify(wuxingAnalysis || {})}
- 십신: ${JSON.stringify(translatedData?.십신 || {})}

답변 요구사항:
1. 전문적이면서도 이해하기 쉽게 설명
2. 구체적이고 실용적인 조언 제공
3. 긍정적이고 건설적인 방향으로 안내
4. 200-300자 내외로 간결하게 작성

답변:`;

    // 10초 타임아웃으로 Bedrock 호출
    const timeoutPromise = new Promise((_, reject) => 
      setTimeout(() => reject(new Error('Bedrock timeout')), 10000)
    );

    const bedrockPromise = (async () => {
      const command = new InvokeModelCommand({
        modelId: 'anthropic.claude-3-haiku-20240307-v1:0',
        body: JSON.stringify({
          anthropic_version: 'bedrock-2023-05-31',
          max_tokens: 500,
          messages: [{ role: 'user', content: prompt }]
        })
      });

      const response = await bedrockClient.send(command);
      const responseBody = JSON.parse(new TextDecoder().decode(response.body));
      return responseBody.content[0].text;
    })();

    return await Promise.race([bedrockPromise, timeoutPromise]);

  } catch (error) {
    console.error('Bedrock 호출 오류:', error);
    
    // 빠른 폴백 응답
    const name = sajuData.data?.name || '고객';
    const wuxing = sajuData.data?.wuxingAnalysis || [];
    
    let response = `${name}님의 사주를 바탕으로 답변드리겠습니다.\n\n`;
    
    if (question.includes('운세') || question.includes('올해')) {
      response += '올해는 ';
      if (wuxing.some(w => w.includes('화') && w.includes('강함'))) {
        response += '화의 기운이 강해 활동적이고 적극적인 한 해가 될 것입니다. ';
      } else if (wuxing.some(w => w.includes('금') && w.includes('강함'))) {
        response += '금의 기운으로 결단력과 추진력이 좋은 해입니다. ';
      } else {
        response += '균형잡힌 오행으로 안정적인 운세를 보입니다. ';
      }
    } else {
      response += '전반적으로 균형잡힌 사주를 가지고 계십니다. ';
    }
    
    response += '꾸준한 노력과 긍정적인 마음가짐이 좋은 결과를 가져다 줄 것입니다.';
    
    return response;
  }
}

// Bedrock을 사용한 상담 응답 생성 함수 (타임아웃 최적화)
async function generateConsultation(question, sajuData) {
  try {
    const name = sajuData.data?.name || "고객";
    const translatedData = sajuData.data?.translatedData;
    const wuxingAnalysis = sajuData.data?.wuxingAnalysis;
    
    const prompt = `당신은 전문 사주명리학 상담사입니다. 다음 사주 정보를 바탕으로 질문에 답변해주세요.

고객명: ${name}
질문: ${question}

사주 정보:
- 사주팔자: ${JSON.stringify(translatedData?.사주팔자 || {})}
- 오행 분석: ${JSON.stringify(wuxingAnalysis || {})}

답변 요구사항:
1. 전문적이면서도 이해하기 쉽게 설명
2. 구체적이고 실용적인 조언 제공
3. 긍정적이고 건설적인 방향으로 안내
4. 200-300자 내외로 간결하게 작성

답변:`;

    // 10초 타임아웃으로 Bedrock 호출
    const timeoutPromise = new Promise((_, reject) => 
      setTimeout(() => reject(new Error("Bedrock timeout")), 10000)
    );

    const bedrockPromise = (async () => {
      const command = new InvokeModelCommand({
        modelId: "anthropic.claude-3-haiku-20240307-v1:0",
        body: JSON.stringify({
          anthropic_version: "bedrock-2023-05-31",
          max_tokens: 500,
          messages: [{ role: "user", content: prompt }]
        })
      });

      const response = await bedrockClient.send(command);
      const responseBody = JSON.parse(new TextDecoder().decode(response.body));
      return responseBody.content[0].text;
    })();

    return await Promise.race([bedrockPromise, timeoutPromise]);

  } catch (error) {
    console.error("Bedrock 호출 오류:", error);
    
    // 빠른 폴백 응답 (사주 데이터 기반)
    const name = sajuData.data?.name || "고객";
    const wuxing = sajuData.data?.wuxingAnalysis || [];
    
    let response = `${name}님의 사주를 바탕으로 답변드리겠습니다.\n\n`;
    
    if (question.includes("운세") || question.includes("올해")) {
      response += "올해는 ";
      if (wuxing.some(w => w.includes("화") && w.includes("강함"))) {
        response += "화의 기운이 강해 활동적이고 적극적인 한 해가 될 것입니다. ";
      } else if (wuxing.some(w => w.includes("금") && w.includes("강함"))) {
        response += "금의 기운으로 결단력과 추진력이 좋은 해입니다. ";
      } else {
        response += "균형잡힌 오행으로 안정적인 운세를 보입니다. ";
      }
    } else {
      response += "전반적으로 균형잡힌 사주를 가지고 계십니다. ";
    }
    
    response += "꾸준한 노력과 긍정적인 마음가짐이 좋은 결과를 가져다 줄 것입니다.";
    
    return response;
  }
}
