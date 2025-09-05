import { useState } from 'react'
import axios from 'axios'

function ChatInterface({ personalInfo, sajuData, cacheKey, onGoHome }) {
  const [messages, setMessages] = useState([
    {
      type: 'ai',
      content: `안녕하세요 ${personalInfo.name}님! 사주 분석을 바탕으로 궁금한 점을 물어보세요.`
    }
  ])
  const [inputMessage, setInputMessage] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!inputMessage.trim()) return

    const userMessage = { type: 'user', content: inputMessage }
    setMessages(prev => [...prev, userMessage])
    const currentQuestion = inputMessage
    setInputMessage('')
    setIsLoading(true)

    try {
      const requestData = {
        cache_key: cacheKey,
        question: currentQuestion
      }

      const response = await axios.post(
        'https://a2lqo7fctd.execute-api.us-east-1.amazonaws.com/prod/saju/consultation',
        requestData
      )

      const aiResponse = {
        type: 'ai',
        content: response.data.answer || response.data.message || '답변을 받지 못했습니다.'
      }
      setMessages(prev => [...prev, aiResponse])
    } catch (error) {
      console.error('상담 요청 실패:', error)
      const errorResponse = {
        type: 'ai',
        content: '죄송합니다. 상담 요청에 실패했습니다. 다시 시도해주세요.'
      }
      setMessages(prev => [...prev, errorResponse])
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="max-w-2xl mx-auto bg-white rounded-lg shadow-lg">
      <div className="p-4 border-b">
        <h2 className="text-xl font-semibold text-gray-800">AI 사주 상담</h2>
      </div>

      <div className="h-96 overflow-y-auto p-4 space-y-4">
        {messages.map((message, index) => (
          <div
            key={index}
            className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                message.type === 'user'
                  ? 'bg-purple-600 text-white'
                  : 'bg-gray-100 text-gray-800'
              }`}
            >
              {message.content}
            </div>
          </div>
        ))}
        
        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-gray-100 text-gray-800 px-4 py-2 rounded-lg">
              답변을 생성하고 있습니다...
            </div>
          </div>
        )}
      </div>

      <form onSubmit={handleSubmit} className="p-4 border-t">
        <div className="flex space-x-2 mb-3">
          <textarea
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            placeholder="궁금한 점을 물어보세요..."
            className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500 resize-none"
            rows="2"
            disabled={isLoading}
          />
          <button
            type="submit"
            disabled={isLoading || !inputMessage.trim()}
            className="bg-purple-600 text-white px-4 py-2 rounded-md hover:bg-purple-700 disabled:opacity-50 transition duration-200 self-end"
          >
            전송
          </button>
        </div>
        <button
          type="button"
          onClick={onGoHome}
          className="w-full bg-gray-500 text-white py-2 px-4 rounded-md hover:bg-gray-600 transition duration-200"
        >
          새로운 상담 시작하기
        </button>
      </form>
    </div>
  )
}

export default ChatInterface