import axios from 'axios'

const apiClient = axios.create({
  baseURL: 'https://w3qvjjo80g.execute-api.us-east-1.amazonaws.com/prod',
  headers: {
    'Content-Type': 'application/json'
  }
})

export default apiClient