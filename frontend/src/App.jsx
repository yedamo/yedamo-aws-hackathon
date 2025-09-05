import { useState } from 'react'
import PersonalInfoForm from './components/PersonalInfoForm'
import SajuResult from './components/SajuResult'
import ChatInterface from './components/ChatInterface'

function App() {
  const [step, setStep] = useState(1)
  const [personalInfo, setPersonalInfo] = useState(null)
  const [sajuData, setSajuData] = useState(null)

  const handlePersonalInfoSubmit = (info) => {
    setPersonalInfo(info)
    // 실제로는 백엔드 API 호출하여 사주 계산
    setSajuData({
      sajupalja: "갑자년 을축월 병인일 정묘시",
      daeun: "현재 대운: 무진 (2020-2029)",
      seun: "2024년 갑진년 운세"
    })
    setStep(2)
  }

  const handleChatStart = () => {
    setStep(3)
  }

  const handleGoHome = () => {
    setStep(1)
    setPersonalInfo(null)
    setSajuData(null)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-indigo-100">
      <div className="container mx-auto px-4 py-8">
        <header className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-800 mb-2">예다모</h1>
          <p className="text-lg text-gray-600">AI 사주 상담사</p>
        </header>

        {step === 1 && (
          <PersonalInfoForm onSubmit={handlePersonalInfoSubmit} />
        )}

        {step === 2 && (
          <SajuResult 
            personalInfo={personalInfo}
            sajuData={sajuData}
            onChatStart={handleChatStart}
          />
        )}

        {step === 3 && (
          <ChatInterface 
            personalInfo={personalInfo}
            sajuData={sajuData}
            onGoHome={handleGoHome}
          />
        )}
      </div>
    </div>
  )
}

export default App