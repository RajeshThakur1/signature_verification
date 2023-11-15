import "./App.css";
import IndexName from './IndexName'
import Register from './components/Register'
import Match from "./components/Match";
import React, { useState } from 'react';


function App() {
  const [text, setText] = useState("register");
  const value = 'register';

  const handleScrren = (e) => {
    console.log("Inside app value is " + e);
    setText(e);
  }
  var screen;
  if (text == 'register') {
    screen = <Register></Register>;
  } else {
    screen = <Match></Match>;
  }


  return (
    <>
      <h1 className="title">Signature Verification</h1>
      <div className="container-fluid df">
        <div className="sideBar">
          <IndexName onSelect={handleScrren}></IndexName>
        </div>
        <div className="content">
          {screen}
        </div>
      </div>
    </>
  );
}
export default App;