import "../App.css";
import { useState } from "react";
import SignatureCanvas from "react-signature-canvas";
import { useRef } from 'react';
import { API_URL } from "../config"


function Register() {
  const sigCanvas = useRef();
  const [penColor, setPenColor] = useState("black");
  const [imageURL, setImageURL] = useState(null);
  const [name, setName] = useState("");
  const [status, setStatus] = useState("");
  const [isName, setIsName] = useState("");
  const [iD, setID] = useState("");
  const [loader, setLoader] = useState(false);
  const [errorText, setErrorText] = useState("");



  const create = async () => {
    setErrorText("");
    //calling API 
    const URL = sigCanvas.current.getCanvas().toDataURL("image/png");
    var base64 = URL.substring(22);
    if (name === '') {
      setErrorText("Please enter name");
    } else if (base64 === 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAAtJREFUGFdjYAACAAAFAAGq1chRAAAAAElFTkSuQmCC') {
      setErrorText("Canvas cannot be left blank, please draw your signature");
    } else {
      setLoader(true)
      let reqBody = "base_b4=" + base64 + "&name=" + name;
      try {
        await fetch(API_URL + `v1/model-inference/register_signature/`, {
          method: 'POST',
          headers: new Headers({
            'accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded'
          }),
          body: reqBody
        })
          .then((res) => res.text())
          .then(
            (result) => {
              setLoader(false)
              let res = JSON.parse(result);
              let getResult = res?.data
              setStatus(getResult.Status);
              setIsName(getResult.Name);
              setID(getResult.ID);
            },
          )
      }
      catch (error) {
        console.log("fetch error", error);
        setLoader(false);
        setErrorText("Something went wrong. Please try again");
      }
    }
  }

  const createImage = () => {
    const URL = sigCanvas.current.getCanvas().toDataURL("image/png");
    console.log("Url is " + URL)
    setImageURL(URL);
  }

  const download = () => {
    const dlink = document.createElement("a");
    dlink.setAttribute("href", imageURL);
    dlink.setAttribute("download", "signature.png");
    dlink.click();
  };

  const onChangeValue = (e) => {
    console.log(e.target.value.length)
    setErrorText("");
    setName(e.target.value);
  }

  const reset = () => {
    sigCanvas.current.clear();
    setName("")
    setStatus("")
    setIsName("")
    setID("")
    setLoader(false)
    setErrorText("")
  }

  return (
    <div className="signute-area">
      <div className="sigPad__penColors">
      </div>
      <div className="sigPadContainer">
        <p className="signute">Signature here</p>
        <SignatureCanvas clearOnResize={false} penColor={penColor} canvasProps={{ className: "sigCanvas" }} ref={sigCanvas} />
        <div className="clear-btn">
          <button onClick={() => reset()}>Clear</button>
        </div>
      </div>
      <div className="canva-ready">
        <div className="c-input">
          Enter your name : <input onChange={(e) => { onChangeValue(e) }} value={name} />
        </div>
        <br />
        <div className="col-sm-12 canva-submit-btn">
          <button type="button" className="btn btn-primary" onClick={create}>Submit</button>
        </div>
        {errorText &&
          <p className="errorText">{errorText}</p>
        }
        {status && <table className="statusTB">
          <tr>
            <th>Status :</th>
            <td className="text-green">{status}</td>
          </tr>
          <tr>
            <th>Name :</th>
            <td>{isName}</td>
          </tr>
          <tr>
            <th>ID :</th>
            <td>{iD}</td>
          </tr>
        </table>}
      </div>
      {
        loader && (
          <div className="loader-container" id="loader">
            <div className="loader"></div>
          </div>
        )
      }
    </div>
  );
}
export default Register;