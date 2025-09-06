import express from "express";
import cors from "cors";
import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";
import { spawn } from "child_process";
import crypto from "crypto";
import redis from "redis";
import { translateSajuResult, analyzeWuxing } from "./utils/sajuTranslator.js";

const app = express();
const PORT = process.env.PORT || 3001;

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
    const {
      birthDate,
      birthTime,
      isLunar,
      gender,
      name,
      cacheKey: requestCacheKey,
    } = req.body;

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
              cacheKey: cacheKey,
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
      cacheKey: cacheKey,
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
      cacheKey: cacheKey,
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
