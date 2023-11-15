import "../App.css";
import { useState } from "react";
import SignatureCanvas from "react-signature-canvas";
import { useRef } from 'react';
import { API_URL } from "../config"


function Match() {
  const sigCanvas = useRef();
  const [penColor, setPenColor] = useState("black");
  const [imageURL, setImageURL] = useState(null);
  const [id, setId] = useState("");
  const [statusName, setStatusName] = useState("");
  const [statusProbability, setProbability] = useState("");
  const [statusPred, setPred] = useState("");
  const [loader, setLoader] = useState(false);
  const [errorText, setErrorText] = useState("");

  const create = async () => {
    setErrorText("");
    const URL = sigCanvas.current.getCanvas().toDataURL("image/png");
    let base64 = URL.substring(22);
    let reqBody = "id=" + id + "&base64=" + base64;
    if (id === '') {
      setErrorText(" ");
      setErrorText("Please enter ID");
    } else if (base64 === 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAAtJREFUGFdjYAACAAAFAAGq1chRAAAAAElFTkSuQmCC') {
      setErrorText("Canvas cannot be left blank, please draw your signature");
    } else {
      setLoader(true);
      try {
        await fetch(API_URL + `v1/model-inference/verify_sign/`, {
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
              if (result) {
                let res = result && JSON.parse(result);
                setStatusName(res.name)
                setProbability(res.probability)
                setPred(res.label_pred)
              }
            },

          )
      } catch (error) {
        console.log("fetch error", error)
        setLoader(false);
        setErrorText("Something went wrong. Please try again");
      }
    }
  }

  const createImage = () => {
    const URL = sigCanvas.current.getTrimmedCanvas().toDataURL("image/png");
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
    setErrorText("");
    setId(e.target.value);
  }

  const reset = () => {
    sigCanvas.current.clear();
    setLoader(false);
    setId("");
    setErrorText("");
    setStatusName("");
    setProbability("");
    setPred("");
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
          Enter your Id : <input onChange={onChangeValue} value={id} />
        </div>
        <br />
        <div className="col-sm-12 canva-submit-btn">
          <button type="button" className="btn btn-primary" onClick={create}>Submit</button>
        </div>
        {errorText &&
          <p className="errorText">{errorText}</p>
        }
        {statusName && <table className="statusTB">
          <tr>
            <th>Status :</th>
            <td className={statusPred === 1 ? 'text-green' : 'text-red'}>{statusPred === 1 ? 'Match ' + '(' + statusProbability + '%)' : 'Not Match ' + '(' + statusProbability + '%)'}</td>
          </tr>
          <tr>
            <th>Name :</th>
            <td>{statusName}</td>
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
export default Match;