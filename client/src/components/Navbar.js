import { AppBar, TextField, Toolbar } from "@material-ui/core";
import React, { useEffect, useState } from "react";
import { Redirect, useLocation } from "react-router-dom";

function Navbar() {
  const [symbol, setSymbol] = useState("");
  const [submitted, setSubmitted] = useState(false);
  const location = useLocation();

  useEffect(() => {
    console.log({ location });
    const path = location.pathname.split("/");
    if (path[path.length - 1] === symbol) {
      setSubmitted(false);
      setSymbol("");
    }
  }, [symbol, location]);

  const handleSubmit = (e) => {
    e.preventDefault();
    setSubmitted(true);
  };

  const renderRedirect = () => {
    if (submitted) {
      return <Redirect to={`/company/${symbol}`} />;
    }
  };

  return (
    <div>
      {renderRedirect()}
      <AppBar position="static" color="inherit" elevation={0}>
        <Toolbar>
          <form onSubmit={handleSubmit} style={{ width: "100%" }}>
            <TextField
              fullWidth
              value={symbol}
              onChange={(e) => setSymbol(e.target.value)}
              placeholder="Enter Symbol"
            />
          </form>
        </Toolbar>
      </AppBar>
    </div>
  );
}

export default Navbar;
