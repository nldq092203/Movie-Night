import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Login from './components/Login';
import Register from './components/Register';
import MovieDetails from './components/MovieDetails';
import MovieSearch from './components/MovieSearch';
import HomePage from './components/HomePage';
import MovieNightDetails from './components/MovieNightDetails';


function App() {
  return (

      <Router>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/" element={<HomePage />} />
          <Route path="/search" element={<MovieSearch />} />
          <Route path="/movies/:id" element={<MovieDetails />} />
          <Route path="/movie-nights/:id" element={<MovieNightDetails />} />
        </Routes>
      </Router>

  );
}

export default App;

