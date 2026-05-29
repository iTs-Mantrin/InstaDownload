import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout.tsx'
import Home from './pages/Home.tsx'
import YouTubePage from './pages/YouTube.tsx'
import InstagramPage from './pages/Instagram.tsx'

function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/youtube" element={<YouTubePage />} />
        <Route path="/instagram" element={<InstagramPage />} />
      </Routes>
    </Layout>
  )
}

export default App
