import { BrowserRouter as Router, Switch, Route } from 'react-router-dom'
import CompanyPage from './components/CompanyPage';

function App() {
  return (
    <div className="App">
      <Router>
            <Switch>
              <Route exact path='/company/:symbol'>
                  <CompanyPage />
              </Route>
            </Switch>
        </Router>
    </div>
  );
}

export default App;
