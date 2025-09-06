import { useState, useEffect } from 'react';

function SajuResult({ personalInfo, sajuData, onChatStart }) {
  const [generatedImage, setGeneratedImage] = useState(null);
  const [isGenerating, setIsGenerating] = useState(true);
  const [imageError, setImageError] = useState(null);

  // 십간 색깔 매핑
  const colorMapping = {
    "갑": "청색", "을": "청색",
    "병": "적색", "정": "적색", 
    "무": "황색", "기": "황색",
    "경": "백색", "신": "백색",
    "임": "흑색", "계": "흑색"
  };

  // 십이지 동물 매핑
  const animalMapping = {
    "자": "쥐", "축": "소", "인": "호랑이", "묘": "토끼",
    "진": "용", "사": "뱀", "오": "말", "미": "양",
    "신": "원숭이", "유": "닭", "술": "개", "해": "돼지"
  };

  const generateImage = async () => {
    try {
      // 일주에서 색깔과 동물 추출
      const dayPillar = sajuData.day_pillar || "갑자"; // 임시 기본값
      const color = colorMapping[dayPillar[0]] || "청색";
      const animal = animalMapping[dayPillar[1]] || "쥐";

      // 임시 고정 데이터 (추후 실제 사주 데이터로 교체)
      const requestData = {
        animal: animal,
        color: color,
        gender: personalInfo.gender || "neutral",
        elements: {
          wood: 2,
          fire: 1,
          earth: 3,
          metal: 1,
          water: 1
        },
        dominant_element: "earth",
        yin_yang_balance: "balanced"
      };

      const response = await fetch('https://w3qvjjo80g.execute-api.us-east-1.amazonaws.com/prod/image-generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestData)
      });

      const data = await response.json();

      if (data.success) {
        setGeneratedImage(data.image);
      } else {
        throw new Error(data.error || '이미지 생성에 실패했습니다.');
      }
    } catch (error) {
      setImageError(error.message);
    } finally {
      setIsGenerating(false);
    }
  };

  // 컴포넌트 마운트 시 자동으로 이미지 생성
  useEffect(() => {
    generateImage();
  }, []);

  return (
    <div className="max-w-2xl mx-auto bg-white rounded-lg shadow-lg p-6">
      <h2 className="text-2xl font-semibold text-gray-800 mb-6 text-center">
        {personalInfo.name}님의 사주 분석 결과
      </h2>

      <div className="space-y-6">
        <div className="bg-purple-50 p-4 rounded-lg">
          <h3 className="text-lg font-semibold text-purple-800 mb-2">사주팔자</h3>
          <div className="grid grid-cols-2 gap-2 text-sm text-gray-700">
            <div><span className="font-medium">년주:</span> {sajuData.year_pillar}</div>
            <div><span className="font-medium">월주:</span> {sajuData.month_pillar}</div>
            <div><span className="font-medium">일주:</span> {sajuData.day_pillar}</div>
            <div><span className="font-medium">시주:</span> {sajuData.hour_pillar}</div>
          </div>
        </div>

        <div className="bg-blue-50 p-4 rounded-lg">
          <h3 className="text-lg font-semibold text-blue-800 mb-2">오행 분석</h3>
          <p className="text-gray-700">{sajuData.elements}</p>
        </div>

        <div className="bg-green-50 p-4 rounded-lg">
          <h3 className="text-lg font-semibold text-green-800 mb-2">출생 정보</h3>
          <p className="text-gray-700">
            생년월일: {sajuData.birth_date}
          </p>
        </div>

        {sajuData.fallback_used && (
          <div className="bg-yellow-50 p-4 rounded-lg">
            <h3 className="text-lg font-semibold text-yellow-800 mb-2">분석 정보</h3>
            <p className="text-sm text-gray-600">
              기본 계산 방식으로 분석되었습니다. 더 자세한 상담을 위해 AI 상담사와 대화해보세요.
            </p>
          </div>
        )}

        {/* 이미지 생성 섹션 */}
        <div className="bg-gradient-to-r from-purple-50 to-pink-50 p-4 rounded-lg">
          <h3 className="text-lg font-semibold text-purple-800 mb-3">이세계 사주월드에서의 내 모습</h3>
          
          {isGenerating && (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-500 mx-auto mb-4"></div>
              <p className="text-gray-600 text-lg font-medium">당신만의 특별한 이미지를 생성하고 있습니다...</p>
              <p className="text-gray-500 text-sm mt-2">잠시만 기다려주세요 (약 30초 소요)</p>
            </div>
          )}

          {imageError && (
            <div className="bg-red-50 border border-red-200 rounded-md p-4 text-center">
              <p className="text-red-600 mb-3">이미지 생성 중 오류가 발생했습니다</p>
              <p className="text-red-500 text-sm mb-3">{imageError}</p>
              <button
                onClick={() => {
                  setIsGenerating(true);
                  setImageError(null);
                  generateImage();
                }}
                className="bg-red-500 text-white py-2 px-4 rounded-md hover:bg-red-600 transition duration-200"
              >
                다시 시도
              </button>
            </div>
          )}

          {generatedImage && !isGenerating && (
            <div className="text-center">
              <img
                src={`data:image/png;base64,${generatedImage}`}
                alt="생성된 사주 동물 이미지"
                className="max-w-full h-auto rounded-lg shadow-lg mx-auto mb-4"
                style={{ maxHeight: '400px' }}
              />
              <button
                onClick={() => {
                  setIsGenerating(true);
                  setGeneratedImage(null);
                  generateImage();
                }}
                className="text-sm text-purple-600 hover:text-purple-800 underline"
              >
                새로운 이미지 생성
              </button>
            </div>
          )}
        </div>
      </div>

      <div className="mt-8 text-center">
        <button
          onClick={onChatStart}
          className="bg-purple-600 text-white py-3 px-6 rounded-md hover:bg-purple-700 transition duration-200"
        >
          AI 상담사와 대화하기
        </button>
      </div>
    </div>
  )
}

export default SajuResult