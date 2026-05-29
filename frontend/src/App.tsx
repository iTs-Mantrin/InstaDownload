import { Routes, Route } from 'react-router-dom'
import Navbar from './components/Navbar.tsx'
import Layout from './components/Layout.tsx'
import Home from './pages/Home.tsx'
import YouTubePage from './pages/YouTube.tsx'
import YouTubeMp3 from './pages/YouTubeMp3.tsx'
import InstagramPage from './pages/Instagram.tsx'
import InstagramStory from './pages/InstagramStory.tsx'
import Contact from './pages/Contact.tsx'
import Privacy from './pages/Privacy.tsx'
import Terms from './pages/Terms.tsx'
import Dmca from './pages/Dmca.tsx'

function App() {
  return (
    <>
      <Navbar />
      <Layout>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/youtube" element={<YouTubePage />} />
          <Route path="/youtube-mp3" element={<YouTubeMp3 />} />
          <Route path="/instagram" element={<InstagramPage />} />
          <Route path="/instagram-story" element={<InstagramStory />} />
          <Route path="/contact" element={<Contact />} />
          <Route path="/privacy" element={<Privacy />} />
          <Route path="/terms" element={<Terms />} />
          <Route path="/dmca" element={<Dmca />} />
        </Routes>
      </Layout>
    </>
  )
}

export default App
