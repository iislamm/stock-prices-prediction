import { Container } from "@material-ui/core";
import {
  BrowserRouter as Router,
  Switch,
  Route,
  Redirect,
} from "react-router-dom";
import CompanyPage from "./components/CompanyPage";
import Navbar from "./components/Navbar";
import "./globalStyles.css";

function App() {
  return (
    <div className="App">
      <Container maxWidth="md">
        <Router>
          <Navbar />
          <Switch>
            <Route exact path="/">
              <Redirect to="/company/nflx" />
            </Route>
            <Route exact path="/company/:symbol">
              <CompanyPage />
            </Route>
          </Switch>
        </Router>
      </Container>
    </div>
  );
}

export default App;
