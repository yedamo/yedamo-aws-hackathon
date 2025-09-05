function SajuResult({ personalInfo, sajuData, onChatStart }) {
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