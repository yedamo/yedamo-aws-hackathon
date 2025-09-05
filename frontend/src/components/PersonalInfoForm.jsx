import { useState } from 'react'

function PersonalInfoForm({ onSubmit, loading }) {
  const [formData, setFormData] = useState({
    name: '',
    birthDate: '',
    birthTime: '',
    gender: 'male',
    calendarType: 'solar'
  })

  const handleSubmit = (e) => {
    e.preventDefault()
    onSubmit(formData)
  }

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    })
  }

  return (
    <div className="max-w-md mx-auto bg-white rounded-lg shadow-lg p-6">
      <h2 className="text-2xl font-semibold text-gray-800 mb-6 text-center">
        개인정보 입력
      </h2>
      
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            이름
          </label>
          <input
            type="text"
            name="name"
            value={formData.name}
            onChange={handleChange}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            생년월일
          </label>
          <input
            type="date"
            name="birthDate"
            value={formData.birthDate}
            onChange={handleChange}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            출생시간
          </label>
          <input
            type="time"
            name="birthTime"
            value={formData.birthTime}
            onChange={handleChange}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            성별
          </label>
          <select
            name="gender"
            value={formData.gender}
            onChange={handleChange}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
          >
            <option value="male">남성</option>
            <option value="female">여성</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            달력 구분
          </label>
          <select
            name="calendarType"
            value={formData.calendarType}
            onChange={handleChange}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
          >
            <option value="solar">양력</option>
            <option value="lunar">음력</option>
          </select>
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full bg-purple-600 text-white py-2 px-4 rounded-md hover:bg-purple-700 transition duration-200 disabled:bg-gray-400 disabled:cursor-not-allowed"
        >
          {loading ? '분석 중...' : '사주 분석하기'}
        </button>
      </form>
    </div>
  )
}

export default PersonalInfoForm