import { useState } from 'react'
import axios from 'axios'
import PersonalInfoForm from './components/PersonalInfoForm'
import SajuResult from './components/SajuResult'
import ChatInterface from './components/ChatInterface'

function App() {
  const [step, setStep] = useState(1)
  const [personalInfo, setPersonalInfo] = useState(null)
  const [sajuData, setSajuData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const handlePersonalInfoSubmit = async (info) => {
    setLoading(true)
    setError(null)
    
    try {
      const response = await axios.post('http://localhost:3001/api/saju', {
        birthDate: info.birthDate,
        birthTime: info.birthTime,
        isLunar: info.calendarType === 'lunar',
        gender: info.gender,
        name: info.name
      })
      
      setPersonalInfo(info)
      setSajuData(response.data.data)
      setStep(2)
    } catch (error) {
      console.error('사주 분석 오류:', error)
      setError('사주 분석 중 오류가 발생했습니다. 다시 시도해주세요.')
    } finally {
      setLoading(false)
    }
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
          <div>
            {error && (
              <div className="max-w-md mx-auto mb-4 p-4 bg-red-100 border border-red-400 text-red-700 rounded">
                {error}
              </div>
            )}
            <PersonalInfoForm onSubmit={handlePersonalInfoSubmit} loading={loading} />
          </div>
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