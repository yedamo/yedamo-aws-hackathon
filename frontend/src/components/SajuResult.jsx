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
      // 실제 응답 구조에서 일주 추출
      const dayPillar = sajuData?.translatedData?.사주팔자?.일주 || "임수신(원숭이)";
      
      // 일주에서 천간과 지지 분리 (예: "임수신(원숭이)" -> "임", "신")
      const heavenlyStem = sajuData?.translatedData?.일주천간?.charAt(0) || "임";
      const earthlyBranch = dayPillar.match(/[자축인묘진사오미신유술해]/)?.[0] || "신";
      
      const color = colorMapping[heavenlyStem] || "흑색";
      const animal = animalMapping[earthlyBranch] || "원숭이";

      const requestData = {
        color: color,
        animal: animal
      };

      const response = await fetch('https://hyku48m7d6.execute-api.us-east-1.amazonaws.com/prod/generate', {
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
          <div className="grid grid-cols-3 gap-2 text-sm text-gray-700">
            <div><span className="font-medium">년주:</span> {sajuData?.translatedData?.사주팔자?.년주 || 'N/A'}</div>
            <div><span className="font-medium">월주:</span> {sajuData?.translatedData?.사주팔자?.월주 || 'N/A'}</div>
            <div><span className="font-medium">일주:</span> {sajuData?.translatedData?.사주팔자?.일주 || 'N/A'}</div>
          </div>
        </div>

        <div className="bg-blue-50 p-4 rounded-lg">
          <h3 className="text-lg font-semibold text-blue-800 mb-2">오행 분석</h3>
          <div className="space-y-1">
            {sajuData?.wuxingAnalysis?.map((analysis, index) => (
              <p key={index} className="text-gray-700 text-sm">{analysis}</p>
            )) || <p className="text-gray-700">오행 분석 정보를 불러오는 중...</p>}
          </div>
        </div>

        <div className="bg-green-50 p-4 rounded-lg">
          <h3 className="text-lg font-semibold text-green-800 mb-2">기본 정보</h3>
          <div className="space-y-1 text-sm text-gray-700">
            <div><span className="font-medium">띠:</span> {sajuData?.translatedData?.띠 || 'N/A'}</div>
            <div><span className="font-medium">별자리:</span> {sajuData?.translatedData?.별자리 || 'N/A'}</div>
            <div><span className="font-medium">일주천간:</span> {sajuData?.translatedData?.일주천간 || 'N/A'}</div>
          </div>
        </div>

        {sajuData?.fallback_used && (
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