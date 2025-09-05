function SajuResult({ personalInfo, sajuData, onChatStart }) {
  return (
    <div className="max-w-2xl mx-auto bg-white rounded-lg shadow-lg p-6">
      <h2 className="text-2xl font-semibold text-gray-800 mb-6 text-center">
        {personalInfo.name}님의 사주 분석 결과
      </h2>

      <div className="space-y-6">
        <div className="bg-purple-50 p-4 rounded-lg">
          <h3 className="text-lg font-semibold text-purple-800 mb-2">사주팔자</h3>
          <p className="text-gray-700">{sajuData.sajupalja}</p>
        </div>

        <div className="bg-blue-50 p-4 rounded-lg">
          <h3 className="text-lg font-semibold text-blue-800 mb-2">대운</h3>
          <p className="text-gray-700">{sajuData.daeun}</p>
        </div>

        <div className="bg-green-50 p-4 rounded-lg">
          <h3 className="text-lg font-semibold text-green-800 mb-2">세운</h3>
          <p className="text-gray-700">{sajuData.seun}</p>
        </div>

        <div className="bg-yellow-50 p-4 rounded-lg">
          <h3 className="text-lg font-semibold text-yellow-800 mb-2">기본 성향</h3>
          <p className="text-gray-700">
            차분하고 신중한 성격으로 계획적인 삶을 추구합니다. 
            인간관계에서 신뢰를 중시하며, 꾸준한 노력으로 목표를 달성하는 타입입니다.
          </p>
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