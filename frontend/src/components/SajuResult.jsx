function SajuResult({ personalInfo, sajuData, onChatStart }) {
  const { translatedData, wuxingAnalysis } = sajuData;
  
  return (
    <div className="max-w-4xl mx-auto bg-white rounded-lg shadow-lg p-6">
      <h2 className="text-2xl font-semibold text-gray-800 mb-6 text-center">
        {personalInfo.name}님의 사주 분석 결과
      </h2>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* 사주팔자 */}
        <div className="bg-purple-50 p-4 rounded-lg">
          <h3 className="text-lg font-semibold text-purple-800 mb-3">사주팔자</h3>
          <div className="space-y-2 text-sm">
            <div><span className="font-medium">년주:</span> {translatedData.사주팔자.년주}</div>
            <div><span className="font-medium">월주:</span> {translatedData.사주팔자.월주}</div>
            <div><span className="font-medium">일주:</span> {translatedData.사주팔자.일주}</div>
            <div><span className="font-medium">시주:</span> {translatedData.사주팔자.시주}</div>
          </div>
        </div>

        {/* 기본 정보 */}
        <div className="bg-blue-50 p-4 rounded-lg">
          <h3 className="text-lg font-semibold text-blue-800 mb-3">기본 정보</h3>
          <div className="space-y-2 text-sm">
            <div><span className="font-medium">띠:</span> {translatedData.띠}</div>
            <div><span className="font-medium">별자리:</span> {translatedData.별자리}</div>
            <div><span className="font-medium">일주천간:</span> {translatedData.일주천간}</div>
          </div>
        </div>

        {/* 오행 분석 */}
        <div className="bg-green-50 p-4 rounded-lg">
          <h3 className="text-lg font-semibold text-green-800 mb-3">오행 분석</h3>
          <div className="space-y-1 text-sm">
            {wuxingAnalysis.map((analysis, index) => (
              <div key={index}>{analysis}</div>
            ))}
          </div>
        </div>

        {/* 음력 정보 */}
        <div className="bg-yellow-50 p-4 rounded-lg">
          <h3 className="text-lg font-semibold text-yellow-800 mb-3">음력 정보</h3>
          <div className="space-y-2 text-sm">
            <div><span className="font-medium">음력:</span> {translatedData.음력정보.음력년}년 {translatedData.음력정보.월이름} {translatedData.음력정보.음력일}일</div>
            <div><span className="font-medium">윤달:</span> {translatedData.음력정보.윤달여부}</div>
          </div>
        </div>
      </div>

      {/* MCP 원본 데이터 */}
      {sajuData.rawData && (
        <div className="mt-6 bg-gray-50 p-4 rounded-lg">
          <h3 className="text-lg font-semibold text-gray-800 mb-2">MCP 원본 데이터</h3>
          <pre className="text-xs text-gray-600 overflow-auto max-h-40">
            {JSON.stringify(sajuData.rawData, null, 2)}
          </pre>
        </div>
      )}

      <div className="mt-8 text-center space-x-4">
        <button
          onClick={onChatStart}
          className="bg-purple-600 text-white py-3 px-6 rounded-md hover:bg-purple-700 transition duration-200"
        >
          AI 상담사와 대화하기
        </button>
        <button
          onClick={() => window.location.reload()}
          className="bg-gray-600 text-white py-3 px-6 rounded-md hover:bg-gray-700 transition duration-200"
        >
          다시 분석하기
        </button>
      </div>
    </div>
  )
}

export default SajuResult