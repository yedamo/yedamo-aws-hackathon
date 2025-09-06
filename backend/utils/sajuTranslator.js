// 사주 한자 -> 한국어 번역 유틸리티

// 천간 번역
const tianganMap = {
  '甲': '갑목',
  '乙': '을목',
  '丙': '병화',
  '丁': '정화',
  '戊': '무토',
  '己': '기토',
  '庚': '경금',
  '辛': '신금',
  '壬': '임수',
  '癸': '계수'
};

// 지지 번역
const dizhiMap = {
  '子': '자(쥐)',
  '丑': '축(소)',
  '寅': '인(호랑이)',
  '卯': '묘(토끼)',
  '辰': '진(용)',
  '巳': '사(뱀)',
  '午': '오(말)',
  '未': '미(양)',
  '申': '신(원숭이)',
  '酉': '유(닭)',
  '戌': '술(개)',
  '亥': '해(돼지)'
};

// 오행 번역
const wuxingMap = {
  '木': '목(나무)',
  '火': '화(불)',
  '土': '토(흙)',
  '金': '금(쇠)',
  '水': '수(물)'
};

// 생肖 번역
const shengxiaoMap = {
  '鼠': '쥐',
  '牛': '소',
  '虎': '호랑이',
  '兔': '토끼',
  '龙': '용',
  '蛇': '뱀',
  '马': '말',
  '羊': '양',
  '猴': '원숭이',
  '鸡': '닭',
  '狗': '개',
  '猪': '돼지'
};

// 별자리 번역
const constellationMap = {
  '水瓶': '물병자리',
  '双鱼': '물고기자리',
  '白羊': '양자리',
  '金牛': '황소자리',
  '双子': '쌍둥이자리',
  '巨蟹': '게자리',
  '狮子': '사자자리',
  '处女': '처녀자리',
  '天秤': '천칭자리',
  '天蝎': '전갈자리',
  '射手': '사수자리',
  '摩羯': '염소자리'
};

// 음력 월 번역
const lunarMonthMap = {
  '正月': '정월',
  '二月': '이월',
  '三月': '삼월',
  '四月': '사월',
  '五月': '오월',
  '六月': '유월',
  '七月': '칠월',
  '八月': '팔월',
  '九月': '구월',
  '十月': '시월',
  '十一月': '십일월',
  '腊月': '섣달'
};

// 천간지지 조합 번역
function translateGanZhi(ganZhi) {
  if (!ganZhi || ganZhi.length !== 2) return ganZhi;
  
  const gan = ganZhi[0];
  const zhi = ganZhi[1];
  
  const ganKorean = tianganMap[gan] || gan;
  const zhiKorean = dizhiMap[zhi] || zhi;
  
  return `${ganKorean}${zhiKorean}`;
}

// MCP 결과를 한국어로 번역
export function translateSajuResult(mcpResult) {
  try {
    const content = mcpResult.content?.[0]?.text;
    if (!content) return null;
    
    const data = JSON.parse(content);
    
    return {
      사주팔자: {
        년주: translateGanZhi(data.四柱?.年柱),
        월주: translateGanZhi(data.四柱?.月柱),
        일주: translateGanZhi(data.四柱?.日柱),
        시주: translateGanZhi(data.四柱?.時柱)
      },
      오행: {
        목: data.五行?.木 || 0,
        화: data.五行?.火 || 0,
        토: data.五行?.土 || 0,
        금: data.五行?.金 || 0,
        수: data.五行?.水 || 0
      },
      띠: shengxiaoMap[data.生肖] || data.生肖,
      별자리: constellationMap[data.星座] || data.星座,
      음력정보: {
        음력년: data.農曆?.農曆年,
        음력월: data.農曆?.農曆月,
        음력일: data.農曆?.農曆日,
        윤달여부: data.農曆?.是否閏月 ? '윤달' : '평달',
        월이름: lunarMonthMap[data.農曆?.農曆月名] || data.農曆?.農曆月名
      },
      일주천간: tianganMap[data.日主] || data.日主,
      원본데이터: data
    };
  } catch (error) {
    console.error('사주 결과 번역 오류:', error);
    return null;
  }
}

// 오행 분석 해석
export function analyzeWuxing(wuxing) {
  const total = Object.values(wuxing).reduce((sum, val) => sum + val, 0);
  const analysis = [];
  
  Object.entries(wuxing).forEach(([element, count]) => {
    const percentage = ((count / total) * 100).toFixed(1);
    let strength = '';
    
    if (count === 0) strength = '부족';
    else if (count === 1) strength = '약함';
    else if (count === 2) strength = '보통';
    else if (count >= 3) strength = '강함';
    
    analysis.push(`${element}: ${count}개 (${percentage}%) - ${strength}`);
  });
  
  return analysis;
}