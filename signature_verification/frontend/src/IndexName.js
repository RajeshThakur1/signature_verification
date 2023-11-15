import { useState } from "react";
import "./App.css";

function IndexName(props) {
  const [tabActive, setTabActive] = useState("register");
  const handleDialouge = (e) => {
    setTabActive(e)
    props.onSelect(e);
  }

  return (
    <>
      <button className={tabActive === "register" ? 'mb-10 button active' : 'mb-10 button'} onClick={() => handleDialouge("register")} >Register</button>
      <button className={tabActive === "match" ? 'mb-10 button active' : 'mb-10 button'} onClick={() => handleDialouge("match")}>Match</button>
    </>
  );
}

export default IndexName;
