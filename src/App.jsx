import { Routes, Route } from 'react-router-dom'
import Layout from './components/layout/Layout.jsx'
import Landing from './pages/Landing.jsx'
import Planner from './pages/Planner.jsx'
import Compare from './pages/Compare.jsx'
import NotFound from './pages/NotFound.jsx'

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route index element={<Landing />} />
        <Route path="planner" element={<Planner />} />
        <Route path="compare" element={<Compare />} />
        <Route path="*" element={<NotFound />} />
      </Route>
    </Routes>
  )
}
