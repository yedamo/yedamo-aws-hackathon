import { useState } from 'react'
import axios from 'axios'
import PersonalInfoForm from './components/PersonalInfoForm'
import SajuResult from './components/SajuResult'
import ChatInterface from './components/ChatInterface'

function App() {
  const [step, setStep] = useState(1)
  const [personalInfo, setPersonalInfo] = useState(null)
  const [sajuData, setSajuData] = useState(null)
  const [cacheKey, setCacheKey] = useState(null)
  const [isLoading, setIsLoading] = useState(false)

  const handlePersonalInfoSubmit = async (info) => {
    setIsLoading(true)
    try {
      const birthDate = new Date(info.birthDate)
      
      const timezoneMap = {
        korea: 'Asia/Seoul',
        usa_east: 'America/New_York',
        usa_west: 'America/Los_Angeles',
        china: 'Asia/Shanghai',
        japan: 'Asia/Tokyo'
      }
      
      const requestData = {
        name: info.name,
        birth_info: {
          year: birthDate.getFullYear(),
          month: birthDate.getMonth() + 1,
          day: birthDate.getDate(),
          hour: parseInt(info.birthHour),
          gender: info.gender,
          timezone: timezoneMap[info.timezone]
        }
      }

      const response = await axios.post(
        'https://a2lqo7fctd.execute-api.us-east-1.amazonaws.com/prod/saju/basic',
        requestData
      )

      setPersonalInfo(info)
      setSajuData(response.data.saju_analysis)
      setCacheKey(response.data.cache_key)
      setStep(2)
    } catch (error) {
      console.error('사주 분석 요청 실패:', error)
      alert('사주 분석 요청에 실패했습니다. 다시 시도해주세요.')
    } finally {
      setIsLoading(false)
    }
  }

  const handleChatStart = () => {
    setStep(3)
  }

  const handleGoHome = () => {
    setStep(1)
    setPersonalInfo(null)
    setSajuData(null)
    setCacheKey(null)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-indigo-100">
      <div className="container mx-auto px-4 py-8">
        <header className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-800 mb-2">예다모</h1>
          <p className="text-lg text-gray-600">AI 사주 상담사</p>
        </header>

        {step === 1 && (
          <PersonalInfoForm onSubmit={handlePersonalInfoSubmit} isLoading={isLoading} />
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
            cacheKey={cacheKey}
            onGoHome={handleGoHome}
          />
        )}
      </div>
    </div>
  )
}

export default App